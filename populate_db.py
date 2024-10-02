# populate_db.py

from app import create_app, db
from app.models import Employee, Admin
from werkzeug.security import generate_password_hash
import sys

app = create_app()

with app.app_context():
    # Remove db.drop_all() to preserve existing data
    # db.drop_all()
    
    # Ensure all tables are created (if not using Flask-Migrate)
    db.create_all()

    # Insert Existing Employees
    employee_usernames = [
        'rashida', 'fahima', 'divya', 'noufiya', 'himaja', 'hafsa', 'anusha',
        'krishnendhu', 'nisha_v', 'shajna', 'reshma', 'shadeeda', 'nisha_c',
        'farhath', 'shamla', 'priya_pillai', 'sumayya', 'mufeeda', 'sandra',
        'greeshma', 'elizabeth', 'lubna', 'nisha_hr', 'shafeela'
    ]

    for username in employee_usernames:
        existing_employee = Employee.query.filter_by(username=username).first()
        if existing_employee:
            print(f"Employee {username} already exists. Skipping.")
            continue
        employee = Employee(username=username)
        employee.set_password('Elite@123')
        db.session.add(employee)
        print(f"Added employee: {username}")

    # Insert 100 New Employees with Employee Codes ER1050 to ER1149
    starting_code = 1050
    num_new_employees = 100
    new_employee_usernames = [f'ER{code}' for code in range(starting_code, starting_code + num_new_employees)]

    for username in new_employee_usernames:
        existing_employee = Employee.query.filter_by(username=username).first()
        if existing_employee:
            print(f"Employee {username} already exists. Skipping.")
            continue
        employee = Employee(username=username)
        employee.set_password('Elite@123')  # Common password for all new employees
        db.session.add(employee)
        print(f"Added employee: {username}")

    # Insert Admins (only if they don't already exist)
    admins = [
        {'username': 'amir@eliteresumes.in', 'password': 'Elite@123456'},
        {'username': 'suhaib@eliteresumes.in', 'password': 'Elite@123456'},
        {'username': 'rashida@eliteresumes.in', 'password': 'Elite@123456'}
    ]

    for admin_data in admins:
        existing_admin = Admin.query.filter_by(username=admin_data['username']).first()
        if existing_admin:
            print(f"Admin {admin_data['username']} already exists. Skipping.")
            continue
        admin = Admin(username=admin_data['username'])
        admin.set_password(admin_data['password'])
        db.session.add(admin)
        print(f"Added admin: {admin_data['username']}")

    # Commit all changes to the database
    try:
        db.session.commit()
        print("Database populated successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred while populating the database: {e}")
        sys.exit(1)
