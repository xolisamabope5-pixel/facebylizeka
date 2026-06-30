from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "facebylizeka_secret"

# ---------------- DATABASE ---------------- #

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///beauty.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Uploads folder
app.config["UPLOAD_FOLDER"] = "static/uploads"

db = SQLAlchemy(app)

# ---------------- MODELS ---------------- #

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.String(50))
    image = db.Column(db.String(200))

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    service = db.Column(db.String(100))
    date = db.Column(db.String(50))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default="Pending")

# ---------------- HOME ---------------- #

@app.route("/")
def home():
    services = Service.query.all()
    return render_template("index.html", services=services)

# ---------------- BOOKING ---------------- #

@app.route("/book", methods=["POST"])
def book():
    booking = Booking(
        name=request.form["name"],
        phone=request.form["phone"],
        service=request.form["service"],
        date=request.form["date"],
        message=request.form["message"],
        status="Pending"
    )
    db.session.add(booking)
    db.session.commit()
    return redirect(url_for("home"))

# ---------------- TRACK ---------------- #

@app.route("/track", methods=["GET", "POST"])
def track():
    bookings = None

    if request.method == "POST":
        phone = request.form["phone"]
        bookings = Booking.query.filter_by(phone=phone).all()

    return render_template("track.html", bookings=bookings)

# ---------------- ADMIN LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "facebylizeka" and request.form["password"] == "24689":
            session["admin"] = True
            return redirect(url_for("admin"))
        return "Invalid login"

    return render_template("login.html")

# ---------------- ADMIN DASHBOARD ---------------- #

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect(url_for("login"))

    services = Service.query.all()
    bookings = Booking.query.all()

    return render_template("admin.html", services=services, bookings=bookings)

# ---------------- APPROVE BOOKING ---------------- #

@app.route("/approve/<int:id>")
def approve(id):
    booking = Booking.query.get(id)
    booking.status = "Approved"
    db.session.commit()
    return redirect(url_for("admin"))

# ---------------- REJECT BOOKING ---------------- #

@app.route("/reject/<int:id>")
def reject(id):
    booking = Booking.query.get(id)
    booking.status = "Rejected"
    db.session.commit()
    return redirect(url_for("admin"))

# ---------------- ADD SERVICE ---------------- #

@app.route("/add_service", methods=["POST"])
def add_service():
    name = request.form["name"]
    price = request.form["price"]

    file = request.files["image"]
    filename = None

    if file and file.filename != "":
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    service = Service(
        name=name,
        price=price,
        image=filename
    )

    db.session.add(service)
    db.session.commit()

    return redirect(url_for("admin"))

# ---------------- EDIT SERVICE ---------------- #

@app.route("/edit_service/<int:id>", methods=["GET", "POST"])
def edit_service(id):
    service = Service.query.get(id)

    if request.method == "POST":
        service.name = request.form["name"]
        service.price = request.form["price"]
        db.session.commit()
        return redirect(url_for("admin"))

    return f"""
    <h2>Edit Service</h2>
    <form method='POST'>
        <input name='name' value='{service.name}'><br><br>
        <input name='price' value='{service.price}'><br><br>
        <button>Update</button>
    </form>
    """

# ---------------- DELETE SERVICE ---------------- #

@app.route("/delete_service/<int:id>")
def delete_service(id):
    service = Service.query.get(id)
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for("admin"))

# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- INIT DB ---------------- #

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run()