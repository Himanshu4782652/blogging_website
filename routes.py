from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user

from models import UserModel, db, login  # CategoryMaster, BlogModel, BlogComment


def create_app():
    app = Flask(__name__)
    app.secret_key = "ItShouldBeLongEnough"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the app with extensions
    db.init_app(app)
    login.init_app(app)

    login.login_view = "login"

    with app.app_context():
        # Create the database tables if they don't exist
        db.create_all()

    return app


app = create_app()


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return "Already logged-In"
    
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        if UserModel.query.filter_by(email=email).first():
            return "Email already exists"

        user = UserModel(email=email, username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return "Thank You!"
    return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return "Already logged-In"
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = UserModel.query.filter_by(email=email).first()

        if user is not None and user.check_password(request.form.get("password")):
            login_user(user)
            return "Login Successful"
        else:
            return "Invalid email or password"
        return render_template("/register.html")
    return render_template("/login.html")


if __name__ == "__main__":
    app.run(debug=True)
