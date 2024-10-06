from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user
from models import UserModel, BlogModel, db, login, CategoryMaster

# Global dictionary to store categories with category_id as key and category_name as value
global_all_categories = {}


def get_all_categories():
    global global_all_categories
    # Retrieve all categories from the CategoryMaster model
    all_category_info = db.session.query(
        CategoryMaster.category_id, CategoryMaster.category_name
    ).all()
    # Convert list of tuples into a dictionary
    global_all_categories = {cat_id: cat_name for cat_id, cat_name in all_category_info}


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
        return redirect(url_for("blogs"))

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

        return redirect(url_for("blogs"))

    return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("blogs"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = UserModel.query.filter_by(email=email).first()

        if user is not None and user.check_password(password):
            login_user(user)
            return redirect(url_for("blogs"))
        else:
            return "Invalid email or password"

    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/blogs")
def blogs():
    if current_user.is_authenticated:
        return render_template("blogs_home.html")
    return redirect(url_for("register"))


@app.route("/createBlog", methods=["GET", "POST"])
@login_required
def create_blog():
    # Call the get_all_categories function to populate global variables
    get_all_categories()

    if request.method == "POST":
        category_id = request.form.get("category_id")
        blog_text = request.form.get("blog_text")
        today = datetime.now()
        blog_user_id = current_user.id
        blog_read_count = 0
        blog_rating_count = 0

        new_blog = BlogModel(
            category_id=category_id,
            blog_user_id=blog_user_id,
            blog_text=blog_text,
            blog_creation_date=today,
            blog_read_count=blog_read_count,
            blog_rating_count=blog_rating_count,
        )
        db.session.add(new_blog)
        db.session.commit()
        return redirect(url_for("blogs"))
    else:
        return render_template(
            "create_blog.html",
            all_category_id=global_all_categories.keys(),
            all_category_name=global_all_categories.values(),
        )


@app.route("/viewBlog")
@login_required
def view_blogs():
    # Call the get_all_categories function to ensure the categories are updated
    get_all_categories()
    # Get all blogs authored by the current user
    all_self_blogs = BlogModel.query.filter(
        BlogModel.blog_user_id == current_user.id
    ).all()
    return render_template(
        "view_blog.html",
        all_self_blogs=all_self_blogs,
        all_categories=global_all_categories,
    )


if __name__ == "__main__":
    app.run(debug=True)
