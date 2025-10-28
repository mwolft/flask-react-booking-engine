import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from .models import db, User, RoomTypes, Rooms, Availability, Bookings, Payments


class RoomsAdmin(ModelView):
    form_columns = ['room_number', 'room_type', 'floor', 'description', 'status', 'is_available', 'notes']
    column_list = ['room_number', 'room_type', 'floor', 'status', 'is_available', 'created_at']
    form_ajax_refs = {
        'room_type': {
            'fields': ('name',)
        }
    }


def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

    admin = Admin(app, name='Hotel Admin', template_mode='bootstrap3')

    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(RoomTypes, db.session))
    admin.add_view(RoomsAdmin(Rooms, db.session))  
    admin.add_view(ModelView(Availability, db.session))
    admin.add_view(ModelView(Bookings, db.session))
    admin.add_view(ModelView(Payments, db.session))




