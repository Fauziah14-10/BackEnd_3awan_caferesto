from flask import Blueprint, jsonify

# Import controllers
from controllers.customer_controller import (
    get_all_customers,
    get_customer_by_id,
    add_customer,
    update_customer,
    delete_customer,
)
from controllers.order_controller import (
    get_all_order,
    get_order_by_id,
    create_order,
    update_order,
    delete_order,
)
from controllers.menu_controller import (
    get_all_menus,
    get_menu_by_id,
    create_menu,
    update_menu,
    delete_menu,
)
from controllers.order_item_controller import (
    get_items_by_order,
    add_item,
    update_item,
    delete_item,
)


# Definisikan blueprint
web = Blueprint("web", __name__)


@web.route("/")
def index():
    return jsonify({"message": "API berjalan", "services": ["customers", "orders", "menus"]})


# --- CUSTOMER endpoints ---
web.route("/customers", methods=["GET"])(get_all_customers)
web.route("/customers/<int:customer_id>", methods=["GET"])(get_customer_by_id)
web.route("/customers", methods=["POST"])(add_customer)
web.route("/customers/<int:customer_id>", methods=["PUT"])(update_customer)
web.route("/customers/<int:customer_id>", methods=["DELETE"])(delete_customer)


# --- ORDER endpoints ---
web.route("/orders", methods=["GET"])(get_all_order)
web.route("/orders/<int:order_id>", methods=["GET"])(get_order_by_id)
web.route("/orders", methods=["POST"])(create_order)
web.route("/orders/<int:order_id>", methods=["PUT"])(update_order)
web.route("/orders/<int:order_id>", methods=["DELETE"])(delete_order)


# --- MENU endpoints ---
web.route("/menus", methods=["GET"])(get_all_menus)
web.route("/menus/<int:menu_id>", methods=["GET"])(get_menu_by_id)
web.route("/menus", methods=["POST"])(create_menu)
web.route("/menus/<int:menu_id>", methods=["PUT"])(update_menu)
web.route("/menus/<int:menu_id>", methods=["DELETE"])(delete_menu)

# legacy/alias routes using singular /menu (some clients may call this)
# (removed singular /menu aliases to keep API RESTful; use /menus)


# --- ORDER-ITEM endpoints ---
# list items for an order
web.route("/orders/<int:order_id>/items", methods=["GET"])(get_items_by_order)
# add an item to an order
web.route("/orders/<int:order_id>/items", methods=["POST"])(add_item)
# update an order-item by its id
web.route("/order-items/<int:order_item_id>", methods=["PUT"])(update_item)
# delete an order-item by its id
web.route("/order-items/<int:order_item_id>", methods=["DELETE"])(delete_item)
