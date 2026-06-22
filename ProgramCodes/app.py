import functools
import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from flask_wtf import CSRFProtect

from backend.auth import AuthError, login_user, register_user
from backend.password_generator import generate_password
from backend.vault import add_entry, delete_entry, list_entries

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

Session(app)
csrf = CSRFProtect(app)


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if len(password) < 8:
            flash("Password must be at least 8 characters long.")
            return render_template("register.html")

        try:
            register_user(username, email, password)
        except AuthError as e:
            flash(str(e))
            return render_template("register.html")

        flash("Account created. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        try:
            user_id, vault_key = login_user(username, password)
        except AuthError as e:
            flash(str(e))
            return render_template("login.html")

        session.clear()
        session["user_id"] = user_id
        session["username"] = username
        session["vault_key"] = vault_key
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    entries = list_entries(session["user_id"], session["vault_key"])
    return render_template("dashboard.html", entries=entries, username=session["username"])


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        site_name = request.form.get("site_name", "").strip()
        site_username = request.form.get("site_username", "").strip()
        site_password = request.form.get("site_password", "")
        add_entry(session["user_id"], site_name, site_username, site_password, session["vault_key"])
        return redirect(url_for("dashboard"))

    return render_template("add_entry.html")


@app.route("/delete/<int:entry_id>", methods=["POST"])
@login_required
def delete(entry_id):
    delete_entry(entry_id, session["user_id"])
    return redirect(url_for("dashboard"))


@app.route("/generate-password")
@login_required
def generate_password_route():
    length = request.args.get("length", default=16, type=int)
    return jsonify({"password": generate_password(length)})


if __name__ == "__main__":
    app.run(debug=False)
