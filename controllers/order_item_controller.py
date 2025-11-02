from flask import jsonify, request
from config.database import SessionLocal
from models.order_item_model import OrderItem
from models.menu_model import Menu
from models.order_model import Order
from sqlalchemy.orm import Session


def get_items_by_order(order_id):
    """Return a list of order items for a given order_id."""
    db: Session = SessionLocal()
    try:
        rows = (
            db.query(OrderItem, Menu)
            .join(Menu, OrderItem.menu_id == Menu.id_menu)
            .filter(OrderItem.order_id == order_id)
            .all()
        )

        items = []
        for oi, menu in rows:
            items.append({
                "id": oi.order_item_id,
                "menu_id": menu.id_menu,
                "menu_name": menu.name,
                "price": oi.price,
                "quantity": oi.quantity,
                "subtotal": oi.subtotal,
            })

        return jsonify(items)
    finally:
        db.close()


def add_item(order_id):
    """Add an item to an order. Expects JSON {"menu_id":int, "quantity":int}."""
    if not request.is_json:
        return jsonify({"message": "Gunakan format JSON"}), 400

    body = request.json
    if "menu_id" not in body or "quantity" not in body:
        return jsonify({"message": "menu_id dan quantity diperlukan"}), 400

    try:
        menu_id = int(body["menu_id"])
        quantity = int(body["quantity"])
    except Exception:
        return jsonify({"message": "menu_id dan quantity harus angka"}), 400

    if quantity <= 0:
        return jsonify({"message": "quantity harus > 0"}), 400

    db: Session = SessionLocal()
    try:
        menu = db.query(Menu).filter(Menu.id_menu == menu_id).first()
        if not menu:
            return jsonify({"message": "Menu tidak ditemukan"}), 404

        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            return jsonify({"message": "Order tidak ditemukan"}), 404
            
        # Check order status
        if order.status != "pending":
            return jsonify({
                "message": "Tidak dapat menambah item karena status order sudah " + order.status
            }), 400

        price = float(menu.price)
        subtotal = price * quantity

        oi = OrderItem(order_id=order_id, menu_id=menu.id_menu, quantity=quantity, price=price, subtotal=subtotal)
        db.add(oi)

        # update order total
        order.total_price = (order.total_price or 0) + subtotal
        db.commit()
        db.refresh(oi)

        return jsonify({
            "id": oi.order_item_id,
            "order_id": oi.order_id,
            "menu_id": oi.menu_id,
            "quantity": oi.quantity,
            "price": oi.price,
            "subtotal": oi.subtotal,
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({"message": "Gagal menambah item", "error": str(e)}), 500
    finally:
        db.close()


def update_item(order_item_id):
    """Update quantity of an order item. Expects JSON {"quantity":int}."""
    if not request.is_json:
        return jsonify({"message": "Gunakan format JSON"}), 400

    body = request.json
    if "quantity" not in body:
        return jsonify({"message": "Field 'quantity' diperlukan"}), 400

    try:
        quantity = int(body["quantity"])
    except Exception:
        return jsonify({"message": "quantity harus angka"}), 400

    if quantity <= 0:
        return jsonify({"message": "quantity harus > 0"}), 400

    db: Session = SessionLocal()
    try:
        # Get order item and its associated order
        oi = db.query(OrderItem).filter(OrderItem.order_item_id == order_item_id).first()
        if not oi:
            return jsonify({"message": "OrderItem tidak ditemukan"}), 404
            
        # Check order status
        order = db.query(Order).filter(Order.order_id == oi.order_id).first()
        if order.status != "pending":
            return jsonify({
                "message": "Order tidak dapat diubah karena status sudah " + order.status
            }), 400

        order = db.query(Order).filter(Order.order_id == oi.order_id).first()
        if not order:
            return jsonify({"message": "Order tidak ditemukan"}), 404

        # recompute totals
        old_sub = oi.subtotal
        oi.quantity = quantity
        oi.subtotal = oi.price * quantity

        order.total_price = (order.total_price or 0) - old_sub + oi.subtotal

        db.commit()
        db.refresh(oi)

        return jsonify({
            "id": oi.order_item_id,
            "order_id": oi.order_id,
            "menu_id": oi.menu_id,
            "quantity": oi.quantity,
            "price": oi.price,
            "subtotal": oi.subtotal,
        })
    except Exception as e:
        db.rollback()
        return jsonify({"message": "Gagal memperbarui item", "error": str(e)}), 500
    finally:
        db.close()


def delete_item(order_item_id):
    db: Session = SessionLocal()
    try:
        oi = db.query(OrderItem).filter(OrderItem.order_item_id == order_item_id).first()
        if not oi:
            return jsonify({"message": "OrderItem tidak ditemukan"}), 404
            
        # Check order status
        order = db.query(Order).filter(Order.order_id == oi.order_id).first()
        if order.status != "pending":
            return jsonify({
                "message": "Item tidak dapat dihapus karena status order sudah " + order.status
            }), 400

        order = db.query(Order).filter(Order.order_id == oi.order_id).first()
        if order:
            order.total_price = (order.total_price or 0) - oi.subtotal

        db.delete(oi)
        db.commit()
        return jsonify({"message": "OrderItem dihapus"})
    except Exception as e:
        db.rollback()
        return jsonify({"message": "Gagal menghapus item", "error": str(e)}), 500
    finally:
        db.close()
