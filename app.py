from tkinter import ttk, messagebox
from tkinter import *
from tkcalendar import DateEntry
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
import sqlite3
import re

# these are global variables used to store the respective radio button values
vehicle_class_value = "0"
gear_type_value = "0"
air_conditioning_value = "0"
vehicle_type_value = "0"


class Product:
    @staticmethod
    def db_query(query, parameters=(), fetchone=False, db='instance/vehicles.db'):
        with sqlite3.connect(db) as con:  # Iniciamos uma conexão com a base de dados (alias con)
            cursor = con.cursor()  # Criamos um cursor da conexão para poder operar na base de dados
            result = cursor.execute(query, parameters)  # Preparar a consulta SQL (com parâmetros se os há)
            con.commit()  # Executar a consulta SQL preparada anteriormente
            if fetchone:
                return result.fetchone()
            return result

    def __init__(self, root):
        self.window = root
        self.window.title("Vehicle Management")
        self.window.geometry("1000x400")
        self.window.resizable(FALSE, FALSE)
        self.window.wm_iconbitmap('static/icon.ico')

        self.edit_check = FALSE

        # General Top Frame
        top_frame = Frame()
        top_frame.pack(fill='x', side='top')

        # Top Left Frame
        top_left_frame = Frame(top_frame)
        top_left_frame.pack(side='left', padx=(10, 0), pady=(15, 0))
        # Register Button
        register_btn = ttk.Button(top_left_frame, text="Register Vehicle", command=self.register_vehicle)
        register_btn.grid(row=0, rowspan=2, column=0, ipady=33, ipadx=35)
        # Edit Button
        edit_btn = ttk.Button(top_left_frame, text="Edit Vehicle", command=self.edit_vehicle)
        edit_btn.grid(row=0, column=1, ipady=10, ipadx=35, sticky="w")
        # Delete Button
        delete_btn = ttk.Button(top_left_frame, text="Delete Vehicle", command=self.delete_vehicle)
        delete_btn.grid(row=1, column=1, ipady=10, ipadx=31, sticky="sw")

        # Top Right Frame
        top_right_frame = Frame(top_frame)
        top_right_frame.pack(side="right", padx=(0, 25), pady=(15, 0))
        # Statistics Button
        statistic_btn = ttk.Button(top_right_frame, text="Statistics", command=self.open_statistics)
        statistic_btn.grid(row=0, column=0, columnspan=2, ipadx=39, ipady=10)
        # Check-Up Button
        check_up_btn = ttk.Button(top_right_frame, text="Check-Up", command=self.check_up_vehicle)
        check_up_btn.grid(row=1, column=1, ipady=10, sticky="ne")
        # VED Button
        ved_btn = ttk.Button(top_right_frame, text="VED", command=self.ved_vehicle)
        ved_btn.grid(row=1, column=0, ipady=10, sticky="ne")

        # Top Center Frame
        top_center_frame = Frame(top_frame)
        top_center_frame.pack(side="top")
        # Create the header label
        header_label = Label(top_center_frame, text="CodeLab Solutions", font=("Helvetica", 25))
        header_label.grid(row=0, rowspan=2, padx=(10, 0))
        # Error label
        error_label = Label(top_center_frame)
        error_label.grid(row=2, padx=(10, 0), pady=(25, 0))
        self.error_label = error_label  # Store the error_label as an instance variable

        # Create the table
        table_frame = ttk.Frame()
        table_frame.pack(after=top_frame, padx=10, expand=True, fill='both')
        table_columns = (
            'ID', 'Name', 'Image File Name', 'Type', 'Num People', 'Num Doors', 'Luggage', 'Gear Type',
            'Air Conditioner', 'Price per Day', 'Vehicle Class', 'Next Check-Up', 'Next VED', 'Available in')
        self.table = ttk.Treeview(table_frame, columns=table_columns, show='headings')
        self.table.grid(row=0, column=0, pady=(10, 0), sticky=NSEW)
        # Set the size for each column independently
        self.column_widths = (40, 120, 150, 75, 75, 75, 75, 75, 100, 85, 85, 90, 90, 90, 90, 90)
        for idx, column in enumerate(table_columns):
            self.table.heading(column, text=column)
            self.table.column(column, width=self.column_widths[idx])
        # Set row and column weights to make the table expand with window resizing
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        # Create the vertical scrollbar
        self.y_scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=self.y_scrollbar.set)
        self.y_scrollbar.grid(row=0, column=1, sticky=NS)  # Use grid manager
        # Create the horizontal scrollbar
        self.x_scrollbar = ttk.Scrollbar(table_frame, orient=HORIZONTAL, command=self.table.xview)
        self.table.configure(xscrollcommand=self.x_scrollbar.set)
        self.x_scrollbar.grid(row=1, column=0, sticky=EW)  # Use grid manager

        # General Bottom Frame
        bottom_frame = Frame()
        bottom_frame.pack(after=table_frame, side="top", fill="x")

        # Bottom Left Frame
        bottom_left_frame = Frame(bottom_frame)
        bottom_left_frame.pack(side="left")
        # Balance Label
        self.balance_label = Label(bottom_left_frame, text="Current balance: N/A")
        self.balance_label.grid(row=0, column=0, padx=(5, 0), pady=(0, 5), sticky="w")

        # Bottom Right Frame
        bottom_right_frame = Frame(bottom_frame)
        bottom_right_frame.pack(side="right")
        # Information icon label
        info_table_colors_label = Label(bottom_right_frame, text="Table info", fg="blue", cursor="question_arrow")
        info_table_colors_label.grid(row=0, column=0, padx=(0, 10), pady=(0, 5), sticky="s")
        info_table_colors_label.bind("<Enter>", lambda event: self.show_tooltip(
            event,
            text=["Vehicle can't circulate.\nNeeds Check-Up or VED", "Check-Up ongoing", "Check-Up required soon",
                  "VED ongoing", "VED required soon"],
            colors=["#FA2700", "#EB951D", "#FAE0A7", "#1DD611", "#D0F5D7"]
        ))
        # Date Label
        date_label = Label(bottom_right_frame, text=date.today().strftime("%d/%m/%Y"))
        date_label.grid(row=0, column=1, padx=(0, 15), pady=(0, 5), sticky="e")

        # Initialize transaction cost attributes
        self.transaction_cost_car = None
        self.transaction_cost_motorbike = None

        self.update_error_label()
        self.calculate_balance()
        self.populate_table()
        self.tree_sorter = TreeviewSorter(self.table)

    def populate_table(self):
        # Remove existing rows from the table
        self.table.delete(*self.table.get_children())

        # Fetch data from the database and insert into the table
        query = "SELECT id, name, image_file_name, vehicle_type, num_people, num_doors, luggage, gear_type, air_conditioning, price_per_day, vehicle_class, next_check_up, next_ved, vehicle_available_again, vehicle_status, last_check_up, last_ved FROM vehicle"
        result = self.db_query(query)

        # Create a tag color for check-up
        self.table.tag_configure("not_ready", background="#FA2700")
        self.table.tag_configure("check_up_soon", background="#FAE0A7")
        self.table.tag_configure("check_up_occurring", background="#EB951D")
        self.table.tag_configure("ved_soon", background="#D0F5D7")
        self.table.tag_configure("ved_occurring", background="#1DD611")

        self.updated_rows_check_up = ()
        self.updated_rows_ved = ()
        self.updated_rows_not_ready = ()
        self.updated_rows_else = ()
        for row in result:
            vehicle_id = row[0] # Get the "id" value
            vehicle_status = row[-3]  # Get the "vehicle_status" value
            vehicle_available_again = row[-4] # Get the "vehicle_available_again" value
            next_ved_str = row[-5]  # Get the "next_ved" value
            next_check_up_str = row[-6]  # Get the "next_check_up" value
            today = date.today()
            next_check_up = datetime.strptime(next_check_up_str, "%d/%m/%Y").date()
            days_difference_check_up = (next_check_up - today).days
            next_ved = datetime.strptime(next_ved_str, "%d/%m/%Y").date()
            days_difference_ved = (next_ved - today).days

            # if vehicle is doing check-up, update the row
            if vehicle_status == "checkup":
                # if vehicle is done with check-up (meaning available date = today), update all relevant rows
                if vehicle_available_again == today.strftime("%d/%m/%Y"):
                    self.table.insert("", "end", values=row[:-2])
                    last_check_up_str = vehicle_available_again
                    last_check_up = datetime.strptime(last_check_up_str, "%d/%m/%Y").date()
                    next_check_up = last_check_up + timedelta(days=183)
                    next_check_up_str = next_check_up.strftime("%d/%m/%Y")
                    vehicle_available_again = "Now"
                    vehicle_status = "ready"
                    self.updated_rows_check_up += last_check_up_str, next_check_up_str, vehicle_available_again, vehicle_status, vehicle_id
                else:
                    self.table.insert("", "end", values=row[:-2], tags=("check_up_occurring",))
            # if <= 30 days until next check-up, update the row
            elif days_difference_check_up <= 30:
                if days_difference_check_up > 0:
                    self.table.insert("", "end", values=row[:-2], tags=("check_up_soon",))
                # if days_difference is negative then car isn't legal and can't circulate
                else:
                    self.table.insert("", "end", values=row[:-2], tags=("not_ready",))
                    if not vehicle_status == "not ready":
                        vehicle_available_again = "Unavailable"
                        vehicle_status = "not ready"
                        self.updated_rows_not_ready += vehicle_available_again, vehicle_status, vehicle_id
            # if vehicle is updating ved, update the row
            elif vehicle_status == "ved":
                # if vehicle is done with ved (meaning available date = today), update all relevant rows
                if vehicle_available_again == today.strftime("%d/%m/%Y"):
                    last_ved_str = vehicle_available_again
                    last_ved = datetime.strptime(last_ved_str, "%d/%m/%Y").date()
                    next_ved = last_ved + timedelta(days=365)
                    next_ved_str = next_ved.strftime("%d/%m/%Y")
                    vehicle_available_again = "Now"
                    vehicle_status = "ready"
                    self.updated_rows_ved += last_ved_str, next_ved_str, vehicle_available_again, vehicle_status, vehicle_id
                else:
                    self.table.insert("", "end", values=row[:-2], tags=("ved_occurring",))
            # if <= 30 days until next ved, update the row
            elif days_difference_ved <= 30:
                # if days_difference is positive then car is available
                if days_difference_ved > 0:
                    self.table.insert("", "end", values=row[:-2], tags=("ved_soon",))
                # if days_difference is negative then car isn't legal and can't circulate
                else:
                    self.table.insert("", "end", values=row[:-2], tags=("not_ready",))
                    if not vehicle_status == "not ready":
                        vehicle_available_again = "Unavailable"
                        vehicle_status = "not ready"
                        self.updated_rows_not_ready += vehicle_available_again, vehicle_status, vehicle_id
            # if vehicle isn't any of the above, update the row
            elif vehicle_status == "ready":
                self.table.insert("", "end", values=row[:-2])
            else:
                vehicle_status = "ready"
                self.updated_rows_else += vehicle_status, vehicle_id

        # After iterating through the result set, update the database with the collected changes
        self.update_database()
        self.update_error_label()

    def update_database(self):
        # Update the database with the changes in self.updated_rows
        if not self.updated_rows_check_up and not self.updated_rows_ved and not self.updated_rows_not_ready and not self.updated_rows_else:
            return  # No updates to perform
        elif self.updated_rows_check_up:
            update_query = "UPDATE vehicle SET last_check_up=?, next_check_up=?, vehicle_available_again=?, vehicle_status=? WHERE id=?"
            # Number of items to update
            batch_size = 5
            for i in range(0, len(self.updated_rows_check_up), batch_size):
                batch = self.updated_rows_check_up[i:i + batch_size]
                # Update the database with the current batch
                self.db_query(update_query, batch)
        elif self.updated_rows_ved:
            update_query = "UPDATE vehicle SET last_ved=?, next_ved=?, vehicle_available_again=?, vehicle_status=? WHERE id=?"
            # Number of items to update
            batch_size = 5
            for i in range(0, len(self.updated_rows_ved), batch_size):
                batch = self.updated_rows_ved[i:i + batch_size]
                # Update the database with the current batch
                self.db_query(update_query, batch)
        elif self.updated_rows_not_ready:
            update_query = "UPDATE vehicle SET vehicle_available_again=?, vehicle_status=? WHERE id=?"
            # Number of items to update
            batch_size = 3
            for i in range(0, len(self.updated_rows_not_ready), batch_size):
                batch = self.updated_rows_not_ready[i:i + batch_size]
                # Update the database with the current batch
                self.db_query(update_query, batch)
        elif self.updated_rows_else:
            update_query = "UPDATE vehicle SET vehicle_status=? WHERE id=?"
            # Number of items to update
            batch_size = 2
            for i in range(0, len(self.updated_rows_else), batch_size):
                batch = self.updated_rows_else[i:i + batch_size]
                # Update the database with the current batch
                self.db_query(update_query, batch)

        self.populate_table()

    def update_error_label(self):
        # Get the number of vehicles from vehicles.db
        num_vehicles_query = "SELECT COUNT(*) FROM vehicle WHERE vehicle_status = 'ready';"
        num_vehicles = self.db_query(num_vehicles_query, fetchone=True)[0]

        # Get the number of registered users from logins.db
        num_clients_query = "SELECT COUNT(*) FROM user"
        num_clients = self.db_query(num_clients_query, fetchone=True, db='instance/logins.db')[0]

        if num_vehicles < num_clients + 5:
            cars_needed = num_clients + 5 - num_vehicles
            self.error_label.config(text=f"You have {num_clients} clients so you need to buy {cars_needed} more cars.\nNeed to always have 5 more cars available than the number of clients.", fg="red")
        else:
            self.error_label.config(text="")

    def calculate_balance(self):
        # Fetch the balance from the database
        query = "SELECT * FROM balance WHERE id = (SELECT MAX(id) FROM balance)"
        result = self.db_query(query, fetchone=True, db='instance/company_balance.db')

        if self.transaction_cost_car:
            balance = result[1] + self.transaction_cost_car
            transaction_date = date.today()
            query = "INSERT INTO balance ('balance', 'transaction_cost', 'transaction_date') VALUES (?, ?, ?)"
            parameters = (balance, self.transaction_cost_car, transaction_date)
            self.db_query(query, parameters, db='instance/company_balance.db')
            self.transaction_cost_car = None
        elif self.transaction_cost_motorbike:
            balance = result[1] + self.transaction_cost_motorbike
            transaction_date = date.today()
            query = "INSERT INTO balance ('balance', 'transaction_cost', 'transaction_date') VALUES (?, ?, ?)"
            parameters = (balance, self.transaction_cost_motorbike, transaction_date)
            self.db_query(query, parameters, db='instance/company_balance.db')
            self.transaction_cost_motorbike = None
        else:
            balance = result[1]

        balance = round(balance, 2) # Round the balance to 2 decimal places before returning it
        self.balance_label.config(text=f"Current balance: {balance}")

    @staticmethod
    def show_tooltip(event, text, colors=None):
        # Create a new tooltip
        tooltip = Toplevel()
        tooltip.wm_overrideredirect(True)  # Remove window decorations

        if colors:
            tooltip_width = 135
            tooltip.wm_geometry("+{}+{}".format(event.x_root - tooltip_width - 10, event.y_root - 75))

            # Create a frame to hold the tooltip labels
            tooltip_frame = Frame(tooltip, relief=SOLID, borderwidth=1)
            tooltip_frame.pack()

            # Create the tooltip labels inside the frame
            for i in range(len(colors)):
                tooltip_label = Label(tooltip_frame, text=text[i], bg=colors[i], fg="black")
                tooltip_label.pack(fill="x", anchor="w")
        else:
            tooltip.wm_geometry(
                "+{}+{}".format(event.x_root + 10, event.y_root - 25))  # Position the tooltip next to the mouse cursor
            # Create a regular tooltip label
            tooltip_label = Label(tooltip, text=text)
            tooltip_label.pack(ipadx=5, ipady=2)

        # Bind the <Leave> event to hide_tooltip method for the tooltip window
        event.widget.bind("<Leave>", lambda event: tooltip.destroy())

    def register_vehicle(self):
        # This function creates a pop-up window when called
        self.popup = Toplevel(self.window)
        self.popup.title("Vehicle Registration")  # Title of the pop-up window
        self.popup.geometry("800x380")  # Set the size of the pop-up window
        self.popup.resizable(FALSE, FALSE)
        self.popup.wm_iconbitmap('static/icon.ico')

        # Grab the user's attention and disable interaction with the main window
        self.popup.grab_set()

        # Create the header label
        header_label = Label(self.popup, text="CodeLab Solutions", font=("Helvetica", 20))
        header_label.pack()  # Padding at the top of the window

        # Create a frame to hold the input fields
        input_frame = Frame(self.popup)
        input_frame.pack(pady=20)

        # Column 1
        # Name
        label1_name = Label(input_frame, text="Name:")
        label1_name.grid(row=0, column=0, padx=10, sticky="e")
        self.entry1_name = Entry(input_frame)
        self.entry1_name.grid(row=0, column=1, padx=10, pady=5)
        # Information icon label
        info_icon_label_name = Label(input_frame, text="i", fg="blue", cursor="question_arrow")
        info_icon_label_name.grid(row=0, column=1, pady=5, sticky="e")
        info_icon_label_name.bind("<Enter>", lambda event: self.show_tooltip(event, "Car's Model. Example: Opel Corsa D"))

        # Number of People
        label1_num_people = Label(input_frame, text="Number of People:")
        label1_num_people.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.entry1_num_people = Entry(input_frame)
        self.entry1_num_people.grid(row=1, column=1, padx=10, pady=5)
        # Information icon label
        info_icon_label_num_people = Label(input_frame, text="i", fg="blue", cursor="question_arrow")
        info_icon_label_num_people.grid(row=1, column=1, pady=5, sticky="e")
        info_icon_label_num_people.bind("<Enter>", lambda event: self.show_tooltip(event, "Must be an Integer. Example: 5"))

        # Number of Doors
        label1_num_doors = Label(input_frame, text="Number of Doors:")
        label1_num_doors.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.entry1_num_doors = Entry(input_frame)
        self.entry1_num_doors.grid(row=2, column=1, padx=10, pady=5)
        # Information icon label
        info_icon_label_num_doors = Label(input_frame, text="i", fg="blue", cursor="question_arrow")
        info_icon_label_num_doors.grid(row=2, column=1, pady=5, sticky="e")
        info_icon_label_num_doors.bind("<Enter>", lambda event: self.show_tooltip(event, "Must be an Integer. Example: 4"))

        # Luggage
        label1_luggage = Label(input_frame, text="Luggage:")
        label1_luggage.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.entry1_luggage = Entry(input_frame)
        self.entry1_luggage.grid(row=3, column=1, padx=10, pady=5)
        # Information icon label
        info_icon_label_luggage = Label(input_frame, text="i", fg="blue", cursor="question_arrow")
        info_icon_label_luggage.grid(row=3, column=1, pady=5, sticky="e")
        info_icon_label_luggage.bind("<Enter>", lambda event: self.show_tooltip(event, "Must be an Integer. Example: 1"))

        # Price per Day
        label1_price_per_day = Label(input_frame, text="Price per Day:")
        label1_price_per_day.grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.entry1_price_per_day = Entry(input_frame)
        self.entry1_price_per_day.grid(row=4, column=1, padx=10, pady=5)
        # Information icon label
        info_icon_label_price_per_day = Label(input_frame, text="i", fg="blue", cursor="question_arrow")
        info_icon_label_price_per_day.grid(row=4, column=1, pady=5, sticky="e")
        info_icon_label_price_per_day.bind("<Enter>", lambda event: self.show_tooltip(event, "Must be a Real Positive Number. Example: 32.19"))

        # Last Check-Up
        label1_last_check_up = Label(input_frame, text="Last Check-Up:")
        label1_last_check_up.grid(row=5, column=0, padx=10, pady=5, sticky="e")
        today = date.today()
        self.entry1_last_check_up = DateEntry(input_frame, date_pattern='dd/mm/yyyy', state='readonly', maxdate=today)
        self.entry1_last_check_up.grid(row=5, column=1, padx=10, pady=5, sticky="w")

        # Last VED
        label1_last_ved = Label(input_frame, text="Last VED:")
        label1_last_ved.grid(row=5, column=2, padx=10, pady=5, sticky="e")
        self.entry1_last_ved = DateEntry(input_frame, date_pattern='dd/mm/yyyy', state='readonly', maxdate=today)
        self.entry1_last_ved.grid(row=5, column=3, padx=10, pady=5, sticky="w")

        # Column 2
        # Image File Name
        label1_image_file_name = Label(input_frame, text="Image File Name:")
        label1_image_file_name.grid(row=0, column=2, padx=10, sticky="e")
        self.entry1_image_file_name = Entry(input_frame)
        self.entry1_image_file_name.grid(row=0, column=3, padx=10, columnspan=2, pady=5, sticky="ew")
        # Information icon label
        info_icon_label_image_file_name = Label(input_frame, text="i", fg="blue", cursor="question_arrow")
        info_icon_label_image_file_name.grid(row=0, column=5, pady=5, sticky="e")
        info_icon_label_image_file_name.bind("<Enter>", lambda event: self.show_tooltip(event, "Example format: car-image.jpg"))

        # Gear Type
        label1_gear_type = Label(input_frame, text="Gear Type:")
        label1_gear_type.grid(row=1, column=2, padx=10, pady=5, sticky="e")
        global gear_type_value
        gear_type_value = StringVar(value="0")  # workaround so the radio buttons aren't selected on mouseover
        self.radio_btn1_gear_type = Radiobutton(input_frame, text="Automatic", variable=gear_type_value, value="A")
        self.radio_btn1_gear_type.grid(row=1, column=3, pady=5, sticky="w")
        self.radio_btn3_gear_type = Radiobutton(input_frame, text="Manual", variable=gear_type_value, value="M")
        self.radio_btn3_gear_type.grid(row=1, column=3, columnspan=2, padx=84, pady=5, sticky="w")

        # Air Conditioner
        label1_air_conditioning = Label(input_frame, text="Air Conditioner:")
        label1_air_conditioning.grid(row=2, column=2, padx=10, pady=5, sticky="e")
        global air_conditioning_value
        air_conditioning_value = StringVar(value="0")  # workaround so the radio buttons aren't selected on mouseover
        self.radio_btn1_air_conditioning = Radiobutton(input_frame, text="A/C", variable=air_conditioning_value, value="A/C")
        self.radio_btn1_air_conditioning.grid(row=2, column=3, pady=5, sticky="w")
        self.radio_btn2_air_conditioning = Radiobutton(input_frame, text="No A/C", variable=air_conditioning_value, value="No A/C")
        self.radio_btn2_air_conditioning.grid(row=2, column=4, pady=5, sticky="w")

        # Vehicle Class
        label1_vehicle_class = Label(input_frame, text="Vehicle Class:")
        label1_vehicle_class.grid(row=3, column=2, padx=10, pady=5, sticky="e")
        global vehicle_class_value
        vehicle_class_value = StringVar(value="0")  # workaround so the radio buttons aren't selected on mouseover
        self.radio_btn1_vehicle_class = Radiobutton(input_frame, text="Economy", variable=vehicle_class_value, value="Economy")
        self.radio_btn1_vehicle_class.grid(row=3, column=3, pady=5, sticky="w")
        self.radio_btn2_vehicle_class = Radiobutton(input_frame, text="Silver", variable=vehicle_class_value, value="Silver")
        self.radio_btn2_vehicle_class.grid(row=3, column=4, pady=5, sticky="w")
        self.radio_btn3_vehicle_class = Radiobutton(input_frame, text="Gold", variable=vehicle_class_value, value="Gold")
        self.radio_btn3_vehicle_class.grid(row=3, column=4, padx=65, pady=5, sticky="e")

        # Vehicle Type
        label1_vehicle_type = Label(input_frame, text="Vehicle Type:")
        label1_vehicle_type.grid(row=4, column=2, padx=10, pady=5, sticky="e")
        global vehicle_type_value
        vehicle_type_value = StringVar(value="0")  # workaround so the radio buttons aren't selected on mouseover
        self.radio_btn1_vehicle_type = Radiobutton(input_frame, text="Car", variable=vehicle_type_value, value="Car")
        self.radio_btn1_vehicle_type.grid(row=4, column=3, pady=5, sticky="w")
        self.radio_btn2_vehicle_type = Radiobutton(input_frame, text="Motorbike", variable=vehicle_type_value, value="Motorbike")
        self.radio_btn2_vehicle_type.grid(row=4, column=4, pady=5, sticky="w")

        # Register Vehicle Button
        frame_btn_1 = Frame(self.popup)
        frame_btn_1.pack(after=input_frame, padx=0.5)  # Place the frame with relative coordinates
        register_btn = ttk.Button(frame_btn_1, text="Register", command=self.submit_data)
        register_btn.grid(ipady=15, ipadx=75)

    def edit_vehicle(self):
        selected_item = self.table.focus()  # Get the ID of the selected item
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a vehicle to edit.")
            return
        self.edit_check = TRUE

        # Extract the data from the selected item (row values)
        vehicle_id = self.table.item(selected_item, "values")[0]

        # Fetch the complete data for the selected vehicle from the database
        query = "SELECT * FROM vehicle WHERE id=?"
        result = self.db_query(query, (vehicle_id,))
        complete_vehicle_data = result.fetchone()
        id, name, image_file_name, vehicle_type, num_people, num_doors, luggage, gear_type, air_conditioner, price_per_day, vehicle_class, last_check_up, next_check_up, last_ved, next_ved, vehicle_available_again, vehicle_status = complete_vehicle_data

        # Store the selected vehicle ID as a class attribute to be used later in submit_data
        self.selected_vehicle_id = id

        # Convert the fetched dates to Python date objects
        last_check_up_date = datetime.strptime(last_check_up, "%d/%m/%Y").date()
        last_ved_date = datetime.strptime(last_ved, "%d/%m/%Y").date()

        # This function creates a pop-up window when called
        self.popup = Toplevel(self.window)
        self.popup.title("Vehicle Editing")
        self.popup.geometry("550x535")
        self.popup.resizable(FALSE, FALSE)
        self.popup.wm_iconbitmap('static/icon.ico')

        # Grab the user's attention and disable interaction with the main window
        self.popup.grab_set()

        # Create the header label
        header_label = Label(self.popup, text="CodeLab Solutions", font=("Helvetica", 20))
        header_label.pack()  # Padding at the top of the window

        # Create a frame to hold the input fields
        input_frame = Frame(self.popup)
        input_frame.pack(pady=20)

        # Name
        label1_name = Label(input_frame, text="Name:")
        label1_name.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.entry1_name = Entry(input_frame)
        self.entry1_name.grid(row=0, column=1, padx=10, pady=5)
        self.entry1_name.insert(0, name)
        self.entry1_name.config(state="readonly")
        self.entry2_name = Entry(input_frame)
        self.entry2_name.grid(row=0, column=2, padx=10, pady=5)
        # Information icon label
        info_icon_label_name = Label(input_frame, text="i", fg="blue", cursor="question_arrow")
        info_icon_label_name.grid(row=0, column=2, pady=5, sticky="e")
        info_icon_label_name.bind("<Enter>", lambda event: self.show_tooltip(event, "Car's Model. Example: Opel Corsa D"))

        # Number of People
        label1_num_people = Label(input_frame, text="Number of People:")
        label1_num_people.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.entry1_num_people = Entry(input_frame)
        self.entry1_num_people.grid(row=1, column=1, padx=10, pady=5)
        self.entry1_num_people.insert(0, num_people)
        self.entry1_num_people.config(state="readonly")
        self.entry2_num_people = Entry(input_frame)
        self.entry2_num_people.grid(row=1, column=2, padx=10, pady=5)
        # Information icon label
        info_icon_label_num_people = Label(input_frame, text="i", fg="blue", cursor="question_arrow")
        info_icon_label_num_people.grid(row=1, column=2, pady=5, sticky="e")
        info_icon_label_num_people.bind("<Enter>", lambda event: self.show_tooltip(event, "Must be an Integer. Example: 5"))

        # Number of Doors
        label1_num_doors = Label(input_frame, text="Number of Doors:")
        label1_num_doors.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.entry1_num_doors = Entry(input_frame)
        self.entry1_num_doors.grid(row=2, column=1, padx=10, pady=5)
        self.entry1_num_doors.insert(0, num_doors)
        self.entry1_num_doors.config(state="readonly")
        self.entry2_num_doors = Entry(input_frame)
        self.entry2_num_doors.grid(row=2, column=2, padx=10, pady=5)
        # Information icon label
        info_icon_label_num_doors = Label(input_frame, text="i", fg="blue", cursor="question_arrow")
        info_icon_label_num_doors.grid(row=2, column=2, pady=5, sticky="e")
        info_icon_label_num_doors.bind("<Enter>", lambda event: self.show_tooltip(event, "Must be an Integer. Example: 4"))

        # Luggage
        label1_luggage = Label(input_frame, text="Luggage:")
        label1_luggage.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.entry1_luggage = Entry(input_frame)
        self.entry1_luggage.grid(row=3, column=1, padx=10, pady=5)
        self.entry1_luggage.insert(0, luggage)
        self.entry1_luggage.config(state="readonly")
        self.entry2_luggage = Entry(input_frame)
        self.entry2_luggage.grid(row=3, column=2, padx=10, pady=5)
        # Information icon label
        info_icon_label_luggage = Label(input_frame, text="i", fg="blue", cursor="question_arrow")
        info_icon_label_luggage.grid(row=3, column=2, pady=5, sticky="e")
        info_icon_label_luggage.bind("<Enter>", lambda event: self.show_tooltip(event, "Must be an Integer. Example: 1"))

        # Price per Day
        label1_price_per_day = Label(input_frame, text="Price per Day:")
        label1_price_per_day.grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.entry1_price_per_day = Entry(input_frame)
        self.entry1_price_per_day.grid(row=4, column=1, padx=10, pady=5)
        self.entry1_price_per_day.insert(0, price_per_day)
        self.entry1_price_per_day.config(state="readonly")
        self.entry2_price_per_day = Entry(input_frame)
        self.entry2_price_per_day.grid(row=4, column=2, padx=10, pady=5)
        # Information icon label
        info_icon_label_price_per_day = Label(input_frame, text="i", fg="blue", cursor="question_arrow")
        info_icon_label_price_per_day.grid(row=4, column=2, pady=5, sticky="e")
        info_icon_label_price_per_day.bind("<Enter>", lambda event: self.show_tooltip(event, "Must be a Real Positive Number. Example: 32.19"))

        # Image File Name
        label1_image_file_name = Label(input_frame, text="Image File Name:")
        label1_image_file_name.grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.entry1_image_file_name = Entry(input_frame)
        self.entry1_image_file_name.grid(row=5, column=1, padx=10, pady=5)
        self.entry1_image_file_name.insert(0, image_file_name)
        self.entry1_image_file_name.config(state="readonly")
        self.entry2_image_file_name = Entry(input_frame)
        self.entry2_image_file_name.grid(row=5, column=2, padx=10, pady=5)
        # Information icon label
        info_icon_label_image_file_name = Label(input_frame, text="i", fg="blue", cursor="question_arrow")
        info_icon_label_image_file_name.grid(row=5, column=2, pady=5, sticky="e")
        info_icon_label_image_file_name.bind("<Enter>", lambda event: self.show_tooltip(event, "Example format: car-image.jpg"))

        # Gear Type
        label1_image_file_name = Label(input_frame, text="Gear Type:")
        label1_image_file_name.grid(row=6, column=0, padx=10, pady=5, sticky="e")
        global gear_type_value
        gear_type_value = StringVar(value=gear_type)
        self.radio_btn1_image_file_name = Radiobutton(input_frame, text="Automatic", variable=gear_type_value, value="A")
        self.radio_btn1_image_file_name.grid(row=6, column=1, pady=5, sticky="w")
        self.radio_btn3_image_file_name = Radiobutton(input_frame, text="Manual", variable=gear_type_value, value="M")
        self.radio_btn3_image_file_name.grid(row=6, column=1, columnspan=2, padx=84, pady=5, sticky="w")

        # Air Conditioner
        label1_air_conditioning = Label(input_frame, text="Air Conditioner:")
        label1_air_conditioning.grid(row=7, column=0, padx=10, pady=5, sticky="e")
        global air_conditioning_value
        air_conditioning_value = StringVar(value=air_conditioner)
        self.radio_btn1_air_conditioning = Radiobutton(input_frame, text="A/C", variable=air_conditioning_value, value="A/C")
        self.radio_btn1_air_conditioning.grid(row=7, column=1, pady=5, sticky="w")
        self.radio_btn2_air_conditioning = Radiobutton(input_frame, text="No A/C", variable=air_conditioning_value, value="No A/C")
        self.radio_btn2_air_conditioning.grid(row=7, column=1, padx=20, pady=5, sticky="e")

        # Vehicle Class
        label1_vehicle_class = Label(input_frame, text="Vehicle Class:")
        label1_vehicle_class.grid(row=8, column=0, padx=10, pady=5, sticky="e")
        global vehicle_class_value
        vehicle_class_value = StringVar(value=vehicle_class)
        self.radio_btn1_vehicle_class = Radiobutton(input_frame, text="Economy", variable=vehicle_class_value, value="Economy")
        self.radio_btn1_vehicle_class.grid(row=8, column=1, pady=5, sticky="w")
        self.radio_btn2_vehicle_class = Radiobutton(input_frame, text="Silver", variable=vehicle_class_value, value="Silver")
        self.radio_btn2_vehicle_class.grid(row=8, column=1, padx=5, pady=5, sticky="e")
        self.radio_btn3_vehicle_class = Radiobutton(input_frame, text="Gold", variable=vehicle_class_value, value="Gold")
        self.radio_btn3_vehicle_class.grid(row=8, column=2, pady=5, sticky="w")

        # Vehicle Type
        label1_vehicle_type = Label(input_frame, text="Vehicle Type:")
        label1_vehicle_type.grid(row=9, column=0, padx=10, pady=5, sticky="e")
        global vehicle_type_value
        vehicle_type_value = StringVar(value=vehicle_type)
        self.radio_btn1_vehicle_type = Radiobutton(input_frame, text="Car", variable=vehicle_type_value, value="Car")
        self.radio_btn1_vehicle_type.grid(row=9, column=1, pady=5, sticky="w")
        self.radio_btn2_vehicle_type = Radiobutton(input_frame, text="Motorbike", variable=vehicle_type_value, value="Motorbike")
        self.radio_btn2_vehicle_type.grid(row=9, column=1, padx=10, pady=5, sticky="e")

        # Last Check-Up
        label1_last_check_up = Label(input_frame, text="Last Check-Up:")
        label1_last_check_up.grid(row=11, column=0, padx=10, pady=5, sticky="e")
        today = date.today()
        self.entry1_last_check_up = DateEntry(input_frame, date_pattern='dd/mm/yyyy', state='readonly', maxdate=today)
        self.entry1_last_check_up.grid(row=11, column=1, pady=5, sticky="w")
        # Set the pre-selected date for the Last Check-Up field
        self.entry1_last_check_up.set_date(last_check_up_date)

        # Last VED
        label1_last_ved = Label(input_frame, text="Last VED:")
        label1_last_ved.grid(row=11, column=1, columnspan=2, padx=110, pady=5, sticky="w")
        self.entry1_last_ved = DateEntry(input_frame, date_pattern='dd/mm/yyyy', state='readonly', maxdate=today)
        self.entry1_last_ved.grid(row=11, column=2, padx=30, pady=5, sticky="e")
        # Set the pre-selected date for the Last VED field
        self.entry1_last_ved.set_date(last_ved_date)

        # Edit Vehicle Button
        frame_btn_1 = Frame(self.popup)
        frame_btn_1.pack(after=input_frame, padx=0.5)  # Place the frame with relative coordinates
        register_btn = ttk.Button(frame_btn_1, text="Edit", command=self.submit_data)
        register_btn.grid(ipady=15, ipadx=75)

    def delete_vehicle(self):
        selected_item = self.table.focus()  # Get the ID of the selected item
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a vehicle to delete.")
            return

        # Get the Vehicle ID and Name from the selected item
        vehicle_id = self.table.item(selected_item, "values")[0]
        vehicle_name = self.table.item(selected_item, "values")[1]

        confirmation = messagebox.askyesno("Delete Vehicle", f"Are you sure you want to delete this vehicle?\nID: {vehicle_id} | {vehicle_name}")
        if confirmation:
            vehicle_id = self.table.item(selected_item, "values")[0]  # Get the ID from the selected item
            query = "DELETE FROM vehicle WHERE ID = ?"
            self.db_query(query, (vehicle_id,))

            # Update the table to reflect the deletion
            self.populate_table()

    def open_statistics(self):
        # Calculate the date for 12 months ago from today
        twelve_months_ago = (datetime.now() - timedelta(days=365)).replace(day=1).strftime('%Y-%m-%d')
        # Calculate the first day of the next month
        next_month_first_day = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1)
        # Collect data from the database and group by month and year for the last 12 months
        query = f"""
                SELECT strftime('%Y-%m', transaction_date) AS month_year, SUM(transaction_cost)
                FROM balance
                WHERE transaction_date >= ? AND transaction_date < ?
                GROUP BY month_year
                ORDER BY month_year
                """
        result = self.db_query(query, (twelve_months_ago, next_month_first_day), db='instance/company_balance.db')

        # Process the data to create a dictionary of values
        data_dict = {}
        for row in result:
            month_year, transaction_cost = row
            data_dict[month_year] = transaction_cost
        # Check if there is data to display
        if not data_dict:
            messagebox.showinfo("Warning", "No data to show.")
            return

        # Generate the labels (month and year) for the last 12 months
        labels = []
        current_date = datetime.now().replace(day=1)
        for _ in range(12):
            labels.append(current_date.strftime('%Y-%m'))
            current_date -= timedelta(days=1)
            current_date = current_date.replace(day=1)
        # Ensure that the labels are in the correct order
        labels = list(reversed(labels))
        # Create a list of values based on the labels
        values = [data_dict.get(label, 0) for label in labels]
        # Create a bar chart with different colors for positive and negative values
        colors = ['green' if value >= 0 else 'red' for value in values]

        plt.figure(num='Company Revenue Statistics')
        self.window.iconbitmap(default='static/icon.ico')
        plt.bar(labels, values, color=colors)
        plt.ylabel('Company Revenue')
        plt.title('Company Revenue for each month of the previous 12 months.')
        plt.axhline(0, color='grey', linestyle='-', linewidth=1)  # Add a horizontal line at y=0
        plt.xticks(rotation=45, ha="right", fontsize=8)

        plt.tight_layout()
        plt.show()

    def check_up_vehicle(self):
        selected_item = self.table.focus()  # Get the ID of the selected item
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a vehicle to do a regular check-up.")
            return

        # Get the ID of the selected item from the first column (ID)
        vehicle_id = self.table.item(selected_item, "values")[0]
        next_check_up_str = self.table.item(selected_item, "values")[11]

        # Get the current date and calculate the date after 30 days
        today = date.today()
        check_up_release_date = today + timedelta(days=30)
        check_up_release_date = check_up_release_date.strftime("%d/%m/%Y")
        vehicle_available = "checkup"
        next_check_up = datetime.strptime(next_check_up_str, "%d/%m/%Y").date()
        days_difference_check_up = (next_check_up - today).days

        # if it's time to do a regular check_up
        if days_difference_check_up <= 30:
            # Update "Available in" column in the table with the calculated date and vehicle_status from the database
            update_query = "UPDATE vehicle SET vehicle_available_again=?, vehicle_status=? WHERE ID = ?"
            parameters = (check_up_release_date, vehicle_available, vehicle_id)
            self.db_query(update_query, parameters)
            messagebox.showinfo("Success", "Check-up routine initiated successfully! Available date updated.")
            self.populate_table()  # Refresh the table with the updated data
        # if it's not time to do a regular check_up
        else:
            messagebox.showwarning("Warning", "It is yet not time to do a regular check-up.")

    def ved_vehicle(self):
        selected_item = self.table.focus()  # Get the ID of the selected item
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a vehicle to do a regular check-up.")
            return

        # Get the ID of the selected item from the first column (ID)
        vehicle_id = self.table.item(selected_item, "values")[0]
        next_ved_str = self.table.item(selected_item, "values")[12]
        vehicle_type = self.table.item(selected_item, "values")[3]

        # Get the current date and calculate the date after 1 day
        today = date.today()
        ved_release_date = today + timedelta(days=1)
        ved_release_date = ved_release_date.strftime("%d/%m/%Y")
        vehicle_available = "ved"
        next_ved = datetime.strptime(next_ved_str, "%d/%m/%Y").date()
        days_difference_ved = (next_ved - today).days

        if days_difference_ved <= 30:
            # Update "Available in" column in the table with the calculated date and vehicle_status from the database
            update_query = "UPDATE vehicle SET vehicle_available_again=?, vehicle_status=? WHERE ID = ?"
            parameters = (ved_release_date, vehicle_available, vehicle_id)
            self.db_query(update_query, parameters)
            if vehicle_type == "Car":
                self.transaction_cost_car = -250
                messagebox.showinfo("Success", "VED submitted successfully! Available date updated and 250€ was deducted from your balance.")
            elif vehicle_type == "Motorbike":
                self.transaction_cost_motorbike = -150
                messagebox.showinfo("Success", "VED submitted successfully! Available date updated and 150€ was deducted from your balance.")
            self.calculate_balance()
            self.populate_table()  # Refresh the table with the updated data
        else:
            messagebox.showwarning("Warning", "It is yet not time to renew VED.")

    def submit_data(self):
        # If editing an entry
        if self.edit_check:
            name = self.entry2_name.get().title()
            num_people_str = self.entry2_num_people.get()
            num_doors_str = self.entry2_num_doors.get()
            luggage_str = self.entry2_luggage.get()
            price_per_day_str = self.entry2_price_per_day.get()
            image_file_name = self.entry2_image_file_name.get()
            last_check_up = self.entry1_last_check_up.get()
            last_ved = self.entry1_last_ved.get()
            gear_type = gear_type_value.get()
            air_conditioner = air_conditioning_value.get()
            vehicle_class = vehicle_class_value.get()
            vehicle_type = vehicle_type_value.get()

            # Get the ID of the selected vehicle from the class attribute
            vehicle_id = self.selected_vehicle_id

            # Extract the original data from entry1
            original_name = self.entry1_name.get().title()
            original_num_people_str = self.entry1_num_people.get()
            original_num_doors_str = self.entry1_num_doors.get()
            original_luggage_str = self.entry1_luggage.get()
            original_price_per_day_str = self.entry1_price_per_day.get()
            original_image_file_name = self.entry1_image_file_name.get()

            # Check if the values have changed for each field
            if name == "":
                name = original_name  # Set to None to indicate no update needed
            if num_people_str == "":
                num_people_str = original_num_people_str
            if num_doors_str == "":
                num_doors_str = original_num_doors_str
            if luggage_str == "":
                luggage_str = original_luggage_str
            if price_per_day_str == "":
                price_per_day_str = original_price_per_day_str
            if image_file_name == "":
                image_file_name = original_image_file_name
        # If registering a new entry
        else:
            # Extract the data from the input fields
            name = self.entry1_name.get().title()  # capitalize the first letter of each noun
            num_people_str = self.entry1_num_people.get()
            num_doors_str = self.entry1_num_doors.get()
            luggage_str = self.entry1_luggage.get()
            price_per_day_str = self.entry1_price_per_day.get()
            image_file_name = self.entry1_image_file_name.get()
            last_check_up = self.entry1_last_check_up.get()
            last_ved = self.entry1_last_ved.get()
            gear_type = gear_type_value.get()
            air_conditioner = air_conditioning_value.get()
            vehicle_class = vehicle_class_value.get()
            vehicle_type = vehicle_type_value.get()
            vehicle_available_again = "Now"
            vehicle_status = "ready"

        # Validate price_per_day format and convert if necessary
        if "," in price_per_day_str and "." in price_per_day_str:
            messagebox.showerror("Error", "Price per Day can't contain both a comma and a period.")
            return
        elif "," in price_per_day_str:
            if price_per_day_str.count(",") > 1:
                messagebox.showerror("Error", "Price per Day can't contain more than one comma.")
                return
            price_per_day_str = price_per_day_str.replace(",", ".")
            if len(price_per_day_str.split(".")[-1]) > 2:
                messagebox.showerror("Error", "Price per Day can only have a maximum of two decimal places.")
                return
        elif "." in price_per_day_str:
            if price_per_day_str.count(".") > 1:
                messagebox.showerror("Error", "Price per Day can't contain more than one period.")
                return
            if len(price_per_day_str.split(".")[-1]) > 2:
                messagebox.showerror("Error", "Price per Day can only have a maximum of two decimal places.")
                return

        # Validate num_people as a positive integer
        try:
            num_people = int(num_people_str)
            if num_people <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Number of People must be a positive number.")
            return

        # Validate num_doors as a positive integer
        try:
            num_doors = int(num_doors_str)
            if num_doors <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Number of doors must be a positive number.")
            return

        # Validate luggage as a positive integer or 0
        try:
            luggage = int(luggage_str)
            if luggage < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Luggage must be a positive number or 0.")
            return

        # Validate price_per_day as a positive float
        try:
            price_per_day = float(price_per_day_str)
            if price_per_day <= 0:
                messagebox.showerror("Error", "Price per Day must be a positive number.")
                return
        except ValueError:
            messagebox.showerror("Error", "Price per Day must be a number.")
            return

        # Check if any of the fields is empty
        if not all([name, num_people_str, num_doors_str, luggage_str, price_per_day_str, image_file_name, last_check_up, last_ved]) or gear_type == "0" or air_conditioner == "0" or vehicle_class == "0" or vehicle_type == "0":
            messagebox.showerror("Error", "All fields are required to register a vehicle.")
            return

        # from image_file_name: Unify line spaces with "-" and delete extra line spaces at the end
        image_file_name = re.sub(r'\s+', '-', image_file_name).replace("\r", "")
        image_file_name = image_file_name.rstrip('-')
        image_file_name.lower()
        # Check if image_file_name ends with ".jpg" or ".png" and add it if not
        if not image_file_name.endswith((".jpg", ".png")):
            image_file_name += ".jpg"

        last_ved_date = datetime.strptime(last_ved, "%d/%m/%Y")
        last_check_up_date = datetime.strptime(last_check_up, "%d/%m/%Y")

        # Calculate next_check_up and next_ved by adding one year to last_check_up_date and last_ved_date
        next_check_up_date = last_check_up_date + timedelta(days=183)
        next_ved_date = last_ved_date + timedelta(days=365)

        # Convert next_check_up_date and next_ved_date back to string format "dd/mm/yyyy"
        next_check_up = next_check_up_date.strftime("%d/%m/%Y")
        next_ved = next_ved_date.strftime("%d/%m/%Y")

        if self.edit_check:
            # Update the data in the database
            query = "UPDATE vehicle SET name=?, image_file_name=?, vehicle_type=?, num_people=?, num_doors=?, luggage=?, gear_type=?, air_conditioning=?, price_per_day=?, vehicle_class=?, last_check_up=?, next_check_up=?, last_ved=?, next_ved=? WHERE id=?"
            parameters = (name, image_file_name, vehicle_type, num_people_str, num_doors_str, luggage_str, gear_type, air_conditioner, price_per_day, vehicle_class, last_check_up, next_check_up, last_ved, next_ved, vehicle_id)
            self.db_query(query, parameters)
            self.edit_check = FALSE
        else:
            # Register new data into the database
            query = "INSERT INTO vehicle ('name', 'image_file_name', 'vehicle_type', 'num_people', 'num_doors', luggage, 'gear_type', 'air_conditioning', 'price_per_day', 'vehicle_class', 'last_check_up', 'next_check_up', 'last_ved', 'next_ved', 'vehicle_available_again', 'vehicle_status') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            parameters = (name, image_file_name, vehicle_type, num_people_str, num_doors_str, luggage_str, gear_type, air_conditioner, price_per_day, vehicle_class, last_check_up, next_check_up, last_ved, next_ved, vehicle_available_again, vehicle_status)
            self.db_query(query, parameters)

        # Update the table to reflect the new data
        self.populate_table()

        # Close the popup window
        self.popup.destroy()


class TreeviewSorter:
    def __init__(self, tree):
        self.tree = tree
        self.column_dict = {}
        for col in self.tree['columns']:
            self.column_dict[col] = False
            self.tree.heading(col, text=col, command=lambda c=col: self.sort(c, False))

    def sort(self, col, reverse):
        data = [(self.get_sort_key(self.tree.set(child, col)), child) for child in self.tree.get_children('')]
        data.sort(reverse=reverse)

        for index, item in enumerate(data):
            self.tree.move(item[1], '', index)

        self.column_dict[col] = not reverse
        self.tree.heading(col, command=lambda c=col: self.sort(c, not reverse))

    @staticmethod
    def get_sort_key(value):
        try:
            # Try converting the value to an integer if possible
            return int(value)
        except ValueError:
            # If it's not an integer, return the value as is (for alphabetical sorting)
            return value
