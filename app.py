import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a strong secret in production

DATABASE = 'phone_list.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create employees table (for new databases) with the new 'location' column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            extension TEXT,
            cell_phone TEXT,
            job_title TEXT,
            location TEXT
        )
    ''')
    # Create offices table (unchanged)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS offices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            office_name TEXT NOT NULL,
            direct_line TEXT,
            physical_address TEXT
        )
    ''')
    conn.commit()
    conn.close()

def migrate_employee_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check the current columns in the employees table
    cursor.execute("PRAGMA table_info(employees)")
    columns = [col[1] for col in cursor.fetchall()]
    if "location" not in columns:
        # Add the new 'location' column without affecting existing data
        cursor.execute("ALTER TABLE employees ADD COLUMN location TEXT")
        conn.commit()
    conn.close()

# Initialize the database and run migration
init_db()
migrate_employee_table()

@app.route('/')
def index():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    employees = conn.execute('SELECT * FROM employees').fetchall()
    offices = conn.execute('SELECT * FROM offices').fetchall()
    conn.close()
    return render_template('index.html', employees=employees, offices=offices)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'Touchstone':
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            flash('Invalid password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        admin_password = request.form.get('admin_password')
        if admin_password == 'Chatham':
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid admin password')
    return render_template('admin_login.html')

@app.route('/admin')
def admin_panel():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    employees = conn.execute('SELECT * FROM employees').fetchall()
    offices = conn.execute('SELECT * FROM offices').fetchall()
    conn.close()
    return render_template('admin.html', employees=employees, offices=offices)

@app.route('/admin/add_employee', methods=['POST'])
def add_employee():
    if not session.get('admin'):
        flash('Admin access required')
        return redirect(url_for('admin_login'))
    name = request.form.get('name')
    extension = request.form.get('extension')
    cell_phone = request.form.get('cell_phone')
    job_title = request.form.get('job_title')
    location = request.form.get('location')  # New field
    conn = get_db_connection()
    conn.execute('INSERT INTO employees (name, extension, cell_phone, job_title, location) VALUES (?, ?, ?, ?, ?)',
                 (name, extension, cell_phone, job_title, location))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_employee/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    if not session.get('admin'):
        flash('Admin access required')
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/add_office', methods=['POST'])
def add_office():
    if not session.get('admin'):
        flash('Admin access required')
        return redirect(url_for('admin_login'))
    office_name = request.form.get('office_name')
    direct_line = request.form.get('direct_line')
    physical_address = request.form.get('physical_address')
    conn = get_db_connection()
    conn.execute('INSERT INTO offices (office_name, direct_line, physical_address) VALUES (?, ?, ?)',
                 (office_name, direct_line, physical_address))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_office/<int:office_id>', methods=['POST'])
def delete_office(office_id):
    if not session.get('admin'):
        flash('Admin access required')
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM offices WHERE id = ?', (office_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/edit_employee/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    if not session.get('admin'):
        flash('Admin access required')
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    employee = conn.execute('SELECT * FROM employees WHERE id = ?', (employee_id,)).fetchone()
    if request.method == 'POST':
         name = request.form.get('name')
         extension = request.form.get('extension')
         cell_phone = request.form.get('cell_phone')
         job_title = request.form.get('job_title')
         location = request.form.get('location')  # New field
         conn.execute('UPDATE employees SET name=?, extension=?, cell_phone=?, job_title=?, location=? WHERE id=?',
                      (name, extension, cell_phone, job_title, location, employee_id))
         conn.commit()
         conn.close()
         return redirect(url_for('admin_panel'))
    conn.close()
    return render_template('edit_employee.html', employee=employee)

@app.route('/admin/edit_office/<int:office_id>', methods=['GET', 'POST'])
def edit_office(office_id):
    if not session.get('admin'):
        flash('Admin access required')
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    office = conn.execute('SELECT * FROM offices WHERE id = ?', (office_id,)).fetchone()
    if request.method == 'POST':
         office_name = request.form.get('office_name')
         direct_line = request.form.get('direct_line')
         physical_address = request.form.get('physical_address')
         conn.execute('UPDATE offices SET office_name=?, direct_line=?, physical_address=? WHERE id=?',
                      (office_name, direct_line, physical_address, office_id))
         conn.commit()
         conn.close()
         return redirect(url_for('admin_panel'))
    conn.close()
    return render_template('edit_office.html', office=office)

if __name__ == '__main__':
    app.run(debug=True)
