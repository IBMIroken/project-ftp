# ตั้งค่าการเชื่อมต่อ FTP

# กรอกข้อมูลดังนี้:
# Host	127.0.0.1
# Username	ftpuser1
# Password	รหัสที่ตั้งไว้ (1234)
# Port	21
# จากนั้นกด เชื่อมต่อด่วน

# หาก Login สำเร็จ จะเห็น:
# ด้านซ้าย: ไฟล์ในเครื่องผู้ใช้
# ด้านขวา: ไฟล์ใน FTP Server
# แสดงสถานะ Logged in

# อัปโหลดไฟล์ผ่าน FileZilla
# เลือกไฟล์จากฝั่ง Local Site (ซ้าย)
# ลากไฟล์ไปฝั่ง Remote Site (ขวา)
# ไฟล์จะถูกอัปโหลดไปยัง FTP Server

# ดาวน์โหลดไฟล์ผ่าน FileZilla
# เลือกไฟล์จากฝั่ง Remote Site
# ลากไฟล์มายังฝั่ง Local Site
# ไฟล์จะถูกดาวน์โหลดลงเครื่องผู้ใช้

# ลบไฟล์ (ถ้ามีสิทธิ์)
# คลิกขวาที่ไฟล์ในฝั่ง Remote Site
# เลือก Delete
# ไฟล์จะถูกลบออกจาก FTP Server

# สรุปการใช้งานระบบ
# ระบบรองรับการใช้งาน 2 รูปแบบ
# ผ่านเว็บแอปพลิเคชัน (ใช้งานง่าย เหมาะกับผู้ใช้ทั่วไป)
# ผ่าน FileZilla Client (เหมาะกับการจัดการไฟล์โดยตรง)
# ทั้งสองรูปแบบเชื่อมต่อไปยัง FTP Server เดียวกัน
# FTP Server รันผ่าน Docker โดยใช้ Pure-FTPd
# เว็บทำหน้าที่เป็นตัวกลางเชื่อมต่อ FTP ผ่าน Python Flask

# ================================
# Import Library ที่จำเป็น
# ================================

# Flask → ใช้สร้าง Web Application
# request → รับข้อมูลจาก form (POST/GET)
# render_template → แสดงหน้า HTML
# redirect → เปลี่ยนหน้าเว็บ
# session → เก็บสถานะการ login
# send_from_directory → ส่งไฟล์ให้ดาวน์โหลด
# abort → ใช้ส่ง error เช่น 404

# *---* ส่วนนี้คือการเรียกใช้ library ต่างๆ Flask ใช้สร้างเว็บ ftplib ใช้เชื่อมต่อ FTP และ os ใช้จัดการไฟล์ในเครื่อง *---*
from flask import Flask, request, render_template, redirect, session, send_from_directory, abort

# secure_filename → ป้องกันชื่อไฟล์อันตราย (เช่น ../)
from werkzeug.utils import secure_filename

# FTP → ใช้เชื่อมต่อ FTP Server
from ftplib import FTP

# os → ใช้จัดการไฟล์และโฟลเดอร์ในระบบ
import os

# ================================
# สร้าง Flask Application
# ================================

# สร้าง Web Application ด้วย Flask
# secret_key ใช้สำหรับเข้ารหัส session
# ถ้าไม่มี secret_key ระบบ login จะไม่ทำงาน

# *---* สร้าง Flask Application และตั้งค่า secret_key *---*
app = Flask(__name__)
app.secret_key = "secret123"


# ================================
# การตั้งค่าโฟลเดอร์
# ================================

UPLOAD_FOLDER = "uploads" # *---* โฟลเดอร์เก็บไฟล์ที่อัปโหลดเข้ามาในเครื่อง *---*
TEMP_FOLDER = "temp" # *---* โฟลเดอร์เก็บไฟล์ชั่วคราวตอนดาวน์โหลดจาก FTP ก่อนส่งให้ผู้ใช้ *---*

# กำหนดค่าให้ Flask รู้จักโฟลเดอร์อัปโหลด
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ================================
# การตั้งค่า FTP Server
# ================================

# FTP_HOST = localhost
# หมายถึง FTP Server รันอยู่เครื่องเดียวกัน
# (Docker ทำการ map port ออกมา)
# ถ้า FTP อยู่เครื่องอื่น → เปลี่ยนเป็น IP เครื่องนั้น
FTP_HOST = "localhost"
FTP_PORT = 21


# ================================
# สร้างโฟลเดอร์ถ้ายังไม่มี
# ================================

# exist_ok=True → ถ้ามีโฟลเดอร์อยู่แล้วจะไม่ error
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)


# ================================
# ฟังก์ชันเชื่อมต่อ FTP
# ================================

# *---* ฟังก์ชันนี้ใช้เชื่อมต่อไปยัง FTP Server โดยใช้ username และ password ถ้าเชื่อมต่อสำเร็จระบบจะสามารถสั่งงาน FTP หรือก็คือเข้าไปใช้งานได้ *---*
def ftp_connect(): 
    # ถ้ายังไม่ได้ login FTP → ไม่ให้เชื่อม
    if "ftp_user" not in session or "ftp_pass" not in session:
        return None

    # สร้าง FTP object
    ftp = FTP()

    # เชื่อมต่อ FTP Server
    ftp.connect(FTP_HOST, FTP_PORT)

    # Login เข้า FTP ด้วยข้อมูลใน session
    ftp.login(session["ftp_user"], session["ftp_pass"])

    return ftp


# ================================
# WEB LOGIN 
# ================================

# ส่วนนี้คือระบบสมัครสมาชิกและล็อกอิน จะบันทึกข้อมูลผู้ใช้ไว้ในไฟล์ users.txt ถ้าล็อกอินสำเร็จจะเข้าสู่หน้า แดชบอร์ด
@app.route("/", methods=["GET", "POST"]) 
def login():
    if request.method == "POST":
        # รับข้อมูลจาก form
        username = request.form.get("username")
        password = request.form.get("password")

        # ถ้าไฟล์ users.txt ยังไม่มี
        if not os.path.exists("users.txt"):
            return "ยังไม่มีผู้ใช้ในระบบ"

        # อ่านไฟล์ users.txt เพื่อตรวจสอบ login
        with open("users.txt", "r", encoding="utf-8") as f:
            for line in f:
                # แยก username และ password
                u, p = line.strip().split(":")
                if u == username and p == password:
                    # เก็บสถานะ login ใน session
                    session["user"] = username
                    return redirect("/dashboard")

        # ถ้า login ไม่ผ่าน
        return "Login Failed"

    # แสดงหน้า login.html
    return render_template("login.html")


# ================================
# REGISTER 
# ================================
# สมัครสมาชิกใหม่ (Web User)

# *---* อันนี้ก็เหมือนกัน แต่เป็นการสมัครสมาชิก จะบันทึกข้อมูลลงไฟล์ users.txt และตรวจสอบว่ามี username ซ้ำหรือไม่ ถ้ามีจะไม่ให้สมัครซ้ำ *---*
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # ตรวจสอบว่ามี username ซ้ำหรือไม่
        if os.path.exists("users.txt"):
            with open("users.txt", "r", encoding="utf-8") as f:
                for line in f:
                    u, _ = line.strip().split(":")
                    if u == username:
                        return "ชื่อผู้ใช้นี้มีแล้ว"

        # บันทึกผู้ใช้ใหม่ลงไฟล์ users.txt
        with open("users.txt", "a", encoding="utf-8") as f:
            f.write(f"{username}:{password}\n")

        return redirect("/")

    return render_template("register.html")


# ================================
# DASHBOARD
# ================================

# หน้าแดชบอร์ด สำหรับจัดการไฟล์ในเครื่อง
@app.route("/dashboard")
def dashboard():
    # ถ้ายังไม่ได้ login → กลับหน้า login
    if "user" not in session:
        return redirect("/")

    # ดึงรายชื่อไฟล์จากโฟลเดอร์ uploads
    files = [
        f for f in os.listdir(app.config["UPLOAD_FOLDER"])
        if os.path.isfile(os.path.join(app.config["UPLOAD_FOLDER"], f))
    ]

    # ส่งข้อมูลไปแสดงใน dashboard.html
    return render_template(
        "dashboard.html",
        user=session["user"],
        files=files,
        mode="local"
    )


# ================================
# UPLOAD 
# ================================
# อัปโหลดไฟล์เข้าเครื่อง

# ส่วนนี้คือการอัปโหลดไฟล์ คำสั่ง storbinary คือคำสั่งส่งไฟล์ไปเก็บใน FTP Server
@app.route("/upload", methods=["POST"])
def upload():
    if "user" not in session:
        return redirect("/")

    # รับไฟล์จาก form
    file = request.files.get("file")

    if not file or file.filename == "":
        return redirect("/dashboard")

    # ป้องกันชื่อไฟล์อันตราย
    filename = secure_filename(file.filename)

    # บันทึกไฟล์ลงโฟลเดอร์ uploads
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    return redirect("/dashboard")


# ================================
# DOWNLOAD
# ================================
# ดาวน์โหลดไฟล์จากเครื่อง

# ส่วนนี้คือการดาวน์โหลดไฟล์ คำสั่ง retrbinary คือการดึงไฟล์จาก FTP Server กลับมา
@app.route("/download/<filename>")
def download(filename):
    if "user" not in session:
        return redirect("/")

    filename = secure_filename(filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    # ถ้าไฟล์ไม่มีอยู่จริง → 404
    if not os.path.isfile(path):
        abort(404)

    # ส่งไฟล์ให้ผู้ใช้ดาวน์โหลด
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


# ================================
# DELETE
# ================================

# ลบไฟล์ในเครื่อง
@app.route("/delete/<filename>", methods=["POST"])
def delete_file(filename):
    if "user" not in session:
        return redirect("/")

    filename = secure_filename(filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if os.path.isfile(path):
        os.remove(path)

    return redirect("/dashboard")


# ================================
# FTP LOGIN
# ================================

# Login เข้า FTP Server
@app.route("/ftp-login", methods=["POST"])
def ftp_login():
    username = request.form.get("username")
    password = request.form.get("password")

    try:
        # ทดสอบ login FTP
        ftp = FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(username, password)
        ftp.quit()

        # เก็บข้อมูล FTP ลง session
        session["ftp_user"] = username
        session["ftp_pass"] = password

        return redirect("/ftp-dashboard")
    except:
        return "FTP Login Failed"


# ================================
# FTP DASHBOARD
# ================================

# หน้า Dashboard สำหรับจัดการไฟล์บน FTP
@app.route("/ftp-dashboard")
def ftp_dashboard():
    ftp = ftp_connect()
    if not ftp:
        return redirect("/")

    # ดึงรายชื่อไฟล์จาก FTP Server
    files = ftp.nlst()
    ftp.quit()

    return render_template(
        "dashboard.html",
        user=session["ftp_user"],
        files=files,
        mode="ftp"
    )


# ================================
# FTP UPLOAD
# ================================

# อัปโหลดไฟล์ขึ้น FTP Server
@app.route("/ftp-upload", methods=["POST"])
def ftp_upload():
    ftp = ftp_connect()
    if not ftp:
        return redirect("/")

    file = request.files.get("file")
    if not file:
        return redirect("/ftp-dashboard")

    filename = secure_filename(file.filename)

    # ส่งไฟล์ขึ้น FTP แบบ binary
    ftp.storbinary(f"STOR {filename}", file.stream)
    ftp.quit()

    return redirect("/ftp-dashboard")


# ================================
# FTP DOWNLOAD
# ================================

# ดาวน์โหลดไฟล์จาก FTP Server
@app.route("/ftp-download/<filename>")
def ftp_download(filename):
    ftp = ftp_connect()
    if not ftp:
        return redirect("/")

    filename = secure_filename(filename)
    local_path = os.path.join(TEMP_FOLDER, filename)

    # ดึงไฟล์จาก FTP มาเก็บชั่วคราว
    with open(local_path, "wb") as f:
        ftp.retrbinary(f"RETR {filename}", f.write)

    ftp.quit()

    # ส่งไฟล์ให้ผู้ใช้ดาวน์โหลด
    return send_from_directory(TEMP_FOLDER, filename, as_attachment=True)


# ================================
# FTP DELETE
# ================================

# ลบไฟล์บน FTP Server
@app.route("/ftp-delete/<filename>", methods=["POST"])
def ftp_delete(filename):
    ftp = ftp_connect()
    if not ftp:
        return redirect("/")

    filename = secure_filename(filename)
    ftp.delete(filename)
    ftp.quit()

    return redirect("/ftp-dashboard")


# ================================
# LOGOUT
# ================================

# ออกจากระบบ (ล้าง session)
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ================================
# RUN APPLICATION
# ================================

# รัน Flask App
if __name__ == "__main__":
    app.run(debug=True)

# สรุปคือไฟล์ app.py ทำหน้าที่เป็นตัวกลาง รับคำสั่งจากผู้ใช้ผ่านเว็บ แล้วส่งคำสั่งไปยัง FTP Server ที่รันใน Docker เพื่อจัดการไฟล์
# ใช้คำสั่ง docker-compose up คำสั่งนี้ใช้เปิด FTP Server 
# ใช้คำสั่ง python app.py เพื่อรันโปรแกรม