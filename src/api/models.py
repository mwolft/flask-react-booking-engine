from datetime import datetime
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

db = SQLAlchemy()


class UserRole(Enum):
    GUEST = 'guest'
    ADMIN = 'admin'
    STAFF = 'staff'


class User(db.Model):
    __tablename__ = 'users' 

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.GUEST)
    is_active = db.Column(db.Boolean, default=True)

    # Dirección personal
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    address = db.Column(db.String(200))
    postal_code = db.Column(db.String(20))
    document_id = db.Column(db.String(50))

    # Facturación
    billing_name = db.Column(db.String(150))
    billing_nif = db.Column(db.String(20))
    billing_address = db.Column(db.String(200))
    billing_city = db.Column(db.String(100))
    billing_postal_code = db.Column(db.String(20))
    billing_country = db.Column(db.String(100))

    # Auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    notes = db.Column(db.Text)

    # Relaciones
    bookings = db.relationship('Bookings', back_populates='user', lazy=True)

    # Métodos auxiliares
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def serialize(self, include_private=False):  # ✅ ahora dentro de la clase
        data = {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role.value if self.role else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

        data.update({
            "country": self.country,
            "city": self.city,
            "address": self.address,
            "postal_code": self.postal_code,
            "document_id": self.document_id,
        })

        data.update({
            "billing_name": self.billing_name,
            "billing_nif": self.billing_nif,
            "billing_address": self.billing_address,
            "billing_city": self.billing_city,
            "billing_postal_code": self.billing_postal_code,
            "billing_country": self.billing_country,
        })

        if include_private:
            data["notes"] = self.notes

        return data


class RoomTypes(db.Model):
    __tablename__ = "room_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    capacity = db.Column(db.Integer, nullable=False, default=2)
    beds = db.Column(db.String(100))  # Ej: "1 cama doble", "2 individuales"
    base_price = db.Column(db.Float, nullable=False, default=0.0)
    total_rooms = db.Column(db.Integer, nullable=False, default=1)
    rooms_per_floor = db.Column(db.Integer, nullable=True)
    image_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    rooms = db.relationship("Rooms", back_populates="room_type", lazy=True)
    pricing_rules = db.relationship('PricingRules', back_populates='room_type', lazy=True)
    bookings = db.relationship("Bookings", back_populates="room_type", lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "capacity": self.capacity,
            "beds": self.beds,
            "base_price": self.base_price,
            "total_rooms": self.total_rooms,
            "rooms_per_floor": self.rooms_per_floor,
            "image_url": self.image_url,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Rooms(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), unique=True, nullable=False)
    room_type_id = db.Column(db.Integer, db.ForeignKey("room_types.id"), nullable=False)
    floor = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default="active")
    is_available = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

    # Relaciones
    availabilities = db.relationship('Availability', back_populates='room', lazy=True)
    bookings = db.relationship("Bookings", back_populates="room", lazy=True)
    room_type = db.relationship("RoomTypes", back_populates="rooms", lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "room_number": self.room_number,
            "room_type_id": self.room_type_id,
            "room_type_name": self.room_type.name if self.room_type else None,
            "floor": self.floor,
            "description": self.description,
            "status": self.status,
            "is_available": self.is_available,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Availability(db.Model):
    __tablename__ = "availability"

    id = db.Column(db.Integer, primary_key=True)

    # 🔹 Periodo bloqueado
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    # 🔹 Puede aplicarse a una habitación concreta o a todo un tipo
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=True)
    room_type_id = db.Column(db.Integer, db.ForeignKey("room_types.id"), nullable=True)

    # 🔹 Motivos y estado
    closed_manually = db.Column(db.Boolean, default=False)
    maintenance_block = db.Column(db.Boolean, default=False)
    reason = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔹 Relaciones ORM
    room = db.relationship("Rooms", backref=db.backref("availability_blocks", lazy=True))
    room_type = db.relationship("RoomTypes", backref=db.backref("availability_blocks", lazy=True))

    def serialize(self):
        return {
            "id": self.id,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "room_id": self.room_id,
            "room_number": self.room.room_number if self.room else None,
            "room_type_id": self.room_type_id,
            "room_type_name": self.room_type.name if self.room_type else None,
            "closed_manually": self.closed_manually,
            "maintenance_block": self.maintenance_block,
            "reason": self.reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Bookings(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)

    # 🔹 Relaciones clave
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_types.id'), nullable=False)

    # 🔹 Fechas y estado
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    nights = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled, checked_in, checked_out

    # 🔹 Precio y pago
    price_per_night = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, paid, refunded
    payment_method = db.Column(db.String(20))  # stripe, paypal, cash

    # 🔹 Datos del huésped (en caso de no tener usuario registrado)
    guest_name = db.Column(db.String(150))
    guest_email = db.Column(db.String(120))
    guest_phone = db.Column(db.String(50))

    # 🔹 Tiempos y control
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)

    # 🔹 Relaciones ORM
    user = db.relationship('User', back_populates='bookings')
    room = db.relationship('Rooms', back_populates='bookings')
    room_type = db.relationship('RoomTypes', back_populates='bookings')

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": f"{self.user.first_name} {self.user.last_name}" if self.user else None,
            "room_id": self.room_id,
            "room_number": self.room.room_number if self.room else None,
            "room_type_id": self.room_type_id,
            "room_type_name": self.room_type.name if self.room_type else None,
            "check_in": self.check_in.isoformat(),
            "check_out": self.check_out.isoformat(),
            "nights": self.nights,
            "status": self.status,
            "price_per_night": float(self.price_per_night),
            "total_price": float(self.total_price),
            "payment_status": self.payment_status,
            "payment_method": self.payment_method,
            "guest_name": self.guest_name,
            "guest_email": self.guest_email,
            "guest_phone": self.guest_phone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "notes": self.notes
        }


class Payments(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)

    # 🔹 Relaciones clave
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # 🔹 Datos del pago
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(10), default='EUR')
    method = db.Column(db.String(50))  # stripe, paypal, cash, transfer, etc.
    status = db.Column(db.String(20), default='pending')  # pending, paid, refunded, failed
    transaction_id = db.Column(db.String(255))  # ID de Stripe/PayPal o referencia bancaria
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔹 Auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)

    # 🔹 Relaciones ORM
    booking = db.relationship('Bookings', backref=db.backref('payments', lazy=True))
    user = db.relationship('User', backref=db.backref('payments', lazy=True))

    def serialize(self):
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "user_id": self.user_id,
            "amount": float(self.amount),
            "currency": self.currency,
            "method": self.method,
            "status": self.status,
            "transaction_id": self.transaction_id,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "notes": self.notes
        }


def update_availability_for_booking(booking, make_available=False):
    """Marca o libera disponibilidad según el estado de la reserva"""
    current_date = booking.check_in
    while current_date < booking.check_out:
        availability = Availability.query.filter_by(
            room_id=booking.room_id,
            date=current_date
        ).first()

        if availability:
            availability.is_available = make_available
            availability.booked_by_booking_id = None if make_available else booking.id
        else:
            if not make_available:
                new_availability = Availability(
                    date=current_date,
                    room_id=booking.room_id,
                    room_type_id=booking.room_type_id,
                    is_available=False,
                    booked_by_booking_id=booking.id
                )
                db.session.add(new_availability)

        current_date += timedelta(days=1)


class PricingRules(db.Model):
    __tablename__ = "pricing_rules"

    id = db.Column(db.Integer, primary_key=True)
    room_type_id = db.Column(db.Integer, db.ForeignKey("room_types.id"), nullable=False)

    # 🔹 Nombre visible en el admin o interfaz (Ej: "Super Oferta", "Temporada Alta")
    name = db.Column(db.String(100), nullable=False)

    # 🔹 Multiplicador o valor absoluto (ej: 1.2 = +20%, 0.8 = -20%)
    price_modifier = db.Column(db.Float, nullable=False, default=1.0)

    # 🔹 Alternativa opcional: precio fijo en vez de modificador
    fixed_price = db.Column(db.Float, nullable=True)

    # 🔹 Rango de fechas
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    # 🔹 Color visual para paneles o gráficos
    color = db.Column(db.String(20), nullable=True)

    # 🔹 Estado
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación inversa con RoomType
    room_type = db.relationship('RoomTypes', back_populates='pricing_rules')


    def serialize(self):
        return {
            "id": self.id,
            "room_type_id": self.room_type_id,
            "room_type_name": self.room_type.name if self.room_type else None,
            "name": self.name,
            "price_modifier": self.price_modifier,
            "fixed_price": self.fixed_price,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "color": self.color,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
