from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secretkey"

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("project.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create tables
conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS records(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT
)
""")
conn.commit()
conn.close()

# ---------- REGISTER ----------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        conn.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)",
                     (name,email,password))
        conn.commit()
        conn.close()
        return redirect("/login")
    return render_template("register.html")

# ---------- LOGIN ----------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=? AND password=?",
                            (email,password)).fetchone()
        conn.close()

        if user:
            session["user"] = user["name"]
            return redirect("/dashboard")
        else:
            return "Invalid Email or Password"
    return render_template("login.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    conn = get_db()
    records = conn.execute("SELECT * FROM records").fetchall()
    conn.close()
    return render_template("dashboard.html", records=records)

# ---------- ADD RECORD ----------
@app.route("/add", methods=["GET","POST"])
def add():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        conn = get_db()
        conn.execute("INSERT INTO records (title,description) VALUES (?,?)",
                     (title,description))
        conn.commit()
        conn.close()
        return redirect("/dashboard")
    return render_template("add.html")

# ---------- EDIT RECORD ----------
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):
    conn = get_db()
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        conn.execute("UPDATE records SET title=?, description=? WHERE id=?",
                     (title,description,id))
        conn.commit()
        conn.close()
        return redirect("/dashboard")

    record = conn.execute("SELECT * FROM records WHERE id=?",(id,)).fetchone()
    conn.close()
    return render_template("edit.html", record=record)

# ---------- DELETE RECORD ----------
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM records WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
