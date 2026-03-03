from flask import Flask, request, render_template, redirect, session, send_file
from werkzeug.utils import secure_filename
from ftplib import FTP
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ==============================
# FTP CONFIG (สำคัญมาก)
# ==============================
FTP_HOST = "ftp"   # ชื่อ service ใน docker-compose
FTP_PORT = 21

TEMP_FOLDER = "temp"
os.makedirs(TEMP_FOLDER, exist_ok=True)


# ==============================
# ฟังก์ชันเชื่อมต่อ FTP
# ==============================
def ftp_connect():
    if "user" not in session:
        return None

    ftp = FTP()
    ftp.connect(FTP_HOST, FTP_PORT)
    ftp.login(session["user"], session["pass"])
    ftp.set_pasv(True)
    return ftp


# ==============================
# LOGIN
# ==============================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            ftp = FTP()
            ftp.connect(FTP_HOST, FTP_PORT)
            ftp.login(username, password)
            ftp.quit()

            session["user"] = username
            session["pass"] = password
            return redirect("/dashboard")

        except:
            return "Login Failed"

    return render_template("login.html")


# ==============================
# DASHBOARD (ดึงไฟล์จาก FTP)
# ==============================
@app.route("/dashboard")
def dashboard():
    ftp = ftp_connect()
    if not ftp:
        return redirect("/")

    files = ftp.nlst()
    ftp.quit()

    return render_template("dashboard.html",
                           user=session["user"],
                           files=files)


# ==============================
# UPLOAD (ผ่าน FTP เท่านั้น)
# ==============================
@app.route("/upload", methods=["POST"])
def upload():
    ftp = ftp_connect()
    if not ftp:
        return redirect("/")

    file = request.files.get("file")
    if not file or file.filename == "":
        return redirect("/dashboard")

    filename = secure_filename(file.filename)

    ftp.storbinary(f"STOR {filename}", file.stream)
    ftp.quit()

    return redirect("/dashboard")


# ==============================
# DOWNLOAD (ผ่าน FTP เท่านั้น)
# ==============================
@app.route("/download/<filename>")
def download(filename):
    ftp = ftp_connect()
    if not ftp:
        return redirect("/")

    filename = secure_filename(filename)
    local_path = os.path.join(TEMP_FOLDER, filename)

    with open(local_path, "wb") as f:
        ftp.retrbinary(f"RETR {filename}", f.write)

    ftp.quit()

    return send_file(local_path, as_attachment=True)


# ==============================
# DELETE (ผ่าน FTP เท่านั้น)
# ==============================
@app.route("/delete/<filename>", methods=["POST"])
def delete_file(filename):
    ftp = ftp_connect()
    if not ftp:
        return redirect("/")

    filename = secure_filename(filename)
    ftp.delete(filename)
    ftp.quit()

    return redirect("/dashboard")


# ==============================
# LOGOUT
# ==============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

    # วิธีรัน docker-compose up --build หรือ docker compose up --build
    # และเข้าไปที่ http://localhost:8000