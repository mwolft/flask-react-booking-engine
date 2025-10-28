import os
from datetime import datetime, timedelta
from flask_admin import Admin, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from flask_admin.form.widgets import DatePickerWidget
from wtforms.fields import DateField
from flask import flash, redirect, request, url_for
from .models import db, User, RoomTypes, Rooms, Availability, Bookings, Payments


# =====================================================
# 🔹 Habitaciones (Rooms)
# =====================================================
class RoomsAdmin(ModelView):
    """Vista personalizada para habitaciones"""
    form_columns = ['room_number', 'room_type', 'floor', 'description', 'status', 'is_available', 'notes']
    column_list = ['room_number', 'room_type', 'floor', 'status', 'is_available', 'created_at']

    form_ajax_refs = {
        'room_type': {'fields': ('name',)}
    }

    column_labels = {
        "room_number": "Número",
        "room_type": "Tipo",
        "floor": "Planta",
        "status": "Estado",
        "is_available": "Disponible",
        "created_at": "Creado el"
    }


# =====================================================
# 🔹 Disponibilidad / Cierres (Availability)
# =====================================================
class AvailabilityAdminView(ModelView):
    """Vista para gestionar bloqueos de disponibilidad (cierres o mantenimiento)"""

    # 🔒 Acceso (ajusta si tienes control de login)
    def is_accessible(self):
        return True

    # 🧭 Configuración general
    column_list = [
        "id", "room", "room_type",
        "start_date", "end_date",
        "closed_manually", "maintenance_block",
        "reason", "created_at"
    ]

    column_labels = {
        "room": "Habitación",
        "room_type": "Tipo de habitación",
        "start_date": "Inicio",
        "end_date": "Fin",
        "closed_manually": "Cierre manual",
        "maintenance_block": "Mantenimiento",
        "reason": "Motivo",
        "created_at": "Creado el",
    }

    column_filters = [
        "room",
        "room_type",
        "closed_manually",
        "maintenance_block",
        "start_date",
        "end_date",
    ]

    column_searchable_list = ["reason"]
    column_default_sort = ("start_date", True)

    form_columns = [
        "room",
        "room_type",
        "start_date",
        "end_date",
        "closed_manually",
        "maintenance_block",
        "reason",
    ]

    # 📅 Widgets de fecha
    form_overrides = {
        "start_date": DateField,
        "end_date": DateField,
    }

    form_args = {
        "start_date": {"widget": DatePickerWidget()},
        "end_date": {"widget": DatePickerWidget()},
        "reason": {"label": "Motivo del cierre"},
    }

    # 🧹 Ajuste visual
    can_view_details = True
    create_modal = True
    edit_modal = True
    page_size = 25

    # =====================================================
    # ⚙️ Acción personalizada: cerrar por mantenimiento X días
    # =====================================================
    @action('close_maintenance', 'Cerrar por mantenimiento (3 días)', '¿Cerrar las seleccionadas por mantenimiento?')
    def action_close_maintenance(self, ids):
        try:
            for room_id in ids:
                room = Rooms.query.get(room_id)
                if room:
                    block = Availability(
                        start_date=datetime.utcnow().date(),
                        end_date=(datetime.utcnow() + timedelta(days=3)).date(),
                        room_id=room.id,
                        room_type_id=room.room_type_id,
                        maintenance_block=True,
                        closed_manually=True,
                        reason="Cierre temporal por mantenimiento (acción rápida)"
                    )
                    db.session.add(block)
            db.session.commit()
            flash(f"Se cerraron {len(ids)} habitaciones por mantenimiento durante 3 días.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear cierres: {str(e)}", "error")



# =====================================================
# 🔹 Configuración del panel de administración
# =====================================================
def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

    admin = Admin(app, name='Hotel Admin', template_mode='bootstrap3')

    # Secciones
    admin.add_view(ModelView(User, db.session, name="Usuarios"))
    admin.add_view(ModelView(RoomTypes, db.session, name="Tipos de habitación"))
    admin.add_view(RoomsAdmin(Rooms, db.session, name="Habitaciones"))
    admin.add_view(AvailabilityAdminView(Availability, db.session, name="Disponibilidad / Cierres"))
    admin.add_view(ModelView(Bookings, db.session, name="Reservas"))
    admin.add_view(ModelView(Payments, db.session, name="Pagos"))




