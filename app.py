import os
from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import date, timedelta
from collections import defaultdict
from dotenv import load_dotenv

from models import db, User, Project, Task
from auth import auth_bp, login_required, admin_required

load_dotenv()

# ─── App Factory ──────────────────────────────────────────────────────────────

def create_app():
    app = Flask(__name__)

    app.secret_key = os.environ.get("SECRET_KEY", "astra-dev-secret-change-in-prod")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///astra.db"
    )
    # Railway PostgreSQL compat: fix postgres:// -> postgresql://
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgres://"):
        app.config["SQLALCHEMY_DATABASE_URI"] = app.config[
            "SQLALCHEMY_DATABASE_URI"
        ].replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    db.init_app(app)

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        _seed_demo_data()

    return app


def _seed_demo_data():
    """Create demo projects and tasks if they are missing."""
    import bcrypt
    
    # Ensure Admin and Member exist
    admin = User.query.filter_by(role="Admin").first()
    if not admin:
        admin = User(
            name="Alex Admin",
            email="admin@gmail.com",
            password_hash=bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode(),
            role="Admin",
        )
        db.session.add(admin)
        db.session.commit()
        
    member = User.query.filter_by(role="Member").first()
    if not member:
        member = User(
            name="Morgan Member",
            email="member@gmail.com",
            password_hash=bcrypt.hashpw(b"member123", bcrypt.gensalt()).decode(),
            role="Member",
        )
        db.session.add(member)
        db.session.commit()

    # Ensure 5 projects exist
    if Project.query.count() < 5:
        projects_data = [
            ("Astra Launch", "Ship the MVP by Q3."),
            ("Mobile App", "Develop the iOS and Android versions."),
            ("Marketing Campaign", "Plan and execute the summer campaign."),
            ("Internal Security", "Audit and enhance system security."),
            ("Data Analytics", "Implement the new dashboard metrics.")
        ]
        
        today = date.today()
        for title, desc in projects_data:
            # Check if project title already exists to avoid duplicates
            if not Project.query.filter_by(title=title).first():
                proj = Project(title=title, description=desc, created_by=admin.id)
                db.session.add(proj)
                db.session.flush() # Get proj.id
                
                # Add 3 demo tasks for each new project
                tasks = [
                    Task(title=f"Research for {title}", status="Done", 
                         due_date=today - timedelta(days=5), assignee_id=admin.id, project_id=proj.id),
                    Task(title=f"Planning for {title}", status="In Progress", 
                         due_date=today + timedelta(days=2), assignee_id=member.id, project_id=proj.id),
                    Task(title=f"Testing for {title}", status="Todo", 
                         due_date=today + timedelta(days=10), assignee_id=member.id, project_id=proj.id),
                ]
                db.session.add_all(tasks)
        
        db.session.commit()


# ─── Main Blueprint ────────────────────────────────────────────────────────────

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    today = date.today()
    all_tasks = Task.query.all()
    total = len(all_tasks)
    pending = sum(1 for t in all_tasks if t.status in ("Todo", "In Progress"))
    overdue = [t for t in all_tasks if t.is_overdue]

    recent_tasks = Task.query.order_by(Task.id.desc()).limit(8).all()
    for t in recent_tasks:
        t._project = Project.query.get(t.project_id)
        t._assignee = User.query.get(t.assignee_id) if t.assignee_id else None

    return render_template(
        "dashboard.html",
        total=total,
        pending=pending,
        overdue_count=len(overdue),
        overdue_tasks=overdue[:5],
        recent_tasks=recent_tasks,
        all_projects=Project.query.all(),
        all_users=User.query.all(),
    )


@main_bp.route("/projects", methods=["GET", "POST"])
@login_required
def projects():
    if request.method == "POST":
        # Admin only
        if session.get("role") != "Admin":
            flash("Admin access required.", "error")
            return redirect(url_for("main.projects"))

        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

        if not title:
            flash("Project title is required.", "error")
            return redirect(url_for("main.projects"))

        proj = Project(title=title, description=description, created_by=session["user_id"])
        db.session.add(proj)
        db.session.commit()
        flash(f'Project "{title}" created!', "success")
        return redirect(url_for("main.projects"))

    all_projects = Project.query.order_by(Project.id.desc()).all()
    for p in all_projects:
        p._creator = User.query.get(p.created_by)
    return render_template("projects.html", projects=all_projects)


@main_bp.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks():
    if request.method == "POST":
        # Admin only
        if session.get("role") != "Admin":
            return jsonify({"error": "Forbidden"}), 403

        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        project_id = request.form.get("project_id")
        assignee_id = request.form.get("assignee_id") or None
        due_date_str = request.form.get("due_date", "").strip()
        status = request.form.get("status", "Todo")

        errors = []
        if not title:
            errors.append("Task title is required.")
        if not project_id:
            errors.append("Project is required.")

        due_date = None
        if due_date_str:
            try:
                due_date = date.fromisoformat(due_date_str)
            except ValueError:
                errors.append("Invalid date format.")

        if errors:
            for e in errors:
                flash(e, "error")
            return redirect(url_for("main.tasks"))

        task = Task(
            title=title,
            description=description,
            status=status,
            due_date=due_date,
            assignee_id=int(assignee_id) if assignee_id else None,
            project_id=int(project_id),
        )
        db.session.add(task)
        db.session.commit()
        flash(f'Task "{title}" created!', "success")
        return redirect(url_for("main.tasks"))

    # Build query — members see all tasks (but can only change their own)
    all_tasks = Task.query.order_by(Task.id.desc()).all()
    for t in all_tasks:
        t._project = Project.query.get(t.project_id)
        t._assignee = User.query.get(t.assignee_id) if t.assignee_id else None

    all_projects = Project.query.all()
    all_users = User.query.all()

    return render_template(
        "tasks.html",
        tasks=all_tasks,
        projects=all_projects,
        users=all_users,
    )


@main_bp.route("/tasks/<int:task_id>/status", methods=["POST"])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)

    # Safely read from JSON body or form
    if request.is_json:
        new_status = (request.get_json() or {}).get("status")
    else:
        new_status = request.form.get("status")

    if new_status not in ("Todo", "In Progress", "Done"):
        return jsonify({"error": "Invalid status"}), 400

    # Members can only update their own tasks
    if session.get("role") != "Admin" and task.assignee_id != session["user_id"]:
        return jsonify({"error": "Forbidden"}), 403

    task.status = new_status
    db.session.commit()

    if request.is_json:
        return jsonify({"ok": True, "status": new_status, "is_overdue": task.is_overdue})
    flash(f"Task status updated to {new_status}.", "success")
    return redirect(url_for("main.tasks"))


@main_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@admin_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted.", "info")
    return redirect(url_for("main.tasks"))


@main_bp.route("/projects/<int:project_id>/delete", methods=["POST"])
@admin_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash("Project deleted.", "info")
    return redirect(url_for("main.projects"))


@main_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    if user_id == session.get("user_id"):
        flash("You cannot delete your own administrative account.", "error")
        return redirect(url_for("main.dashboard"))

    user = User.query.get_or_404(user_id)
    
    # Check if user owns projects (due to foreign key constraints)
    if Project.query.filter_by(created_by=user.id).first():
        flash(f"Cannot delete {user.name} because they are the creator of one or more projects. Reassign or delete those projects first.", "error")
        return redirect(url_for("main.dashboard"))

    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.name} has been removed from the workspace.", "info")
    return redirect(url_for("main.dashboard"))


# ─── Chart API ────────────────────────────────────────────────────────────────

@main_bp.route("/api/chart-data")
@login_required
def chart_data():
    """Return completed-task counts for the last 14 days."""
    today = date.today()
    counts = defaultdict(int)

    done_tasks = Task.query.filter_by(status="Done").all()
    for t in done_tasks:
        if t.due_date:
            delta = (today - t.due_date).days
            if 0 <= delta <= 13:
                counts[t.due_date.isoformat()] += 1

    labels = []
    data = []
    for i in range(13, -1, -1):
        d = today - timedelta(days=i)
        labels.append(d.strftime("%b %d"))
        data.append(counts.get(d.isoformat(), 0))

    return jsonify({"labels": labels, "data": data})


# ─── Context Processor ────────────────────────────────────────────────────────

@main_bp.app_context_processor
def inject_user():
    return {
        "current_user_id": session.get("user_id"),
        "current_user_name": session.get("user_name"),
        "current_role": session.get("role"),
        "current_initials": session.get("initials"),
    }


# ─── Entry Point ──────────────────────────────────────────────────────────────

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
