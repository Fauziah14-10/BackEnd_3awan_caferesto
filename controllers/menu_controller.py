from typing import Optional
from flask import jsonify, request
from config import database
from models.menu_model import Menu


def _serialize_menu(item: Menu) -> dict:
	return {
		"id_menu": item.id_menu,
		"name": item.name,
		"price": item.price,
		"category": item.category,
		"image_url": item.image_url,
	}


def get_all_menus():
	"""Flask view: return JSON list of menus."""
	db = database.SessionLocal()
	try:
		rows = db.query(Menu).all()
		return jsonify([_serialize_menu(r) for r in rows])
	finally:
		db.close()


def get_menu_by_id(menu_id: int):
	db = database.SessionLocal()
	try:
		item = db.query(Menu).filter(Menu.id_menu == menu_id).first()
		if not item:
			return jsonify({"message": "Menu tidak ditemukan"}), 404
		return jsonify(_serialize_menu(item))
	finally:
		db.close()


def create_menu():
	if not request.is_json:
		return jsonify({"message": "Gunakan format JSON"}), 400
	body = request.json
	required = ["name", "price", "category", "image_url"]
	if not all(k in body for k in required):
		return jsonify({"message": "Data tidak lengkap"}), 400

	db = database.SessionLocal()
	try:
		item = Menu(name=body["name"], price=body["price"], category=body["category"], image_url=body["image_url"])
		db.add(item)
		db.commit()
		db.refresh(item)
		return jsonify(_serialize_menu(item)), 201
	finally:
		db.close()


def update_menu(menu_id: int):
	if not request.is_json:
		return jsonify({"message": "Gunakan format JSON"}), 400
	body = request.json

	db = database.SessionLocal()
	try:
		item = db.query(Menu).filter(Menu.id_menu == menu_id).first()
		if not item:
			return jsonify({"message": "Menu tidak ditemukan"}), 404
		for k in ("name", "price", "category", "image_url"):
			if k in body:
				setattr(item, k, body[k])
		db.commit()
		db.refresh(item)
		return jsonify(_serialize_menu(item))
	finally:
		db.close()


def delete_menu(menu_id: int):
	db = database.SessionLocal()
	try:
		item = db.query(Menu).filter(Menu.id_menu == menu_id).first()
		if not item:
			return jsonify({"message": "Menu tidak ditemukan"}), 404
		db.delete(item)
		db.commit()
		return jsonify({"message": "Menu dihapus"})
	finally:
		db.close()
