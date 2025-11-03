from flask import jsonify, request
from config.database import SessionLocal
from models.order_model import Order
from models.menu_model import Menu
from models.order_item_model import OrderItem
from sqlalchemy.orm import Session
from datetime import datetime

# --- GET: Semua order (opsional filter per customer) ---
def get_all_order():
    db = SessionLocal()
    try:
        orders = db.query(Order).all()
        results = []
        for order in orders:
            # ambil semua order items yang terkait order_id ini
            order_items = (
                db.query(OrderItem, Menu)
                .join(Menu, OrderItem.menu_id == Menu.id_menu)
                .filter(OrderItem.order_id == order.order_id)
                .all()
            )

            # buat daftar item
            items = []
            for oi, menu in order_items:
                items.append({
                    "menu_id": menu.id_menu,
                    "menu_name": menu.name,
                    "price": oi.price,
                    "quantity": oi.quantity,
                    "subtotal": oi.subtotal,
                })

            # Format tanggal dengan konsisten
            formatted_date = order.order_date.strftime("%Y-%m-%d %H:%M:%S") if order.order_date else None

            # bentuk struktur JSON yang terstandarisasi
            results.append({
                "order_id": order.order_id,
                "customer_id": order.customer_id,
                "total_price": float(order.total_price),
                "payment_method": order.payment_method,
                "status": order.status,
                "order_date": formatted_date,
                "items": items
            })

        return jsonify(results)
    finally:
        db.close()

# --- GET: Order berdasarkan ID ---
def get_order_by_id(order_id):
    db: Session = SessionLocal()
    try:
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            return jsonify({"message": "Order tidak ditemukan"}), 404

        order_items = (
            db.query(OrderItem, Menu)
            .join(Menu, OrderItem.menu_id == Menu.id_menu)
            .filter(OrderItem.order_id == order_id)
            .all()
        )

        items = []
        for oi, menu in order_items:
            items.append({
                "menu_id": menu.id_menu,
                "menu_name": menu.name,
                "price": float(oi.price),
                "quantity": int(oi.quantity),
                "subtotal": float(oi.subtotal)
            })

        formatted_date = order.order_date.strftime("%Y-%m-%d %H:%M:%S") if order.order_date else None

        return jsonify({
            "order_id": order.order_id,
            "customer_id": order.customer_id,
            "total_price": float(order.total_price),
            "payment_method": order.payment_method,
            "status": order.status,
            "order_date": formatted_date,
            "items": items
        }), 200
    except Exception as e:
        return jsonify({"message": "Terjadi kesalahan saat mengambil order", "error": str(e)}), 500
    finally:
        db.close()


# --- POST: Buat order dari daftar item (items) ---
def create_order():
    if not request.is_json:
        return jsonify({"message": "Gunakan format JSON"}), 400

    body = request.json
    required_fields = ["customer_id", "payment_method"]

    if not all(field in body for field in required_fields):
        return jsonify({"message": "Data tidak lengkap"}), 400

    try:
        customer_id = int(body["customer_id"])
    except ValueError:
        return jsonify({"message": "customer_id harus angka"}), 400

    db: Session = SessionLocal()

    try:
        # Expect items list in body: [{"menu_id": <int>, "quantity": <int>}, ...]
        if "items" not in body or not isinstance(body["items"], list) or not body["items"]:
            return jsonify({"message": "Field 'items' harus berisi daftar item"}), 400

        items_in = body["items"]

        total_price = 0.0
        order_items_to_create = []

        for it in items_in:
            if "menu_id" not in it or "quantity" not in it:
                return jsonify({"message": "Setiap item harus memiliki menu_id dan quantity"}), 400
            try:
                qty = int(it["quantity"])
            except Exception:
                return jsonify({"message": "quantity harus angka"}), 400
            if qty <= 0:
                return jsonify({"message": "quantity harus > 0"}), 400

            menu = db.query(Menu).filter(Menu.id_menu == int(it["menu_id"])).first()
            if not menu:
                return jsonify({"message": f"Menu dengan id {it['menu_id']} tidak ditemukan"}), 400

            price = float(menu.price)
            subtotal = price * qty
            total_price += subtotal
            order_items_to_create.append({"menu_id": menu.id_menu, "quantity": qty, "price": price, "subtotal": subtotal})

        # Buat order baru
        new_order = Order(
            customer_id=customer_id,
            total_price=total_price,
            payment_method=body["payment_method"],
            # Default status for customer-created orders set to 'diantar' per request
            status="diantar",
            order_date=datetime.utcnow()
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        # Buat OrderItem rows
        items_response = []
        for oi in order_items_to_create:
            new_oi = OrderItem(order_id=new_order.order_id, menu_id=oi["menu_id"], quantity=oi["quantity"], price=oi["price"], subtotal=oi["subtotal"])
            db.add(new_oi)
            items_response.append({"menu_id": oi["menu_id"], "quantity": oi["quantity"], "price": oi["price"], "subtotal": oi["subtotal"]})

        db.commit()

        return jsonify({
            "order_id": new_order.order_id,
            "customer_id": new_order.customer_id,
            "total_price": float(new_order.total_price),
            "payment_method": new_order.payment_method,
            "status": new_order.status,
            "order_date": new_order.order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "items": [{
                "menu_id": item["menu_id"],
                "quantity": int(item["quantity"]),
                "price": float(item["price"]),
                "subtotal": float(item["subtotal"])
            } for item in items_response],
            "message": "Order berhasil dibuat"
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({"message": "Gagal membuat order", "error": str(e)}), 500
    finally:
        db.close()


# --- PUT: Customer ubah metode pembayaran ---
def update_order(order_id):
    if not request.is_json:
        return jsonify({"message": "Gunakan format JSON"}), 400

    body = request.json
    db: Session = SessionLocal()
    try:
        order_item = db.query(Order).filter(Order.order_id == order_id).first()
        if not order_item:
            return jsonify({"message": "Order tidak ditemukan"}), 404

        if "payment_method" not in body:
            return jsonify({"message": "Field 'payment_method' harus ada"}), 400

        order_item.payment_method = body["payment_method"]

        db.commit()
        db.refresh(order_item)
        return jsonify({
            "message": "Metode pembayaran berhasil diperbarui",
            "order_id": order_item.order_id,
            "payment_method": order_item.payment_method
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({"message": "Gagal memperbarui metode pembayaran", "error": str(e)}), 500
    finally:
        db.close()



# --- DELETE: Hapus order ---
def delete_order(order_id):
    db: Session = SessionLocal()
    try:
        order_item = db.query(Order).filter(Order.order_id == order_id).first()
        if not order_item:
            return jsonify({"message": "Order tidak ditemukan"}), 404

        # delete order -> OrderItem rows will be removed by cascade
        db.delete(order_item)
        db.commit()
        return jsonify({"message": "Order berhasil dihapus"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"message": "Gagal menghapus order", "error": str(e)}), 500
    finally:
        db.close()
