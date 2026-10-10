from flask import Flask, render_template, request, redirect, send_from_directory
import mysql.connector
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

print("MAIL_USERNAME:", os.getenv("MAIL_USERNAME"))
print("MAIL_APP_PASSWORD exists:", bool(os.getenv("MAIL_APP_PASSWORD")))

def send_caregiver_email(to_email, medicine_name, status):
    msg = EmailMessage()

    msg["Subject"] = f"MediTrack AI - Medicine {status}"
    msg["From"] = os.getenv("MAIL_USERNAME")
    msg["To"] = to_email

    msg.set_content(
        f"Medicine: {medicine_name}\n"
        f"Status: {status}\n\n"
        f"MediTrack AI notification."
    )

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(
            os.getenv("MAIL_USERNAME"),
            os.getenv("MAIL_APP_PASSWORD")
        )
        smtp.send_message(msg)
 
@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/medicines")
def medicines():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM medicines")
    medicines = cursor.fetchall()
    cursor.close()

    return render_template("medicines.html", medicines=medicines)

@app.route("/adherence-report")
def adherence_report():
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(status = 'Taken') AS taken
        FROM medicines_adherence
    """)

    result = cursor.fetchone()
    cursor.close()

    total = result[0] or 0
    taken = result[1] or 0

    if total > 0:
        percentage = round((taken / total) * 100, 2)
    else:
        percentage = 0

    return render_template(
        "adherence_report.html",
        total=total,
        taken=taken,
        percentage=percentage
    )

@app.route("/add-medicine", methods=["GET", "POST"])
def add_medicine():

    if request.method == "POST":
        name = request.form["name"]
        dose = request.form["dose"]
        time = request.form["time"]
        duration = request.form["duration"]
        caregiver_email = request.form["caregiver_email"]

        cursor = db.cursor()

        cursor.execute(
    "INSERT INTO medicines (medicine_name, dosage, time, notes, Caregiver_email) VALUES (%s, %s, %s, %s, %s)",
    (name, dose, time, duration, caregiver_email)
)

        db.commit()

        return redirect("/medicines")

    return render_template("add_medicine.html")

@app.route("/medicine/<int:medicine_id>/taken", methods=["POST"])
def medicine_taken(medicine_id):
    cursor = db.cursor()

    cursor.execute(
        "SELECT medicine_name, caregiver_email FROM medicines WHERE id = %s",
        (medicine_id,)
    )

    medicine = cursor.fetchone()

    if medicine:
        medicine_name = medicine[0]
        caregiver_email = medicine[1]

        cursor.execute(
            "INSERT INTO medicines_adherence (medicine_id, status, taken_at) VALUES (%s, %s, NOW())",
            (medicine_id, "Taken")
        )

        db.commit()

        try:
            send_caregiver_email(
                caregiver_email,
                medicine_name,
                "Taken"
            )
        except Exception as e:
            print("Email error:", e)

    cursor.close()

    return redirect("/medicines")

@app.route("/medicine/<int:medicine_id>/missed", methods=["POST"])
def medicine_missed(medicine_id):
    cursor = db.cursor()

    cursor.execute(
        "SELECT medicine_name, caregiver_email FROM medicines WHERE id = %s",
        (medicine_id,)
    )

    medicine = cursor.fetchone()

    if medicine:
        medicine_name = medicine[0]
        caregiver_email = medicine[1]

        cursor.execute(
            "INSERT INTO medicines_adherence (medicine_id, status, taken_at) VALUES (%s, %s, NOW())",
            (medicine_id, "Missed")
        )

        db.commit()

        try:
            send_caregiver_email(
                caregiver_email,
                medicine_name,
                "Missed"
            )
        except Exception as e:
            print("Email error:", e)

    cursor.close()

    return redirect("/medicines")
    
@app.route("/test-db")
def test_db():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM medicines")
    medicines = cursor.fetchall()
    cursor.close()
    return str(medicines)

@app.route("/adherence/<int:medicine_id>/<status>", methods=["POST"])
def adherence(medicine_id, status):

    if status not in ["Taken", "Missed"]:
        return redirect("/medicines")

    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO medicines_adherence (medicine_id, status, taken_at) VALUES (%s, %s, NOW())",
        (medicine_id, status)
    )

    db.commit()
    cursor.close()

    return redirect("/medicines")

@app.route("/reminders.html")
def reminders():
    return send_from_directory(".", "reminders.html")
    
if __name__ == "__main__":
from flask import Flask, render_template, request, redirect, send_from_directory
import mysql.connector
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

print("MAIL_USERNAME:", os.getenv("MAIL_USERNAME"))
print("MAIL_APP_PASSWORD exists:", bool(os.getenv("MAIL_APP_PASSWORD")))

def send_caregiver_email(to_email, medicine_name, status):
    msg = EmailMessage()

    msg["Subject"] = f"MediTrack AI - Medicine {status}"
    msg["From"] = os.getenv("MAIL_USERNAME")
    msg["To"] = to_email

    msg.set_content(
        f"Medicine: {medicine_name}\n"
        f"Status: {status}\n\n"
        f"MediTrack AI notification."
    )

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(
            os.getenv("MAIL_USERNAME"),
            os.getenv("MAIL_APP_PASSWORD")
        )
        smtp.send_message(msg)
 
@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/medicines")
def medicines():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM medicines")
    medicines = cursor.fetchall()
    cursor.close()

    return render_template("medicines.html", medicines=medicines)

@app.route("/adherence-report")
def adherence_report():
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(status = 'Taken') AS taken
        FROM medicines_adherence
    """)

    result = cursor.fetchone()
    cursor.close()

    total = result[0] or 0
    taken = result[1] or 0

    if total > 0:
        percentage = round((taken / total) * 100, 2)
    else:
        percentage = 0

    return render_template(
        "adherence_report.html",
        total=total,
        taken=taken,
        percentage=percentage
    )

@app.route("/add-medicine", methods=["GET", "POST"])
def add_medicine():

    if request.method == "POST":
        name = request.form["name"]
        dose = request.form["dose"]
        time = request.form["time"]
        duration = request.form["duration"]
        caregiver_email = request.form["caregiver_email"]

        cursor = db.cursor()

        cursor.execute(
    "INSERT INTO medicines (medicine_name, dosage, time, notes, Caregiver_email) VALUES (%s, %s, %s, %s, %s)",
    (name, dose, time, duration, caregiver_email)
)

        db.commit()

        return redirect("/medicines")

    return render_template("add_medicine.html")

@app.route("/medicine/<int:medicine_id>/taken", methods=["POST"])
def medicine_taken(medicine_id):
    cursor = db.cursor()

    cursor.execute(
        "SELECT medicine_name, caregiver_email FROM medicines WHERE id = %s",
        (medicine_id,)
    )

    medicine = cursor.fetchone()

    if medicine:
        medicine_name = medicine[0]
        caregiver_email = medicine[1]

        cursor.execute(
            "INSERT INTO medicines_adherence (medicine_id, status, taken_at) VALUES (%s, %s, NOW())",
            (medicine_id, "Taken")
        )

        db.commit()

        try:
            send_caregiver_email(
                caregiver_email,
                medicine_name,
                "Taken"
            )
        except Exception as e:
            print("Email error:", e)

    cursor.close()

    return redirect("/medicines")

@app.route("/medicine/<int:medicine_id>/missed", methods=["POST"])
def medicine_missed(medicine_id):
    cursor = db.cursor()

    cursor.execute(
        "SELECT medicine_name, caregiver_email FROM medicines WHERE id = %s",
        (medicine_id,)
    )

    medicine = cursor.fetchone()

    if medicine:
        medicine_name = medicine[0]
        caregiver_email = medicine[1]

        cursor.execute(
            "INSERT INTO medicines_adherence (medicine_id, status, taken_at) VALUES (%s, %s, NOW())",
            (medicine_id, "Missed")
        )

        db.commit()

        try:
            send_caregiver_email(
                caregiver_email,
                medicine_name,
                "Missed"
            )
        except Exception as e:
            print("Email error:", e)

    cursor.close()

    return redirect("/medicines")
    
@app.route("/test-db")
def test_db():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM medicines")
    medicines = cursor.fetchall()
    cursor.close()
    return str(medicines)

@app.route("/adherence/<int:medicine_id>/<status>", methods=["POST"])
def adherence(medicine_id, status):

    if status not in ["Taken", "Missed"]:
        return redirect("/medicines")

    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO medicines_adherence (medicine_id, status, taken_at) VALUES (%s, %s, NOW())",
        (medicine_id, status)
    )

    db.commit()
    cursor.close()

    return redirect("/medicines")

@app.route("/reminders.html")
def reminders():
    return send_from_directory(".", "reminders.html")
    
if __name__ == "__main__":
    app.run(debug=True)