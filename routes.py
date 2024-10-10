from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user
from models import UserModel, BlogModel, db, login, CategoryMaster

global_all_category_no = None
global_all_category_name = None
app = Flask(__name__)
app.secret_key = "ItShouldBeLongEnough"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login.init_app(app)

login.login_view = "login"
    

def get_all_categories():
    global global_all_category_no, global_all_category_name
    all_category_info = db.session.query(
        CategoryMaster.category_id, CategoryMaster.category_name
    )
    all_category_info = list(all_category_info)
    global_all_category_no, global_all_category_name = zip(*all_category_info)


# Initialize the database and categories when the app starts
with app.app_context():
    db.create_all()
    get_all_categories()


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
    return redirect(url_for('list_all_blogs'))



@app.route("/createBlog", methods=["GET", "POST"])
@login_required
def create_blog():
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
            all_category_id=global_all_category_no,  # Using global_all_category_no for category IDs
            all_category_name=global_all_category_name,  # Using global_all_category_name for category names
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

    # Render the template with blog data and categories
    return render_template(
        "view_blog.html",
        all_self_blogs=all_self_blogs,
        all_categories=global_all_category_name,  # Pass the category names as 'all_categories'
    )


@app.route(
    "/self_blog_detail/<int:blog_model_id>/<string:blog_model_category>",
    methods=["GET", "POST"],
)
@login_required
def self_blog_detail(blog_model_id, blog_model_category):
    # Ensure the categories are updated
    get_all_categories()

    # Retrieve the specific blog by its ID
    blog_model = db.session.get(BlogModel, blog_model_id)

    # Handle form submission for updating or deleting the blog
    if request.method == "POST":
        if request.form["action"] == "Update":
            blog_model.blog_text = request.form.get("blog_text")
        else:
            BlogModel.query.filter_by(id=blog_model_id).delete()

        db.session.commit()
        return redirect(url_for("view_blogs"))

    # Render the blog detail template
    return render_template(
        "self_blog_detail.html",
        blog_id=blog_model_id,
        blog_categories=blog_model_category,
        blog_text=blog_model.blog_text,  # Corrected duplicate keys and cleaned access to variables
    )

@app.route('/listAllBlogs')
def list_all_blogs():
    all_blogs = BlogModel.query.all()
    all_users = UserModel.query.all()
    return render_template('list_all_blogs.html',all_blogs=all_blogs, all_users=all_users, all_categories=global_all_category_name)


if __name__ == "__main__":
    app.run(debug=True)
