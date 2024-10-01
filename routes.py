from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models import db, UserModel, CategoryMaster, BlogModel, BlogComment, login

app = Flask(__name__)
app.secret_key = "ItShouldBeLongEnough"

app.config["SQLALchemy_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

# binding with app
db.init_app(app)
login.init_app(app)

login.login_view = "login"


@app.before_first_request
def create_all():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
