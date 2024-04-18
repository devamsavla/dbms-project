from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'yes'
app.config['MYSQL_DB'] = 'hospital_management'

mysql = MySQL(app)

# Define predefined usernames and passwords
user_credentials = {
    'admin': '123',
    'user1': 'password1',
    'user2': 'password2'
}

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the submitted username exists and the password matches
        if username in user_credentials and user_credentials[username] == password:
            session['logged_in'] = True
            session['username'] = username  # Store the username in the session
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password. Please try again.'
    return render_template('login.html')

# Route for logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Route for index page
@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', patient={'id': 1})  # Assuming a patient with ID 1 for demonstration

# Route for patients page
@app.route('/patients')
def patients():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM patients")
    columns = [column[0] for column in cur.description]
    patients_list = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    return render_template('patients.html', patients=patients_list)

# Route for deleting a patient
@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('patients'))

# Route for adding a patient
@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        age = request.form['age']
        email = request.form['email']
        phone_number = request.form['phone_number']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO patients (first_name, last_name, age, email, phone_number) VALUES (%s, %s, %s, %s, %s)",
                    (first_name, last_name, age, email, phone_number))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('patients'))
    return render_template('add_patient.html')

# Route for doctors page
@app.route('/doctors')
def doctors():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM doctors")
    doctors = cur.fetchall()
    cur.close()
    return render_template('doctors.html', doctors=doctors)

# Route for all patients page
@app.route('/all_patients')
def all_patients():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM patients")
    columns = [column[0] for column in cur.description]
    patients_list = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    return render_template('all_patients.html', patients=patients_list)

# Route for dashboard
@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # Fetch data from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT specialization, COUNT(*) as count FROM doctors GROUP BY specialization")
    data = cur.fetchall()
    cur.close()
    
    # Prepare data for rendering in the template
    labels = [row[0] for row in data]
    counts = [row[1] for row in data]

    # Render the dashboard template with the fetched data
    return render_template('dashboard.html', labels=labels, counts=counts)


@app.route('/update_patient/<int:patient_id>', methods=['GET', 'POST'])
def update_patient(patient_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        age = request.form['age']
        email = request.form['email']
        phone_number = request.form['phone_number']
        cur.execute("UPDATE patients SET first_name = %s, last_name = %s, age = %s, email = %s, phone_number = %s WHERE id = %s",
                    (first_name, last_name, age, email, phone_number, patient_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('patients'))

    cur.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
    patient_data = cur.fetchone()
    cur.close()

    if patient_data:
        patient = {
            'id': patient_data[0],
            'first_name': patient_data[1],
            'last_name': patient_data[2],
            'age': patient_data[3],
            'email': patient_data[4],
            'phone_number': patient_data[5]
        }
        return render_template('update.html', patient=patient, patient_id=patient_id)
    else:
        return "Patient not found."



if __name__ == '__main__':
    app.run(debug=True)
