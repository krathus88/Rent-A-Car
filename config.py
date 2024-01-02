import secrets
import os


class Config:
    # Define the path to the 'instance' directory
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    # Create the 'instance' directory if it doesn't exist
    os.makedirs(instance_path, exist_ok=True)

    SECRET_KEY = secrets.token_hex(32)
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(instance_path, "rent_a_car.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False