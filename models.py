from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="Member")  # "Admin" | "Member"

    # Relationships
    projects_created = db.relationship("Project", backref="creator", lazy=True)
    tasks_assigned = db.relationship("Task", backref="assignee", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
        }

    @property
    def initials(self):
        parts = self.name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return self.name[:2].upper()


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Relationships
    tasks = db.relationship("Task", backref="project", lazy=True, cascade="all, delete-orphan")

    @property
    def task_count(self):
        return len(self.tasks)

    @property
    def done_count(self):
        return sum(1 for t in self.tasks if t.status == "Done")

    @property
    def progress_pct(self):
        if self.task_count == 0:
            return 0
        return int((self.done_count / self.task_count) * 100)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_by": self.created_by,
            "task_count": self.task_count,
            "done_count": self.done_count,
            "progress_pct": self.progress_pct,
        }


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Todo")  # "Todo" | "In Progress" | "Done"
    due_date = db.Column(db.Date, nullable=True)
    assignee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)

    @property
    def is_overdue(self):
        if self.due_date and self.status != "Done":
            return self.due_date < date.today()
        return False

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "assignee_id": self.assignee_id,
            "project_id": self.project_id,
            "is_overdue": self.is_overdue,
        }
