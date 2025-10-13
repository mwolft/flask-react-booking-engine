import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from .models import db, User, RoomTypes, Rooms, Availability, Bookings, Payments

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    
    admin = Admin(app, name='Hotel Admin', template_mode='bootstrap3')

    # Añadimos cada modelo al panel
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(RoomTypes, db.session))
    admin.add_view(ModelView(Rooms, db.session))
    admin.add_view(ModelView(Availability, db.session))
    admin.add_view(ModelView(Bookings, db.session))
    admin.add_view(ModelView(Payments, db.session))
