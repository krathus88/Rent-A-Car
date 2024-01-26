from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import threading
from tkinter import *
from config import Config
from app.app import Product

app = Flask(__name__,
            static_url_path="",
            template_folder="website/templates",
            static_folder="website/static")
app.config.from_object(Config)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from website.website import *


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

    # Create all the tables defined in the models within the Flask application context
    with app.app_context():
        db.create_all()  # Create the database tables
        db.session.commit()  # Commit the changes to the database

    # Start the Flask app using Gunicorn
    app.run(host='127.0.0.1', port=5000, threaded=True)

    # Wait for the Tkinter thread to finish
    tkinter_thread.join()