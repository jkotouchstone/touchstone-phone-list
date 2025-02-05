from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
import csv
import io

app = Flask(__name__)
app.secret_key = "some_secret_key"  # Needed for flashing messages

# Load database URL from Render environment variable
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
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

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        # Check if a file was uploaded
        if "file" not in request.files or request.files["file"].filename == "":
            flash("No file selected!")
            return redirect(request.url)
        
        file = request.files["file"]

        try:
            # Read and decode the file (assuming it's a CSV encoded in UTF-8)
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.reader(stream)
            
            # Optionally, skip the header row if your CSV has headers:
            headers = next(csv_input, None)
            
            # Iterate over the CSV rows and add each record to the database
            for row in csv_input:
                # Adjust these indices based on your CSV column order:
                # For example: name, extension, cell_phone, job_title, location
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
    
    # If GET, render the upload form
    return render_template("upload.html")

if __name__ == "__main__":
    app.run(debug=True)
