from flask import jsonify, request
from config.database import SessionLocal
from models.customer_model import Customer
from models.order_model import Order
from models.menu_model import Menu
from models.order_item_model import OrderItem
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


# --- GET: Semua customer + order aktif ---
def get_all_customers():
    db: Session = SessionLocal()
    try:
        customers = db.query(Customer).all()
        result = []

        for c in customers:
            # Ambil semua order milik customer ini
            orders = db.query(Order).filter(Order.customer_id == c.customer_id).all()
            order_list = []

            for order in orders:
                # Ambil detail items untuk setiap order
                order_items = (
                    db.query(OrderItem, Menu)
                    .join(Menu, OrderItem.menu_id == Menu.id_menu)
                    .filter(OrderItem.order_id == order.order_id)
                    .all()
                )

                # Format items dengan detail menu
                items = []
                for oi, menu in order_items:
                    items.append({
                        "menu_id": menu.id_menu,
                        "menu_name": menu.name,
                        "quantity": oi.quantity,
                        "price": float(oi.price),
                        "subtotal": float(oi.subtotal)
                    })

                order_list.append({
                    "order_id": order.order_id,
                    "total_price": float(order.total_price),
                    "payment_method": order.payment_method,
                    "status": order.status,
                    "order_date": order.order_date.strftime("%Y-%m-%d %H:%M:%S") if order.order_date else None,
                    "items": items
                })

            result.append({
                "customer_id": c.customer_id,
                "name_customer": c.name_customer,
                "email": c.email,
                "password": c.password,
                "phone": c.phone,
                "address": c.address,
                "orders": order_list,
            })
        
        return jsonify(result)
    finally:
        db.close()
        
# --- POST: Login customer ---
def login_customer():
    db = SessionLocal()
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email dan password harus diisi"}), 400

    customer = db.query(Customer).filter(Customer.email == email).first()

    if not customer:
        return jsonify({"message": "Email tidak ditemukan"}), 404

    # Jika password disimpan dalam bentuk hash:
    # if not check_password_hash(customer.password, password):
    # Jika masih plain-text:
    if customer.password != password:
        return jsonify({"message": "Password salah"}), 401

    return jsonify({
        "message": "Login berhasil",
        "customer": {
            "customer_id": customer.customer_id,
            "name_customer": customer.name_customer,
            "email": customer.email,
            "address": customer.address,
            "phone": customer.phone
        }
    }), 200

# --- GET: Customer berdasarkan ID ---
def get_customer_by_id(customer_id):
    db: Session = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            return jsonify({"message": "Customer tidak ditemukan"}), 404

        orders = db.query(Order).filter(Order.customer_id == customer_id).all()
        order_list = []
        
        for order in orders:
            # Ambil detail items untuk setiap order
            order_items = (
                db.query(OrderItem, Menu)
                .join(Menu, OrderItem.menu_id == Menu.id_menu)
                .filter(OrderItem.order_id == order.order_id)
                .all()
            )

            # Format items dengan detail menu
            items = []
            for oi, menu in order_items:
                items.append({
                    "menu_id": menu.id_menu,
                    "menu_name": menu.name,
                    "quantity": oi.quantity,
                    "price": float(oi.price),
                    "subtotal": float(oi.subtotal)
                })

            order_list.append({
                "order_id": order.order_id,
                "total_price": float(order.total_price),
                "payment_method": order.payment_method,
                "status": order.status,
                "order_date": order.order_date.strftime("%Y-%m-%d %H:%M:%S") if order.order_date else None,
                "items": items
            })

        return jsonify({
            "customer_id": customer.customer_id,
            "name_customer": customer.name_customer,
            "email": customer.email,
            "password": customer.password,
            "phone": customer.phone,
            "address": customer.address,
            "orders": order_list,
        })
    finally:
        db.close()



# --- POST: Tambah customer baru ---
def add_customer():
    if not request.is_json:
        return jsonify({"message": "Gunakan format JSON"}), 400

    body = request.json
    required_fields = ["name_customer", "email", "password", "address", "phone"]

    if not all(field in body and body[field] for field in required_fields):
        return jsonify({"message": "Data tidak lengkap"}), 400

    db: Session = SessionLocal()
    try:
        # Cek duplikasi email
        if db.query(Customer).filter(Customer.email.ilike(body["email"])).first():
            return jsonify({"message": "Email sudah terdaftar"}), 400

        new_customer = Customer(
            name_customer=body["name_customer"],
            email=body["email"],
            password=body["password"],
            phone=body["phone"],
            address=body["address"],
        )
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)

        return jsonify({
            "message": "Customer berhasil ditambahkan",
            "customer_id": new_customer.customer_id,
        }), 201

    except IntegrityError as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            "message": "Terjadi kesalahan database",
            "error": str(e.orig)
        }), 500
    finally:
        db.close()


# --- PUT: Update data customer ---
def update_customer(customer_id):
    if not request.is_json:
        return jsonify({"message": "Gunakan format JSON"}), 400

    body = request.json
    db: Session = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()

        if not customer:
            return jsonify({"message": "Customer tidak ditemukan"}), 404

        # Cek duplikasi email (kalau diubah)
        if "email" in body and body["email"].lower() != customer.email.lower():
            if db.query(Customer).filter(Customer.email.ilike(body["email"])).first():
                return jsonify({"message": "Email sudah terdaftar"}), 400

        # Update data customer
        customer.name_customer = body.get("name_customer", customer.name_customer)
        customer.email = body.get("email", customer.email)
        customer.password = body.get("password", customer.password)
        customer.phone = body.get("phone", customer.phone)
        customer.address = body.get("address", customer.address)

        db.commit()
        db.refresh(customer)

        return jsonify({
            "message": "Customer berhasil diperbarui",
            "customer_id": customer.customer_id
        })
    except IntegrityError as e:
        db.rollback()
        return jsonify({
            "message": "Terjadi kesalahan database",
            "error": str(e.orig)
        }), 500
    finally:
        db.close()


# --- DELETE: Hapus customer ---
def delete_customer(customer_id):
    db: Session = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()

        if not customer:
            return jsonify({"message": "Customer tidak ditemukan"}), 404

        db.delete(customer)
        db.commit()

        return jsonify({"message": "Customer berhasil dihapus"})
    finally:
        db.close()
