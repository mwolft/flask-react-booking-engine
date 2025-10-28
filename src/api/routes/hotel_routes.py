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
# =====================================================
# 🔹 RUTA 1: Listar todos los bloqueos creados
# =====================================================
@hotel_bp.route('/availability', methods=['GET'])
def get_availability_blocks():
    """
    Devuelve todos los bloqueos de disponibilidad (cierres, mantenimiento...).
    Por defecto, si no hay registros, se considera todo disponible.
    """
    blocks = Availability.query.order_by(Availability.start_date.desc()).all()
    results = [b.serialize() for b in blocks]
    return jsonify(results), 200


# =====================================================
# 🔹 RUTA 2: Crear un nuevo bloqueo de disponibilidad
# =====================================================
@hotel_bp.route('/availability', methods=['POST'])
def block_availability():
    """
    Crea un bloqueo de disponibilidad entre dos fechas,
    ya sea para una habitación concreta o un tipo completo.
    """
    data = request.get_json()

    if not data or "start_date" not in data or "end_date" not in data:
        return jsonify({"error": "Missing required fields: start_date or end_date"}), 400

    try:
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    block = Availability(
        start_date=start_date,
        end_date=end_date,
        room_id=data.get("room_id"),
        room_type_id=data.get("room_type_id"),
        closed_manually=data.get("closed_manually", True),
        maintenance_block=data.get("maintenance_block", False),
        reason=data.get("reason", "Cierre manual")
    )

    db.session.add(block)
    db.session.commit()
    return jsonify(block.serialize()), 201


# =====================================================
# 🔹 RUTA 3: Editar un bloqueo existente
# =====================================================
@hotel_bp.route('/availability/<int:block_id>', methods=['PUT'])
def update_availability_block(block_id):
    """
    Modifica las fechas o el motivo de un bloqueo existente.
    """
    data = request.get_json()
    block = Availability.query.get(block_id)

    if not block:
        return jsonify({"error": "Block not found"}), 404

    try:
        if "start_date" in data:
            block.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        if "end_date" in data:
            block.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    if "reason" in data:
        block.reason = data["reason"]
    if "closed_manually" in data:
        block.closed_manually = data["closed_manually"]
    if "maintenance_block" in data:
        block.maintenance_block = data["maintenance_block"]

    db.session.commit()
    return jsonify(block.serialize()), 200


# =====================================================
# 🔹 RUTA 4: Eliminar un bloqueo
# =====================================================
@hotel_bp.route('/availability/<int:block_id>', methods=['DELETE'])
def delete_availability_block(block_id):
    """
    Elimina un bloqueo de disponibilidad.
    """
    block = Availability.query.get(block_id)
    if not block:
        return jsonify({"error": "Block not found"}), 404

    db.session.delete(block)
    db.session.commit()
    return jsonify({"message": f"Block {block_id} deleted successfully"}), 200


# =====================================================
# 🔹 RUTA 5: Consultar disponibilidad real (para el cliente)
# =====================================================
@hotel_bp.route('/availability/search', methods=['GET'])
def get_available_rooms():
    """
    Devuelve habitaciones disponibles para un rango de fechas,
    excluyendo las bloqueadas o en mantenimiento.
    Ejemplo: /availability/search?checkin=2025-11-05&checkout=2025-11-08
    """
    check_in = request.args.get("checkin")
    check_out = request.args.get("checkout")

    if not check_in or not check_out:
        return jsonify({"error": "Missing required query params: checkin and checkout"}), 400

    try:
        check_in = datetime.strptime(check_in, "%Y-%m-%d").date()
        check_out = datetime.strptime(check_out, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # 1️⃣ Bloqueos que solapan con el rango solicitado
    blocked = Availability.query.filter(
        Availability.start_date < check_out,
        Availability.end_date > check_in
    ).all()

    blocked_room_ids = [b.room_id for b in blocked if b.room_id]
    blocked_type_ids = [b.room_type_id for b in blocked if b.room_type_id]

    # 2️⃣ Habitaciones activas y no bloqueadas
    available_rooms = Rooms.query.filter(
        Rooms.status == "active",
        Rooms.is_available == True,
        ~Rooms.id.in_(blocked_room_ids),
        ~Rooms.room_type_id.in_(blocked_type_ids)
    ).all()

    # 3️⃣ Serializar resultado
    results = []
    for room in available_rooms:
        results.append({
            **room.serialize(),
            "room_type": room.room_type.serialize() if room.room_type else None
        })

    return jsonify(results), 200


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
