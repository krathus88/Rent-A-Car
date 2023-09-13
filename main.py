from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import secrets
import threading
import os 
from tkinter import *
from app import Product

app = Flask(__name__)
# Define the path to the 'instance' directory
instance_path = os.path.join(app.root_path, 'instance')
# Create the 'instance' directory if it doesn't exist
os.makedirs(instance_path, exist_ok=True)
# Configure SQLite database URIs
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "logins.db")}'
app.config['SQLALCHEMY_BINDS'] = {
    'vehicle': f'sqlite:///{os.path.join(instance_path, "vehicles.db")}',
    'balance': f'sqlite:///{os.path.join(instance_path, "company_balance.db")}',
    'rented': f'sqlite:///{os.path.join(instance_path, "rented_vehicles.db")}'
}
app.config['SECRET_KEY'] = secrets.token_hex(32)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from website import *  # Import the Flask app instance


# Function to run the Flask website
def run_flask():
    app.run(debug=True)


# Function to run the Tkinter app
def run_tkinter():
    root = Tk()
    app_tkinter = Product(root)
    root.mainloop()


if __name__ == '__main__':
    # Start the Tkinter app in a separate thread
    tkinter_thread = threading.Thread(target=run_tkinter)
    tkinter_thread.start()

    with app.app_context():
        db.create_all()
        db.session.commit()

    # Start the Flask app using Gunicorn
    app.run(host='127.0.0.1', port=5000)  # No need for debug=True

    # Wait for the Tkinter thread to finish
    tkinter_thread.join()
