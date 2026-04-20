from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='conductor')

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer)
    plate = db.Column(db.String(20), unique=True, nullable=False)
    serial = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(20), default='Disponible')

class Driver(db.Model):
    __tablename__ = 'drivers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    license_number = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(200))

class Rental(db.Model):
    __tablename__ = 'rentals'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    end_date = db.Column(db.DateTime, nullable=True)
    origin = db.Column(db.String(200))
    destination = db.Column(db.String(200))
    amount = db.Column(db.Float, default=0)
    vehicle = db.relationship('Vehicle', backref=db.backref('rentals', lazy=True))
    driver = db.relationship('Driver', backref=db.backref('rentals', lazy=True))

class Maintenance(db.Model):
    __tablename__ = 'maintenance'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    type = db.Column(db.String(50))
    workshop = db.Column(db.String(100))
    description = db.Column(db.Text)
    cost = db.Column(db.Float)
    next_maintenance_date = db.Column(db.DateTime)
    vehicle = db.relationship('Vehicle', backref=db.backref('maintenances', lazy=True))
