from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
import csv
import io

app = Flask(__name__)
app.secret_key = "some_secret_key"  # Replace with your own secret key

# Load the database URL from the environment variable (set in Render)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --------------------------
# Database Models
# --------------------------

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    extension = db.Column(db.String(10), nullable=False)
    cell_phone = db.Column(db.String(20), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)

class Office(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    office_name = db.Column(db.String(100), nullable=False)
    direct_line = db.Column(db.String(20), nullable=False)
    physical_address = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

# --------------------------
# Public Routes
# --------------------------

@app.route("/")
def index():
    employees = Employee.query.all()
    offices = Office.query.all()
    return render_template("index.html", employees=employees, offices=offices)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files or request.files["file"].filename == "":
            flash("No file selected!")
            return redirect(request.url)
        
        file = request.files["file"]
        try:
            # Read and decode the CSV file (assumed UTF-8)
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.reader(stream)
            
            # Optionally, skip the header row if your CSV has headers
            headers = next(csv_input, None)
            
            for row in csv_input:
                if len(row) < 5:
                    continue  # Skip incomplete rows
                employee = Employee(
                    name=row[0].strip(),
                    extension=row[1].strip(),
                    cell_phone=row[2].strip(),
                    job_title=row[3].strip(),
                    location=row[4].strip()
                )
                db.session.add(employee)
            db.session.commit()
            flash("File uploaded and data imported successfully!")
        except Exception as e:
            flash(f"An error occurred: {str(e)}")
        return redirect(url_for("index"))
    
    return render_template("upload.html")

# --------------------------
# Admin Panel and Management Routes
# --------------------------

@app.route("/admin_panel")
def admin_panel():
    # Query all employees and offices to display in the admin panel.
    employees = Employee.query.all()
    offices = Office.query.all()
    
    # Optionally, check if the admin panel should load data for editing.
    employee_to_edit = None
    office_to_edit = None
    edit_employee_id = request.args.get("edit_employee_id")
    if edit_employee_id:
        employee_to_edit = Employee.query.get(edit_employee_id)
    edit_office_id = request.args.get("edit_office_id")
    if edit_office_id:
        office_to_edit = Office.query.get(edit_office_id)
    
    return render_template("admin.html",
                           employees=employees,
                           offices=offices,
                           employee_to_edit=employee_to_edit,
                           office_to_edit=office_to_edit)

@app.route("/save_employee", methods=["POST"])
def save_employee():
    # This route handles both adding a new employee and updating an existing one.
    employee_id = request.form.get("employee_id")
    name = request.form["name"]
    extension = request.form["extension"]
    cell_phone = request.form["cell_phone"]
    job_title = request.form["job_title"]
    location = request.form["location"]

    if employee_id and employee_id.strip():
        # Update existing employee.
        employee = Employee.query.get_or_404(employee_id)
        employee.name = name
        employee.extension = extension
        employee.cell_phone = cell_phone
        employee.job_title = job_title
        employee.location = location
    else:
        # Add new employee.
        employee = Employee(name=name,
                            extension=extension,
                            cell_phone=cell_phone,
                            job_title=job_title,
                            location=location)
        db.session.add(employee)
    db.session.commit()
    return redirect(url_for("admin_panel"))

@app.route("/delete_employee/<int:employee_id>", methods=["POST"])
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    db.session.delete(employee)
    db.session.commit()
    return redirect(url_for("admin_panel"))

@app.route("/save_office", methods=["POST"])
def save_office():
    # This route handles both adding a new office and updating an existing one.
    office_id = request.form.get("office_id")
    office_name = request.form["office_name"]
    direct_line = request.form["direct_line"]
    physical_address = request.form["physical_address"]

    if office_id and office_id.strip():
        office = Office.query.get_or_404(office_id)
        office.office_name = office_name
        office.direct_line = direct_line
        office.physical_address = physical_address
    else:
        office = Office(office_name=office_name,
                        direct_line=direct_line,
                        physical_address=physical_address)
        db.session.add(office)
    db.session.commit()
    return redirect(url_for("admin_panel"))

@app.route("/delete_office/<int:office_id>", methods=["POST"])
def delete_office(office_id):
    office = Office.query.get_or_404(office_id)
    db.session.delete(office)
    db.session.commit()
    return redirect(url_for("admin_panel"))

@app.route("/logout")
def logout():
    # Simple logout: clear session if you're using one, then redirect.
    # For now, just redirect to the public index.
    return redirect(url_for("index"))

# --------------------------
# (Optional) Public Add Employee Route
# --------------------------
# You may or may not need this if all adding/editing is done through the admin panel.
@app.route("/add_employee", methods=["POST"])
def public_add_employee():
    # This duplicate route can be renamed or removed if unnecessary.
    name = request.form["name"]
    extension = request.form["extension"]
    cell_phone = request.form["cell_phone"]
    job_title = request.form["job_title"]
    location = request.form["location"]

    new_employee = Employee(name=name,
                            extension=extension,
                            cell_phone=cell_phone,
                            job_title=job_title,
                            location=location)
    db.session.add(new_employee)
    db.session.commit()
    return redirect(url_for("index"))

# --------------------------
# Run the Application
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)
