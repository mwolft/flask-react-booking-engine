from flask import Blueprint, jsonify, request
from api.models import db, RoomTypes, Rooms, Availability, Bookings
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import db, Bookings, update_availability_for_booking
from api.utils import apply_pricing_rules

hotel_bp = Blueprint('hotel_bp', __name__)




# Room types

@hotel_bp.route('/room_types', methods=['GET'])
def get_room_types():
    room_types = RoomTypes.query.all()
    results = [room.serialize() for room in room_types]
    return jsonify(results), 200


@hotel_bp.route('/room_types', methods=['POST'])
def create_room_type():
    data = request.get_json()

    if not data or "name" not in data or "price_per_night" not in data:
        return jsonify({"error": "Missing required fields: name, price_per_night"}), 400

    new_room_type = RoomTypes(
        name=data["name"],
        description=data.get("description"),
        capacity=data.get("capacity", 2),
        beds=data.get("beds"),
        price_per_night=data["price_per_night"],
        image_url=data.get("image_url"),
        is_active=data.get("is_active", True)
    )

    db.session.add(new_room_type)
    db.session.commit()

    return jsonify(new_room_type.serialize()), 201


@hotel_bp.route('/room_types/<int:room_type_id>', methods=['PUT'])
def update_room_type(room_type_id):
    data = request.get_json()
    room_type = RoomTypes.query.get(room_type_id)

    if not room_type:
        return jsonify({"error": "Room type not found"}), 404

    room_type.name = data.get("name", room_type.name)
    room_type.description = data.get("description", room_type.description)
    room_type.capacity = data.get("capacity", room_type.capacity)
    room_type.beds = data.get("beds", room_type.beds)
    room_type.price_per_night = data.get(
        "price_per_night", room_type.price_per_night)
    room_type.image_url = data.get("image_url", room_type.image_url)
    room_type.is_active = data.get("is_active", room_type.is_active)

    db.session.commit()

    return jsonify(room_type.serialize()), 200


@hotel_bp.route('/room_types/<int:room_type_id>', methods=['DELETE'])
def delete_room_type(room_type_id):
    room_type = RoomTypes.query.get(room_type_id)

    if not room_type:
        return jsonify({"error": "Room type not found"}), 404

    db.session.delete(room_type)
    db.session.commit()

    return jsonify({"message": f"Room type {room_type_id} deleted successfully"}), 200


# Rooms


@hotel_bp.route('/rooms', methods=['GET'])
def get_rooms():
    rooms = Rooms.query.all()
    results = [room.serialize() for room in rooms]
    return jsonify(results), 200


@hotel_bp.route('/rooms', methods=['POST'])
def create_room():
    data = request.get_json()

    if not data or "room_number" not in data or "room_type_id" not in data:
        return jsonify({"error": "Missing required fields: room_number, room_type_id"}), 400

    # Verificar si ya existe una habitación con ese número
    existing_room = Rooms.query.filter_by(
        room_number=data["room_number"]).first()
    if existing_room:
        return jsonify({"error": "Room number already exists"}), 400

    new_room = Rooms(
        room_number=data["room_number"],
        room_type_id=data["room_type_id"],
        floor=data.get("floor"),
        description=data.get("description"),
        is_available=data.get("is_available", True),
        notes=data.get("notes")
    )

    db.session.add(new_room)
    db.session.commit()

    return jsonify(new_room.serialize()), 201


@hotel_bp.route('/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    data = request.get_json()
    room = Rooms.query.get(room_id)

    if not room:
        return jsonify({"error": "Room not found"}), 404

    room.room_number = data.get("room_number", room.room_number)
    room.room_type_id = data.get("room_type_id", room.room_type_id)
    room.floor = data.get("floor", room.floor)
    room.description = data.get("description", room.description)
    room.is_available = data.get("is_available", room.is_available)
    room.notes = data.get("notes", room.notes)

    db.session.commit()
    return jsonify(room.serialize()), 200


@hotel_bp.route('/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    room = Rooms.query.get(room_id)

    if not room:
        return jsonify({"error": "Room not found"}), 404

    db.session.delete(room)
    db.session.commit()
    return jsonify({"message": f"Room {room_id} deleted successfully"}), 200


# Availity


@hotel_bp.route('/availability', methods=['GET'])
def get_availability():
    availabilities = Availability.query.all()
    results = [a.serialize() for a in availabilities]
    return jsonify(results), 200


@hotel_bp.route('/availability', methods=['POST'])
def create_availability():
    data = request.get_json()

    if not data or "date" not in data:
        return jsonify({"error": "Missing required field: date"}), 400

    try:
        parsed_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    new_availability = Availability(
        date=parsed_date,
        room_id=data.get("room_id"),
        room_type_id=data.get("room_type_id"),
        is_available=data.get("is_available", True),
        booked_by_booking_id=data.get("booked_by_booking_id")
    )

    db.session.add(new_availability)
    db.session.commit()

    return jsonify(new_availability.serialize()), 201


@hotel_bp.route('/availability/<int:availability_id>', methods=['PUT'])
def update_availability(availability_id):
    data = request.get_json()
    availability = Availability.query.get(availability_id)

    if not availability:
        return jsonify({"error": "Availability record not found"}), 404

    if "date" in data:
        availability.date = data["date"]
    if "room_id" in data:
        availability.room_id = data["room_id"]
    if "room_type_id" in data:
        availability.room_type_id = data["room_type_id"]
    if "is_available" in data:
        availability.is_available = data["is_available"]
    if "booked_by_booking_id" in data:
        availability.booked_by_booking_id = data["booked_by_booking_id"]

    db.session.commit()

    return jsonify(availability.serialize()), 200


@hotel_bp.route('/availability/<int:availability_id>', methods=['DELETE'])
def delete_availability(availability_id):
    availability = Availability.query.get(availability_id)

    if not availability:
        return jsonify({"error": "Availability record not found"}), 404

    db.session.delete(availability)
    db.session.commit()

    return jsonify({"message": f"Availability {availability_id} deleted successfully"}), 200


# Bookings


@hotel_bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_user_bookings():
    user_id = int(get_jwt_identity())

    bookings = Bookings.query.filter_by(user_id=user_id).order_by(
        Bookings.created_at.desc()).all()

    if not bookings:
        return jsonify({"message": "No bookings found for this user"}), 200

    return jsonify([b.serialize() for b in bookings]), 200


@hotel_bp.route('/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    # 🔹 Validar campos obligatorios
    required_fields = ["guest_name", "guest_email", "guest_phone", "check_in", "check_out", "room_type_id"]
    missing = [field for field in required_fields if not data.get(field)]

    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    try:
        booking = Bookings(
            user_id=user_id,
            room_id=data.get("room_id"),
            room_type_id=data.get("room_type_id"),
            check_in=datetime.strptime(data.get("check_in"), "%Y-%m-%d").date(),
            check_out=datetime.strptime(data.get("check_out"), "%Y-%m-%d").date(),
            nights=data.get("nights", 1),
            status="pending",
            price_per_night=data.get("price_per_night", 0),
            total_price=data.get("total_price", 0),
            payment_status="unpaid",
            guest_name=data.get("guest_name").strip(),
            guest_email=data.get("guest_email").strip(),
            guest_phone=data.get("guest_phone").strip(),
            notes=data.get("notes")
        )

        db.session.add(booking)
        db.session.commit()

        # 🔹 Actualizar disponibilidad (bloquear fechas)
        update_availability_for_booking(booking)
        db.session.commit()

        return jsonify(booking.serialize()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@hotel_bp.route('/bookings/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    user_id = int(get_jwt_identity())
    booking = Bookings.query.filter_by(id=booking_id, user_id=user_id).first()

    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    if booking.status != "pending":
        return jsonify({"error": "Only pending bookings can be modified"}), 400

    data = request.get_json()

    try:
        if "check_in" in data:
            booking.check_in = datetime.strptime(
                data["check_in"], "%Y-%m-%d").date()
        if "check_out" in data:
            booking.check_out = datetime.strptime(
                data["check_out"], "%Y-%m-%d").date()
        if "status" in data:
            booking.status = data["status"]
        if "notes" in data:
            booking.notes = data["notes"]

        db.session.commit()
        return jsonify(booking.serialize()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@hotel_bp.route('/bookings/<int:booking_id>', methods=['DELETE'])
@jwt_required()
def cancel_booking(booking_id):
    user_id = int(get_jwt_identity())
    booking = Bookings.query.filter_by(id=booking_id, user_id=user_id).first()

    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    if booking.status != "pending":
        return jsonify({"error": "Only pending bookings can be cancelled"}), 400

    try:
        booking.status = "cancelled"
        update_availability_for_booking(booking, make_available=True)
        db.session.commit()
        return jsonify({"message": "Booking cancelled and availability updated"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@hotel_bp.route('/pricing/apply/<int:room_type_id>', methods=['POST'])
def update_prices(room_type_id):
    result = apply_pricing_rules(room_type_id)
    return jsonify(result), 200
