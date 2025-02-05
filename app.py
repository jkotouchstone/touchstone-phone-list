from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Use your Render PostgreSQL database URL
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://phone_list_user:Im2SEXmPwj7aFeuvv5gCjGwTBM1c8jJ3@dpg-cuhj5el2ng1s7387h7p0-a/phone_list"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Define Employee Model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    extension = db.Column(db.String(10), nullable=False)
    cell_phone = db.Column(db.String(20), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)

# Create Tables
with app.app_context():
    db.create_all()  # Ensures tables exist

@app.route("/")
def index():
    employees = Employee.query.all()  # Fetch all employees
    return render_template("index.html", employees=employees)

@app.route("/add_employee", methods=["POST"])
def add_employee():
    name = request.form["name"]
    extension = request.form["extension"]
    cell_phone = request.form["cell_phone"]
    job_title = request.form["job_title"]
    location = request.form["location"]

    new_employee = Employee(name=name, extension=extension, cell_phone=cell_phone, job_title=job_title, location=location)
    db.session.add(new_employee)
    db.session.commit()

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
