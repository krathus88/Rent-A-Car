from main import db, bcrypt
from sqlalchemy.orm import relationship


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    phone_number_prefix = db.Column(db.String(5), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(20), nullable=False)

    def __init__(self, username, email, name, surname, phone_number_prefix, phone_number, password):
        self.username = username
        self.email = email
        self.name = name
        self.surname = surname
        self.phone_number_prefix = phone_number_prefix
        self.phone_number = phone_number
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_file_name = db.Column(db.String(255), nullable=False)
    vehicle_type = db.Column(db.String(1), nullable=False)
    num_people = db.Column(db.Integer, nullable=False)
    num_doors = db.Column(db.Integer, nullable=False)
    luggage = db.Column(db.Integer, nullable=False)
    gear_type = db.Column(db.String(1), nullable=False)
    air_conditioning = db.Column(db.String(10), nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    vehicle_class = db.Column(db.String(10), nullable=False)
    last_check_up = db.Column(db.String, nullable=False)
    next_check_up = db.Column(db.String, nullable=False)
    last_ved = db.Column(db.String, nullable=False)
    next_ved = db.Column(db.String, nullable=False)
    vehicle_available_again = db.Column(db.String, nullable=True)
    vehicle_status = db.Column(db.String(1), nullable=False)

    def __init__(self, name, image_file_name, vehicle_type, num_people, num_doors, luggage, gear_type, air_conditioning, price_per_day, vehicle_class, last_check_up, next_check_up, last_ved, next_ved, vehicle_available_again, vehicle_status):
        self.name = name
        self.image_file_name = image_file_name
        self.vehicle_type = vehicle_type
        self.num_people = num_people
        self.num_doors = num_doors
        self.luggage = luggage
        self.gear_type = gear_type
        self.air_conditioning = air_conditioning
        self.price_per_day = price_per_day
        self.vehicle_class = vehicle_class
        self.last_check_up = last_check_up
        self.next_check_up = next_check_up
        self.last_ved = last_ved
        self.next_ved = next_ved
        self.vehicle_available_again = vehicle_available_again
        self.vehicle_status = vehicle_status


class Bookings(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)  # column "vehicle_id" is the same as column "id" from Vehicle
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # column "user_id" is the same as column "id" from User
    rent_from_date = db.Column(db.String, nullable=False)
    rent_until_date = db.Column(db.String, nullable=False)
    rental_status = db.Column(db.String, nullable=False)

    # Define the relationship with the Vehicle table
    vehicle_relation = relationship('Vehicle', backref='rentals', lazy=True)
    # Define the relationship with the User table
    user_relation = relationship('User', backref='rentals', lazy=True)

    def __init__(self, rent_from_date, rent_until_date, rental_status):
        self.rent_from_date = rent_from_date
        self.rent_until_date = rent_until_date
        self.rental_status = rental_status


class CompanyBalance(db.Model):
    __tablename__ = 'balance'
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, nullable=False)
    transaction_cost = db.Column(db.Float, nullable=True)
    transaction_date = db.Column(db.String, nullable=True)

    def __init__(self, balance, transaction_cost, transaction_date):
        self.balance = balance
        self.transaction_cost = transaction_cost
        self.transaction_date = transaction_date
