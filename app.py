from cs50 import SQL
from datetime import datetime
from flask_session import Session
from flask import Flask, redirect, render_template, request, session

app = Flask(__name__)

db = SQL("sqlite:///todo.db")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    """Shows current list of tasks that are both done and undone"""
    if "user_id" not in session:
        return redirect("/login")

    tasks = db.execute("SELECT * FROM tasks WHERE id = ?", session["user_id"])

    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["GET", "POST"])
def add():
    """Adds tasks to the database"""
    if request.method == "POST":
        task = request.form.get("task")

        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y, %H:%M:%S")

        db.execute("INSERT INTO tasks (id, task, status, add_date_time, complete_date_time) VALUES(?, ?, ?, ?, ?)", session["user_id"], task, "Not Completed", date_time, "Haven't completed yet")

        return redirect("/")

    else:
        return render_template("add.html")


@app.route("/complete", methods=["GET", "POST"])
def complete():
    """Marks tasks that aren't completed yet"""
    tasks = db.execute("SELECT task FROM tasks WHERE status = ? AND id = ?", "Not Completed", session["user_id"])
    if request.method == "POST":

        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y, %H:%M:%S")

        for task in tasks:
            check = request.form.get(task["task"])
            if check == "on":
                db.execute("UPDATE tasks SET status = ?, complete_date_time = ? WHERE task = ?", "Completed", date_time, task["task"])

        return redirect("/")
    else:
        return render_template("complete.html", tasks=tasks)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Registers the user to the web application"""
    if request.method == "POST":
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        db.execute("INSERT INTO users (name, password) VALUES(?, ?)", user_name, password)

        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login to the website"""
    if request.method == "POST":
        user_name = request.form.get("user_name")
        password = request.form.get("password")

        for user in db.execute("SELECT * FROM users"):
            if user["name"] == user_name and user["password"] == password:
                session["user_id"] = user["id"]
                break
        else:
            return redirect("/login")

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log the users out"""
    session.clear()
    return redirect("/")
