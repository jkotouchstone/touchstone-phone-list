from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Load database URL from Render environment variable
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")  # Now using an environment variable
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

# Create Tables in Database (if they don’t exist)
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    employees = Employee.query.all()  # Fetch all employees from the database
    return render_template("index.html", employees=employees)

@app.route("/add_employee", methods=["POST"])
def add_employee():
    """Route to add a new employee from the form."""
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

if __name__ == "__main__":
    app.run(debug=True)
