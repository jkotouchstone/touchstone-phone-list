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

# Define the Employee model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    extension = db.Column(db.String(10), nullable=False)
    cell_phone = db.Column(db.String(20), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)

# Define the Office model
class Office(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    office_name = db.Column(db.String(100), nullable=False)
    direct_line = db.Column(db.String(20), nullable=False)
    physical_address = db.Column(db.String(200), nullable=False)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    employees = Employee.query.all()
    offices = Office.query.all()  # Adjust as needed if you have a different source of office data
    return render_template("index.html", employees=employees, offices=offices)

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

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files or request.files["file"].filename == "":
            flash("No file selected!")
            return redirect(request.url)
        
        file = request.files["file"]
        try:
            # Read and decode the CSV file
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

@app.route("/admin_panel")
def admin_panel():
    # This route serves your admin panel from templates/admin.html
    return render_template("admin.html")

if __name__ == "__main__":
    app.run(debug=True)
