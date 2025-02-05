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

# Define the Employee model (data for the phone list)
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    extension = db.Column(db.String(10), nullable=False)
    cell_phone = db.Column(db.String(20), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)

# Define the Office model (office location data)
class Office(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    office_name = db.Column(db.String(100), nullable=False)
    direct_line = db.Column(db.String(20), nullable=False)
    physical_address = db.Column(db.String(200), nullable=False)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Main public view: display phone list and office locations
@app.route("/")
def index():
    employees = Employee.query.all()
    offices = Office.query.all()
    return render_template("index.html", employees=employees, offices=offices)

# Add a new employee (from public form, if any)
@app.route("/add_employee", methods=["POST"])
def add_employee():
    name = request.form["name"]
    extension = request.form["extension"]
    cell_phone = request.form["cell_phone"]
    job_title = request.form["job_title"]
    location = request.form["location"]

    new_employee = Employee(
        name=name, 
        extension=extension, 
        cell_phone=cell_phone, 
        job_title=job_title, 
        location=location
    )
    db.session.add(new_employee)
    db.session.commit()

    return redirect(url_for("index"))

# Upload employees via CSV (each row: name, extension, cell_phone, job_title, location)
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files or request.files["file"].filename == "":
            flash("No file selected!")
            return redirect(request.url)
        
        file = request.files["file"]
        try:
            # Read and decode the CSV file (UTF-8 encoding assumed)
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.reader(stream)
            
            # Optionally skip the header row if your CSV has headers
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

# Admin panel to manage data (renders admin.html)
@app.route("/admin_panel")
def admin_panel():
    employees = Employee.query.all()
    offices = Office.query.all()
    return render_template("admin.html", employees=employees, offices=offices)

# ----- Employee Edit/Delete Endpoints -----

@app.route("/edit_employee/<int:employee_id>", methods=["GET", "POST"])
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    if request.method == "POST":
        employee.name = request.form["name"]
        employee.extension = request.form["extension"]
        employee.cell_phone = request.form["cell_phone"]
        employee.job_title = request.form["job_title"]
        employee.location = request.form["location"]
        db.session.commit()
        return redirect(url_for("admin_panel"))
    return render_template("edit_employee.html", employee=employee)

@app.route("/delete_employee/<int:employee_id>", methods=["POST"])
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    db.session.delete(employee)
    db.session.commit()
    return redirect(url_for("admin_panel"))

# ----- Office Edit/Delete Endpoints -----

@app.route("/add_office", methods=["POST"])
def add_office():
    office_name = request.form["office_name"]
    direct_line = request.form["direct_line"]
    physical_address = request.form["physical_address"]

    new_office = Office(
        office_name=office_name,
        direct_line=direct_line,
        physical_address=physical_address
    )
    db.session.add(new_office)
    db.session.commit()
    return redirect(url_for("admin_panel"))

@app.route("/edit_office/<int:office_id>", methods=["GET", "POST"])
def edit_office(office_id):
    office = Office.query.get_or_404(office_id)
    if request.method == "POST":
        office.office_name = request.form["office_name"]
        office.direct_line = request.form["direct_line"]
        office.physical_address = request.form["physical_address"]
        db.session.commit()
        return redirect(url_for("admin_panel"))
    return render_template("edit_office.html", office=office)

@app.route("/delete_office/<int:office_id>", methods=["POST"])
def delete_office(office_id):
    office = Office.query.get_or_404(office_id)
    db.session.delete(office)
    db.session.commit()
    return redirect(url_for("admin_panel"))

if __name__ == "__main__":
    app.run(debug=True)
