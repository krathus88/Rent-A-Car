# First Web App
This web app represents a significant milestone in my coding journey.

## Technologies Used
* __Frontend:__ I built the frontend of this web app using HTML, CSS, and JavaScript. It's designed to be responsive and user-friendly across various devices and screen sizes.

* __Backend:__ For the backend, I used Python and Flask, which allowed me to create a robust server to handle requests and interact with a database. I also created an App to allow admins to manage their fleet efficiently and get insight about the state of their vehicles.

* __Database:__ I chose SQL Lite as my database to store and manage data efficiently.

## Key Features of my Web App
Here are some of the key features of my web app:

* __User Authentication:__ Users can create accounts and log in securely.

* __Data Management:__ The app allows users to perform various CRUD (Create, Read, Update, Delete) operations on their data. Whether it's creating notes, managing tasks, or maintaining a list of favorite items, the app has got it covered.

* __Interactive UI:__ I put a lot of effort into creating an intuitive and visually pleasing user interface. The responsive design ensures a seamless experience on both desktop and mobile devices.

* __Real-time Updates:__ Users can expect real-time updates without having to refresh the page.

## Key Features of my Admin App
My admin app offers a range of powerful features designed to streamline fleet management and provide essential insights into company expenses. Here are some of the standout features:

### Fleet Management
* __Vehicle Registration:__ Admins have the capability to effortlessly register new vehicles into the fleet, ensuring a seamless addition process.

* __Vehicle Editing:__ The app enables admins to make necessary updates to vehicle details, ensuring that the fleet's information remains accurate and up to date.

* __Vehicle Deletion:__ When needed, administrators can easily remove vehicles from the fleet, simplifying fleet management.

* __Check-Up and VED Scheduling:__ Admins can schedule routine check-ups or Vehicle Excise Duty (VED) checks with ease, ensuring that vehicles are properly maintained and in compliance with regulations.

### Comprehensive Statistics
* __Expense Tracking:__ Admins have access to a comprehensive expense tracking system that provides insights into the company's financial health. This feature allows administrators to view expenses for the previous 12 months, aiding in informed decision-making.

### Intuitive and Visually Pleasing UI
* __User-Centric Design:__ The user interface has been meticulously crafted to be user-friendly, intuitive, and visually appealing, enhancing the overall user experience.

* __Visual Warnings:__ To ensure timely maintenance and compliance, the app employs visual cues with color identifications to notify admins of upcoming Check-UP and VED deadlines. This feature helps administrators stay proactive and organized.

## Getting Started
If you want to run the app locally for testing purposes, follow these steps:

1. Clone the repository:
###
    git clone https://github.com/krathus88/Rent-A-Car.git
<br/>

2. Install dependencies for both the frontend and backend:
###
    python -m venv ./venv
    cd venv
    .\Scripts\activate
    pip install flask==2.3.2
    pip install flask_bcrypt==1.0.1
    pip install flask_sqlalchemy==3.0.5
    pip install SQLAlchemy==2.0.18
    pip install tkcalendar==1.6.1
    pip install matplotlib==3.7.2
    pip install phonenumbers==8.13.18

3. Start the development server for both the frontend and backend:
###
    cd .\Rent-A-Car\
    python .\main.py
    
4. You can now access the web app locally in your browser at http://127.0.0.1:5000/.

## Things that I've learnt
During the development of my first web app, I acquired valuable skills and knowledge in various areas of web development. Here's a summary of what I've learned:
* __Creating Adaptive and Dynamic HTML Pages:__ I've gained proficiency in designing HTML pages that adapt gracefully to different screen sizes and devices. This involved implementing responsive design principles and utilizing CSS frameworks like Bootstrap.

* __User Authentication and Data Encryption:__ I've learnt how to create a secure user authentication system. This included encrypting user data to ensure the confidentiality and integrity of sensitive information.

* __Database Interaction:__ I've learnt how to interact with databases through SQL Lite. This encompassed both writing data to a database and retrieving information from it.

* __JavaScript for Enhanced Responsiveness:__ JavaScript became my go-to tool for enhancing the interactivity and responsiveness of my web app. I employed JavaScript to create dynamic user interfaces and add features that improve the user experience.

* __Debugging Proficiency:__ I developed strong debugging skills by utilizing various debugging tools, such as the Browser's Console and Python's Console. These tools helped me identify and resolve issues efficiently during the development process.

* __Handling Non-Idempotent Operations:__ I tackled the challenge of dealing with non-idempotent operations, ensuring that actions like form submissions and database updates were executed safely and predictably.

* __Database Design Choices:__ In this initial iteration of my web app, rather than using a single database with multiple tables, I've used more than one which led to difficulties managing them all.

## Conclusion
It's been an incredible learning experience. If you have any questions or comments, please feel free to reach out.
