import phonenumbers
import re
from datetime import date, datetime
from math import ceil

from flask import render_template, request, redirect, session, url_for
from sqlalchemy.exc import IntegrityError

from databases import Vehicle, User, RentedVehicle, CompanyBalance
from main import app, db, bcrypt

pickup_date_str = ""
dropoff_date_str = ""


@app.route('/', methods=['GET', 'POST'])
def login():
    # Check if the user is already logged in by verifying the presence of the user_id in the session
    if 'user_id' in session:
        return redirect('/main-page')  # Redirect to the main page if the user is already logged in

    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email')
        password = request.form.get('password')
        button_clicked = request.form.get('button_clicked')  # Check if the button was clicked

        if button_clicked:  # Check if the button was clicked
            if not username_or_email or not password:
                session['error'] = "Both username/email and password are required"
                return redirect('/')  # Redirect to clear the POST data

            user = User.query.filter(
                (User.username == username_or_email) | (User.email == username_or_email)
            ).first()

            # Checks if the username/email and the password ("decrypted") are valid
            if user and user.check_password(password):
                session['user_id'] = user.id  # Store the user ID in the session
                session.pop('error', None)  # Clear the error message from session
                return redirect("/main-page")
            else:
                session['error'] = "Invalid username or password"
                return redirect('/')  # Redirect to clear the POST data

    error = session.pop('error', None)  # Clear the error message on page refresh
    logout_success = session.pop('logout_success', None)  # Clear the logout success message on page refresh
    return render_template("index.html", error=error or "", logout_success=logout_success or "")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        raw_phone_number = request.form['phone_number']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check for any empty field
        if not username or not email or not password:
            session['error'] = "All fields are required."
            return redirect('/register')  # Redirect to clear the POST data

        # Check for a valid email address
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            session['error'] = "Invalid email address."
            return redirect('/register')

        # Check for a valid phone number
        try:
            parsed_phone_number = phonenumbers.parse(raw_phone_number, None)
            if not phonenumbers.is_valid_number(parsed_phone_number):
                session['error'] = "Invalid phone number."
                return redirect('/register')
            # Extract prefix and phone number
            phone_number = parsed_phone_number.national_number
            phone_number_prefix = "+" + str(parsed_phone_number.country_code)
        except phonenumbers.NumberParseException:
            session['error'] = "Invalid phone number format."
            return redirect('/register')

        # Check for special characters in the username
        if re.search(r'[^a-zA-Z0-9_]', username):
            session['error'] = "Username should only contain letters, numbers and underscores."
            return redirect('/register')

        # username length < 21
        if len(username) > 20:
            session['error'] = "Username cannot exceed 20 characters."
            return redirect('/register')

        # email length < 256
        if len(email) > 255:
            session['error'] = "Email address cannot exceed 255 characters."
            return redirect('/register')

        # password length < 21
        if len(password) > 20:
            session['error'] = "Password cannot exceed 20 characters."
            return redirect('/register')

        # if username or email is already in the DB it crashes gives an error to the user
        try:
            new_user = User(username=username, email=email, name=name, surname=surname, phone_number_prefix=phone_number_prefix, phone_number=phone_number, password=password)
            db.session.add(new_user)
            db.session.commit()
            return render_template("register-successful.html")
        except IntegrityError:
            session['error'] = "Username or email already in use."
            return redirect('/register')

    error = session.pop('error', None)  # Clear the error message on page refresh
    return render_template("register.html", error=error or "")


@app.route('/password-recovery', methods=['GET', 'POST'])
def password_recovery():
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email')
        # Perform the password update for the user with the given username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if not username_or_email:
            session['error'] = "Please insert a valid username or email."
            return redirect('/password-recovery')

        if not user:
            session['error'] = "Couldn't find any match in our systems."
            return redirect('/password-recovery')

        # Store the username or email in the session to use it in the next password recovery step
        session['username_or_email'] = username_or_email
        return redirect('/password-recovery-2')

    error = session.pop('error', None)  # Clear the error message on page refresh
    return render_template("password-recovery.html", error=error or "")


@app.route('/password-recovery-2', methods=['GET', 'POST'])
def password_recovery_2():
    if request.method == 'POST':
        new_password = request.form.get('new_password')

        if not new_password:
            session['error'] = "Please insert a valid password."
            return redirect('/password-recovery-2')

        # password length < 21
        if len(new_password) > 20:
            session['error'] = "Password cannot exceed 20 characters"
            return redirect('/password-recovery-2')

        # Retrieve the username or email from the session
        username_or_email = session.get('username_or_email')

        # Perform the password update for the user with the given username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        # Update the user's password
        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()

        # Clear the username or email from the session
        session.pop('username_or_email', None)
        return render_template("password-recovery-successful.html")

    error = session.pop('error', None)  # Clear the error message on page refresh
    return render_template("password-recovery-2.html", error=error or "")


# After log in, this is the initial page
@app.route('/main-page', methods=['GET'])
def main_page():
    # Check if the user is logged in by verifying the presence of the user_id in the session
    if 'user_id' in session:
        # Keeps the name and surname of the user in order to call for it
        user = User.query.get(session['user_id'])
        session['name'] = user.name
        session['surname'] = user.surname

        # Keep track of the user's progress
        session['booking_progress'] = 0

        return render_template("main-page.html")
    else:
        return redirect('/')  # Redirect to the login page if the user is not logged in


@app.route('/economy-class', methods=['GET', 'POST'])
def economy_class():
    # Check if the user is logged in by verifying the presence of the user_id in the session
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        session['name'] = user.name
        session['surname'] = user.surname
        # Get the selected pickup and drop-off dates from the request parameters
        global pickup_date_str, dropoff_date_str

        pickup_date_str = request.args.get('pickup_date')
        dropoff_date_str = request.args.get('dropoff_date')
        # If pickup and drop-off dates are not provided, simply render the initial page
        if not pickup_date_str or not dropoff_date_str:
            today = date.today().strftime("%d/%m/%Y")
            return render_template("economy-class.html", today=today, vehicles=[], current_page=1, total_pages=0)

        # Parse the pickup and drop-off dates into datetime objects
        pickup_date = datetime.strptime(pickup_date_str, "%d/%m/%Y")
        dropoff_date = datetime.strptime(dropoff_date_str, "%d/%m/%Y")

        vehicles_to_remove = []  # Create an empty list to store the vehicles that need to be removed
        # Query Vehicle database to get only the vehicles with vehicle_class = "Economy" and vehicle_status = "ready"
        economy_vehicles = Vehicle.query.filter_by(vehicle_class="Economy", vehicle_status="ready").all()

        # Query RentedVehicle database to get only the vehicles with rental_status = "rented"
        rented_vehicles = RentedVehicle.query.filter_by(rental_status="rented").all()

        # Filter out the vehicles that are already rented for the selected dates
        for vehicle in economy_vehicles:
            if rented_vehicles:
                for rented_vehicle in rented_vehicles:
                    if rented_vehicle.vehicle_name == vehicle.name:
                        rent_from_date_str = rented_vehicle.rent_from_date
                        rent_until_date_str = rented_vehicle.rent_until_date

                        rent_from_date = datetime.strptime(rent_from_date_str, "%d/%m/%Y")
                        rent_until_date = datetime.strptime(rent_until_date_str, "%d/%m/%Y")

                        # Check if there's any overlap with the requested pickup and drop-off dates
                        if rent_from_date <= dropoff_date and rent_until_date >= pickup_date:
                            vehicles_to_remove.append(vehicle)  # Add the vehicle to the removal list
            else:
                break

        # Remove the vehicles that are not available from economy_vehicles
        for vehicle in vehicles_to_remove:
            economy_vehicles.remove(vehicle)

        # Get today's date
        today = date.today().strftime("%d/%m/%Y")
        # Get the total number of vehicles
        total_vehicles = len(economy_vehicles)
        # Get the current page number from the 'page' query parameter (defaults to 1)
        page = int(request.args.get('page', 1))
        # Set the number of vehicles to display per page
        vehicles_per_page = 5
        # Calculate the starting and ending indices for the current page
        start_idx = (page - 1) * vehicles_per_page
        end_idx = min(start_idx + vehicles_per_page, total_vehicles)

        # Calculate the total number of pages based on the total number of vehicles and vehicles_per_page
        total_pages = ceil(total_vehicles / vehicles_per_page)
        return render_template("economy-class.html", today=today, vehicles=economy_vehicles[start_idx:end_idx], current_page=page, total_pages=total_pages, pickup_date=pickup_date_str, dropoff_date=dropoff_date_str)

    else:
        return redirect('/')  # Redirect to the login page if the user is not logged in


@app.route('/silver-class', methods=['GET'])
def silver_class():
    # Check if the user is logged in by verifying the presence of the user_id in the session
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        session['name'] = user.name
        session['surname'] = user.surname
        # Get the selected pickup and drop-off dates from the request parameters
        global pickup_date_str, dropoff_date_str

        pickup_date_str = request.args.get('pickup_date')
        dropoff_date_str = request.args.get('dropoff_date')
        # If pickup and drop-off dates are not provided, simply render the initial page
        if not pickup_date_str or not dropoff_date_str:
            today = date.today().strftime("%d/%m/%Y")
            return render_template("silver-class.html", today=today, vehicles=[], current_page=1, total_pages=0)

        # Parse the pickup and drop-off dates into datetime objects
        pickup_date = datetime.strptime(pickup_date_str, "%d/%m/%Y")
        dropoff_date = datetime.strptime(dropoff_date_str, "%d/%m/%Y")

        vehicles_to_remove = []  # Create an empty list to store the vehicles that need to be removed
        # Query Vehicle database to get only the vehicles with vehicle_class = "Silver" and vehicle_status = "ready"
        silver_vehicles = Vehicle.query.filter_by(vehicle_class="Silver", vehicle_status="ready").all()

        # Query RentedVehicle database to get only the vehicles with rental_status = "rented"
        rented_vehicles = RentedVehicle.query.filter_by(rental_status="rented").all()

        # Filter out the vehicles that are already rented for the selected dates
        for vehicle in silver_vehicles:
            if rented_vehicles:
                for rented_vehicle in rented_vehicles:
                    if rented_vehicle.vehicle_name == vehicle.name:
                        rent_from_date_str = rented_vehicle.rent_from_date
                        rent_until_date_str = rented_vehicle.rent_until_date

                        rent_from_date = datetime.strptime(rent_from_date_str, "%d/%m/%Y")
                        rent_until_date = datetime.strptime(rent_until_date_str, "%d/%m/%Y")

                        # Check if there's any overlap with the requested pickup and drop-off dates
                        if rent_from_date <= dropoff_date and rent_until_date >= pickup_date:
                            vehicles_to_remove.append(vehicle)  # Add the vehicle to the removal list
            else:
                break

        # Remove the vehicles that are not available from silver_vehicles
        for vehicle in vehicles_to_remove:
            silver_vehicles.remove(vehicle)

        # Get today's date
        today = date.today().strftime("%d/%m/%Y")
        # Get the total number of vehicles
        total_vehicles = len(silver_vehicles)
        # Get the current page number from the 'page' query parameter (defaults to 1)
        page = int(request.args.get('page', 1))
        # Set the number of vehicles to display per page
        vehicles_per_page = 5
        # Calculate the starting and ending indices for the current page
        start_idx = (page - 1) * vehicles_per_page
        end_idx = min(start_idx + vehicles_per_page, total_vehicles)

        # Calculate the total number of pages based on the total number of vehicles and vehicles_per_page
        total_pages = ceil(total_vehicles / vehicles_per_page)
        return render_template("silver-class.html", today=today, vehicles=silver_vehicles[start_idx:end_idx],
                               current_page=page, total_pages=total_pages, pickup_date=pickup_date_str,
                               dropoff_date=dropoff_date_str)

    else:
        return redirect('/')  # Redirect to the login page if the user is not logged in


@app.route('/gold-class', methods=['GET'])
def gold_class():
    # Check if the user is logged in by verifying the presence of the user_id in the session
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        session['name'] = user.name
        session['surname'] = user.surname
        # Get the selected pickup and drop-off dates from the request parameters
        global pickup_date_str, dropoff_date_str

        pickup_date_str = request.args.get('pickup_date')
        dropoff_date_str = request.args.get('dropoff_date')
        # If pickup and drop-off dates are not provided, simply render the initial page
        if not pickup_date_str or not dropoff_date_str:
            today = date.today().strftime("%d/%m/%Y")
            return render_template("gold-class.html", today=today, vehicles=[], current_page=1, total_pages=0)

        # Parse the pickup and drop-off dates into datetime objects
        pickup_date = datetime.strptime(pickup_date_str, "%d/%m/%Y")
        dropoff_date = datetime.strptime(dropoff_date_str, "%d/%m/%Y")

        vehicles_to_remove = []  # Create an empty list to store the vehicles that need to be removed
        # Query Vehicle database to get only the vehicles with vehicle_class = "Gold" and vehicle_status = "ready"
        gold_vehicles = Vehicle.query.filter_by(vehicle_class="Gold", vehicle_status="ready").all()

        # Query RentedVehicle database to get only the vehicles with rental_status = "rented"
        rented_vehicles = RentedVehicle.query.filter_by(rental_status="rented").all()

        # Filter out the vehicles that are already rented for the selected dates
        for vehicle in gold_vehicles:
            if rented_vehicles:
                for rented_vehicle in rented_vehicles:
                    if rented_vehicle.vehicle_name == vehicle.name:
                        rent_from_date_str = rented_vehicle.rent_from_date
                        rent_until_date_str = rented_vehicle.rent_until_date

                        rent_from_date = datetime.strptime(rent_from_date_str, "%d/%m/%Y")
                        rent_until_date = datetime.strptime(rent_until_date_str, "%d/%m/%Y")

                        # Check if there's any overlap with the requested pickup and drop-off dates
                        if rent_from_date <= dropoff_date and rent_until_date >= pickup_date:
                            vehicles_to_remove.append(vehicle)  # Add the vehicle to the removal list
            else:
                break

        # Remove the vehicles that are not available from gold_vehicles
        for vehicle in vehicles_to_remove:
            gold_vehicles.remove(vehicle)

        # Get today's date
        today = date.today().strftime("%d/%m/%Y")
        # Get the total number of vehicles
        total_vehicles = len(gold_vehicles)
        # Get the current page number from the 'page' query parameter (defaults to 1)
        page = int(request.args.get('page', 1))
        # Set the number of vehicles to display per page
        vehicles_per_page = 5
        # Calculate the starting and ending indices for the current page
        start_idx = (page - 1) * vehicles_per_page
        end_idx = min(start_idx + vehicles_per_page, total_vehicles)

        # Calculate the total number of pages based on the total number of vehicles and vehicles_per_page
        total_pages = ceil(total_vehicles / vehicles_per_page)
        return render_template("gold-class.html", today=today, vehicles=gold_vehicles[start_idx:end_idx],
                               current_page=page, total_pages=total_pages, pickup_date=pickup_date_str,
                               dropoff_date=dropoff_date_str)

    else:
        return redirect('/')  # Redirect to the login page if the user is not logged in


@app.route('/check-out', methods=['GET', 'POST'])
def check_out():
    if 'user_id' in session:
        if session.get('booking_progress', 0) == 0:
            # Retrieve the data from the URL parameter
            pickup_date_str = request.args.get('pickup_date')
            dropoff_date_str = request.args.get('dropoff_date')
            vehicle_id = request.args.get('id')
            vehicle_name = request.args.get('vehicle')

            if not (pickup_date_str and dropoff_date_str and vehicle_id and vehicle_name):
                return redirect('/main-page')  # Redirect to the login page if the user is not logged in

            # Keeps the name and surname of the user in order to call for it
            user = User.query.get(session['user_id'])
            session['name'] = user.name
            session['surname'] = user.surname

            # Validate in case there's multiple vehicles with the same name
            selected_vehicle = Vehicle.query.filter_by(id=vehicle_id, name=vehicle_name).first()

            # When the user clicks the "Book Now" button, it triggers this if-clause
            if request.method == 'POST':
                # Create a new RentedVehicle entry in the database
                rented_vehicle = RentedVehicle(
                    vehicle_name=selected_vehicle.name,
                    rent_from_date=pickup_date_str,
                    rent_until_date=dropoff_date_str,
                    rental_status="rented"
                )
                db.session.add(rented_vehicle)
                db.session.commit()

                # Convert date strings to datetime objects
                pickup_date = datetime.strptime(pickup_date_str, "%d/%m/%Y")
                dropoff_date = datetime.strptime(dropoff_date_str, "%d/%m/%Y")

                # Calculate the total price
                delta = dropoff_date - pickup_date
                num_days = delta.days
                total_price = selected_vehicle.price_per_day * num_days

                # Add the total_price to the company balance
                company_balance = CompanyBalance.query.order_by(CompanyBalance.id.desc()).first()
                if company_balance:
                    company_balance_updated = company_balance.balance + total_price
                    # Create a new transaction entry in the database
                    transaction = CompanyBalance(
                        balance=company_balance_updated,
                        transaction_cost=total_price,
                        transaction_date=datetime.now().strftime("%Y-%m-%d")
                    )
                    db.session.add(transaction)
                    db.session.commit()

                return redirect(url_for("booking_confirmation", vehicle=vehicle_name, id=vehicle_id))

            return render_template("check-out.html", user=user, vehicle=selected_vehicle, pickup_date=pickup_date_str, dropoff_date=dropoff_date_str)
        else:
            return redirect('main-page')
    else:
        return redirect('/')  # Redirect to the login page if the user is not logged in


@app.route('/booking-confirmation', methods=['GET', 'POST'])
def booking_confirmation():
    # Check if the user is logged in by verifying the presence of the user_id in the session
    if 'user_id' in session:
        if session.get('booking_progress', 0) == 0:
            vehicle_id = request.args.get('id')
            vehicle_name = request.args.get('vehicle')

            if not (vehicle_id and vehicle_name):
                return redirect('/main-page')  # Redirect to the login page if the user is not logged in

            # Keep track of the user's progress
            session['booking_progress'] = 1

            # Keeps the name and surname of the user in order to call for it
            user = User.query.get(session['user_id'])
            session['name'] = user.name
            session['surname'] = user.surname

            # Retrieve the vehicle name from the URL parameter
            vehicle_id = request.args.get('id')
            vehicle_name = request.args.get('vehicle')
            selected_vehicle = Vehicle.query.filter_by(id=vehicle_id, name=vehicle_name).first()

            return render_template("booking-confirmation.html", user=user, vehicle=selected_vehicle)
        else:
            return redirect('/main-page')
    else:
        return redirect('/')  # Redirect to the login page if the user is not logged in


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()  # Clear the session to log out the user
    session['logout_success'] = 'You have successfully logged out.'
    return redirect('/')
