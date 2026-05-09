from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import bcrypt
from functools import wraps
from models import db, User

auth_bp = Blueprint("auth", __name__)


# ─── Decorators ───────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("role") != "Admin":
            flash("Admin access required.", "error")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)
    return decorated


# ─── Routes ───────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["role"] = user.role
            session["initials"] = user.initials
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid email or password.", "error")

    return render_template("login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if "user_id" in session:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        role = request.form.get("role", "Member")

        # Validation
        errors = []
        if not name:
            errors.append("Name is required.")
        elif not all(c.isalpha() or c.isspace() for c in name):
            errors.append("Name must contain only characters (no digits).")

        if not email:
            errors.append("Email is required.")
        elif "@gmail" not in email:
            errors.append("Only Gmail accounts are allowed.")

        if not password:
            errors.append("Password is required.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if role not in ("Admin", "Member"):
            role = "Member"

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("signup.html", form_data=request.form)

        # Check duplicate email
        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "error")
            return render_template("signup.html", form_data=request.form)

        # Hash password
        pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        user = User(name=name, email=email, password_hash=pw_hash, role=role)
        db.session.add(user)
        db.session.commit()

        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html", form_data={})


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You've been logged out.", "info")
    return redirect(url_for("auth.login"))
