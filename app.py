import os
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from collections import defaultdict

app = Flask(__name__)
app.secret_key = "beauty-secret"

# ---------------- UPLOAD FOLDER ----------------
UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- DATABASE ----------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///beauty.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------- MODELS ----------------

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    price = db.Column(db.String(50))
    image = db.Column(db.String(200))

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    service = db.Column(db.String(120))
    date = db.Column(db.String(50))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default="Pending")

with app.app_context():
    db.create_all()

# ---------------- HOME ----------------
@app.route("/")
def home():
    services = Service.query.all()
    return render_template("index.html", services=services)

# ---------------- BOOK ----------------
@app.route("/book", methods=["POST"])
def book():
    new_booking = Booking(
        name=request.form["name"],
        phone=request.form["phone"],
        service=request.form["service"],
        date=request.form["date"],
        message=request.form["message"],
        status="Pending"
    )

    db.session.add(new_booking)
    db.session.commit()

    return "Booking received successfully!"

# ---------------- TRACK ----------------
@app.route("/track", methods=["GET", "POST"])
def track():
    bookings = []

    if request.method == "POST":
        phone = request.form["phone"]
        bookings = Booking.query.filter_by(phone=phone).all()

    return render_template("track.html", bookings=bookings)

# ---------------- LOGIN (UPDATED) ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "facebylizeka" and password == "24689":
            session["user"] = True
            return redirect("/admin")

        return "Invalid username or password"

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- ADMIN ----------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("user"):
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]

        file = request.files["image"]
        filename = None

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        service = Service(name=name, price=price, image=filename)
        db.session.add(service)
        db.session.commit()

        return redirect("/admin")

    services = Service.query.all()
    return render_template("admin.html", services=services)

# ---------------- DELETE SERVICE ----------------
@app.route("/delete/<int:id>")
def delete(id):
    if not session.get("user"):
        return redirect("/login")

    service = Service.query.get(id)
    if service:
        db.session.delete(service)
        db.session.commit()

    return redirect("/admin")

# ---------------- APPROVE ----------------
@app.route("/approve/<int:id>")
def approve(id):
    if not session.get("user"):
        return redirect("/login")

    booking = Booking.query.get(id)
    if booking:
        booking.status = "Approved"
        db.session.commit()

    return redirect("/bookings")

# ---------------- REJECT ----------------
@app.route("/reject/<int:id>")
def reject(id):
    if not session.get("user"):
        return redirect("/login")

    booking = Booking.query.get(id)
    if booking:
        booking.status = "Rejected"
        db.session.commit()

    return redirect("/bookings")

# ---------------- BOOKINGS ----------------
@app.route("/bookings")
def bookings():
    if not session.get("user"):
        return redirect("/login")

    all_bookings = Booking.query.all()
    return render_template("bookings.html", bookings=all_bookings)

# ---------------- CALENDAR ----------------
@app.route("/calendar")
def calendar():
    if not session.get("user"):
        return redirect("/login")

    bookings = Booking.query.all()

    grouped = defaultdict(list)
    for b in bookings:
        grouped[b.date].append(b)

    return render_template("calendar.html", grouped=grouped)

# ---------------- RUN (LOCAL ONLY) ----------------
if __name__ == "__main__":
    app.run()