from flask import Flask, request, render_template, redirect, session, send_from_directory, abort
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- CONFIG ----------
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# สร้างโฟลเดอร์ uploads ถ้ายังไม่มี
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not os.path.exists("users.txt"):
            return "ยังไม่มีผู้ใช้ในระบบ"

        with open("users.txt", "r", encoding="utf-8") as f:
            for line in f:
                u, p = line.strip().split(":")
                if u == username and p == password:
                    session["user"] = username
                    return redirect("/dashboard")

        return "Login Failed"

    return render_template("login.html")


# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if os.path.exists("users.txt"):
            with open("users.txt", "r", encoding="utf-8") as f:
                for line in f:
                    u, _ = line.strip().split(":")
                    if u == username:
                        return "ชื่อผู้ใช้นี้มีแล้ว"

        with open("users.txt", "a", encoding="utf-8") as f:
            f.write(f"{username}:{password}\n")

        return redirect("/")

    return render_template("register.html")


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    # เอาเฉพาะไฟล์เท่านั้น (ไม่เอาโฟลเดอร์)
    files = [
        f for f in os.listdir(app.config["UPLOAD_FOLDER"])
        if os.path.isfile(os.path.join(app.config["UPLOAD_FOLDER"], f))
    ]

    return render_template(
        "dashboard.html",
        user=session["user"],
        files=files
    )


# ---------- UPLOAD ----------
@app.route("/upload", methods=["POST"])
def upload():
    if "user" not in session:
        return redirect("/")

    file = request.files.get("file")
    if not file or file.filename == "":
        return redirect("/dashboard")

    # ปลอดภัยชื่อไฟล์
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    return redirect("/dashboard")


# ---------- DOWNLOAD ----------
@app.route("/download/<filename>")
def download(filename):
    if "user" not in session:
        return redirect("/")

    filename = secure_filename(filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if not os.path.isfile(file_path):
        abort(404)

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )


# ---------- DELETE ----------
@app.route("/delete/<filename>", methods=["POST"])
def delete_file(filename):
    if "user" not in session:
        return redirect("/")

    filename = secure_filename(filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    # ลบเฉพาะไฟล์เท่านั้น
    if os.path.isfile(file_path):
        os.remove(file_path)

    return redirect("/dashboard")


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)

# python app.py