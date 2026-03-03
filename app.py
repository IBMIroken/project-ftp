# ภาพรวมของระบบเว็บ ระบบนี้เป็น เว็บแอปพลิเคชันสำหรับจัดการไฟล์ ผู้ใช้ต้องเข้าสู่ระบบก่อน จึงจะสามารถจัดการไฟล์ได้ 
# ความสามารถของระบบเว็บคือ สมัครสมาชิก เข้าสู่ระบบ แสดงรายการไฟล์ อัปโหลดไฟล์ ดาวน์โหลดไฟล์ ลบไฟล์ ออกจากระบบ
# app.py เป็นไฟล์หลักของเว็บแอปพลิเคชัน ทำหน้าที่รับคำสั่งจากผู้ใช้ผ่านหน้าเว็บ และจัดการไฟล์บนระบบของเว็บโดยตรง
# Flask → ใช้สร้าง Web Application
# request → รับข้อมูลจาก form (POST/GET)
# render_template → แสดงหน้า HTML
# redirect → เปลี่ยนหน้าเว็บ
# session → เก็บสถานะการ login
# send_from_directory → ส่งไฟล์ให้ดาวน์โหลด
# abort → ใช้ส่ง error เช่น 404


# กลุ่มที่ 1: โค้ดเตรียมเครื่องมือสำหรับระบบเว็บ
# *---* โค้ดกลุ่มนี้เป็นการเตรียมเครื่องมือที่ระบบเว็บต้องใช้ทั้งหมด เช่น ใช้สร้างเว็บและหน้าเว็บต่าง ๆ ใช้รับข้อมูลจากผู้ใช้ผ่านฟอร์ม ใช้แสดงหน้าเว็บ 
# ใช้เปลี่ยนหน้าเว็บ ใช้จดจำสถานะการเข้าสู่ระบบของผู้ใช้ ใช้ส่งไฟล์ให้ผู้ใช้ดาวน์โหลด ใช้จัดการไฟล์และโฟลเดอร์ในเครื่อง ใช้ป้องกันชื่อไฟล์ที่ไม่ปลอดภัย 
# ถ้าไม่มีโค้ดกลุ่มนี้ ระบบเว็บจะไม่สามารถทำงานได้ *---*

from flask import Flask, request, render_template, redirect, session, send_from_directory, abort
from werkzeug.utils import secure_filename
from ftplib import FTP
import os

# ================================
# สร้าง Flask Application
# ================================

# สร้าง Web Application ด้วย Flask
# secret_key ใช้สำหรับเข้ารหัส session
# ถ้าไม่มี secret_key ระบบ login จะไม่ทำงาน

# กลุ่มที่ 2: โค้ดสร้างเว็บแอปพลิเคชัน
# *---* โค้ดกลุ่มนี้เป็นการสร้างตัวเว็บแอปพลิเคชัน บรรทัดแรก คือการสร้างเว็บขึ้นมา บรรทัดที่สอง ใช้ตั้งค่ารหัสลับสำหรับระบบจดจำผู้ใช้ 
# โค้ดส่วนนี้สำคัญมาก เพราะถ้าไม่มี ระบบเข้าสู่ระบบจะใช้งานไม่ได้ *---*

app = Flask(__name__)
app.secret_key = "secret123"


# ================================
# การตั้งค่าโฟลเดอร์
# ================================

# กลุ่มที่ 3: โค้ดกำหนดโฟลเดอร์สำหรับเว็บ
# *---* โค้ดกลุ่มนี้ใช้กำหนดพื้นที่เก็บไฟล์ของระบบเว็บ 
# โฟลเดอร์แรก ใช้เก็บไฟล์ที่ผู้ใช้อัปโหลดผ่านหน้าเว็บ 
# โฟลเดอร์ที่สอง ใช้เก็บไฟล์ชั่วคราว และมีการบอกระบบเว็บว่า ถ้าจะจัดการไฟล์อัปโหลด ให้ไปใช้โฟลเดอร์นี้ *---*

UPLOAD_FOLDER = "uploads"
TEMP_FOLDER = "temp"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ================================
# การตั้งค่า FTP Server
# ================================

# ตรงนี้คือการตั้งค่าที่อยู่ของระบบเก็บไฟล์ ซึ่งรันอยู่เครื่องเดียวกันผ่าน Docker
FTP_HOST = "localhost"
FTP_PORT = 21


# ================================
# สร้างโฟลเดอร์ถ้ายังไม่มี
# ================================

# กลุ่มที่ 4: โค้ดเตรียมโฟลเดอร์อัตโนมัติ
# *---* โค้ดกลุ่มนี้ทำหน้าที่ตรวจสอบโฟลเดอร์ ถ้ายังไม่มี จะสร้างให้เอง ถ้ามีอยู่แล้ว จะไม่เกิดข้อผิดพลาด ช่วยให้ระบบพร้อมใช้งานทันทีตั้งแต่เปิดครั้งแรก *---*

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

# ================================
# ฟังก์ชันเชื่อมต่อ FTP
# ================================

# ฟังก์ชันนี้ใช้เชื่อมต่อไปยัง FTP Server โดยใช้ username และ password ถ้าเชื่อมต่อสำเร็จระบบจะสามารถสั่งงาน FTP หรือก็คือเข้าไปใช้งานได้
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

# กลุ่มที่ 5: โค้ดระบบเข้าสู่ระบบของผู้ใช้
# *---* โค้ดกลุ่มนี้เป็นหน้าแรกของเว็บ ใช้สำหรับให้ผู้ใช้เข้าสู่ระบบ ระบบจะ รับชื่อผู้ใช้และรหัสผ่าน ตรวจสอบข้อมูลผู้ใช้ ถ้าถูกต้อง จะเข้าสู่หน้าใช้งานหลัก
# จะบันทึกข้อมูลผู้ใช้ไว้ในไฟล์ users.txt *---*

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # รับข้อมูลจาก form
        username = request.form.get("username") # ระบบจะนำข้อมูลที่ผู้ใช้กรอกไปตรวจสอบกับข้อมูลผู้ใช้ที่มีอยู่ในระบบ
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
                    session["user"] = username # เมื่อเข้าสู่ระบบสำเร็จ ระบบจะ “จำผู้ใช้ไว้” และพาไปหน้าแดชบอร์ด
                    return redirect("/dashboard")

        # ถ้า login ไม่ผ่าน
        return "Login Failed"

    # แสดงหน้า login.html
    return render_template("login.html")


# ================================
# REGISTER 
# ================================

#กลุ่มที่ 6: โค้ดระบบสมัครสมาชิก
# *---* อันนี้ก็เหมือนกัน แต่เป็นการสมัครสมาชิก จะบันทึกข้อมูลลงไฟล์ users.txt และตรวจสอบว่ามี username ซ้ำหรือไม่ ถ้ามีจะไม่ให้สมัครซ้ำ 
# โค้ดกลุ่มนี้ใช้สำหรับสมัครสมาชิกใหม่ตรวจสอบชื่อผู้ใช้ซ้ำบันทึกข้อมูลผู้ใช้กลับไปหน้าเข้าสู่ระบบหลังสมัครเสร็จ*---*

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

# กลุ่มที่ 7: โค้ดหน้าแสดงรายการไฟล์
# *---* โค้ดกลุ่มนี้เป็นหน้าใช้งานหลักหลังจากเข้าสู่ระบบแสดงรายชื่อไฟล์ทั้งหมดเตรียมข้อมูลส่งไปแสดงบนหน้าเว็บ *---*

@app.route("/dashboard")
def dashboard():
    
# กลุ่มที่ 8: โค้ดควบคุมสิทธิ์การใช้งาน
# *---* โค้ดชุดนี้ใช้ตรวจสอบว่าผู้ใช้เข้าสู่ระบบแล้วหรือยังถ้ายังไม่ได้เข้าสู่ระบบจะไม่อนุญาตให้ใช้งานหน้าเว็บนั้น *---*

    if "user" not in session: # นี่คือระบบควบคุมสิทธิ์ ถ้ายังไม่ล็อกอิน ระบบจะพากลับไปหน้าแรกทันที
        return redirect("/")

    # ดึงรายชื่อไฟล์จากโฟลเดอร์ uploads
    files = [
        f for f in os.listdir(app.config["UPLOAD_FOLDER"]) # ระบบจะไปดูว่าในโฟลเดอร์เก็บไฟล์ มีไฟล์อะไรอยู่บ้าง แล้วเอามาแสดงบนหน้าเว็บ
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

# กลุ่มที่ 9: โค้ดอัปโหลดไฟล์ผ่านเว็บ
# *---* ส่วนนี้คือการอัปโหลดไฟล์ผ่านหน้าเว็บ ระบบจะรับไฟล์จากผู้ใช้ และบันทึกลงโฟลเดอร์ uploads *---*
# ระบบจะไปดูว่าในโฟลเดอร์เก็บไฟล์ มีไฟล์อะไรอยู่บ้าง แล้วเอามาแไฟล์จะถูกบันทึกลงในโฟลเดอร์ที่ระบบกำหนดไว้และเมื่อกลับมาหน้าแดชบอร์ดไฟล์ใหม่จะปรากฏทันที

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

# กลุ่มที่ 10: โค้ดดาวน์โหลดไฟล์
# *---* ส่วนนี้คือการดาวน์โหลดไฟล์เว็บจะส่งไฟล์ให้ผู้ใช้ดาวน์โหลดโดยตรง *---*
# ระบบจะตรวจสอบก่อนว่าไฟล์มีอยู่จริงแล้วส่งไฟล์ให้ผู้ใช้ดาวน์โหลดทันที

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

# กลุ่มที่ 11: โค้ดลบไฟล์
# *---* ส่วนนี้ใช้ลบไฟล์ออกจากระบบเมื่อผู้ใช้กดลบผ่านหน้าเว็บ *---*
# ไฟล์จะถูกลบออกจากระบบจริง ๆ และจะไม่แสดงในหน้าแดชบอร์ดอีก

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

# กลุ่มที่ 12: โค้ดออกจากระบบ
# *---* โค้ดกลุ่มนี้ใช้สำหรับออกจากระบบล้างข้อมูลการเข้าสู่ระบบทั้งหมดกลับไปหน้าแรกของเว็บ *---*
# หลังออกจากระบบผู้ใช้จะต้องล็อกอินใหม่เท่านั้นถึงจะกลับมาใช้งานได้
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ================================
# RUN APPLICATION
# ================================

# กลุ่มที่ 13: โค้ดเริ่มทำงานของระบบ
# *---* โค้ดกลุ่มนี้ใช้เริ่มการทำงานของเว็บแอปพลิเคชัน เมื่อรันไฟล์ ระบบเว็บจะพร้อมใช้งานทันที *---*
if __name__ == "__main__":
    app.run(debug=True)


# สรุปคือไฟล์ app.py ทำหน้าที่เป็นตัวกลาง รับคำสั่งจากผู้ใช้ผ่านเว็บ แล้วส่งคำสั่งไปยัง FTP Server ที่รันใน Docker เพื่อจัดการไฟล์
# ใช้คำสั่ง docker-compose up คำสั่งนี้ใช้เปิด FTP Server 
# ใช้คำสั่ง python app.py เพื่อรันโปรแกรม

# ระบบจะเริ่มจากหน้าเข้าสู่ระบบ ถ้าล็อกอินผ่าน จะพาไปหน้าแดชบอร์ด จากนั้นผู้ใช้สามารถจัดการไฟล์ได้ 
# ทุกหน้าจะมีการตรวจสอบสิทธิ์ และเมื่อออกจากระบบ ระบบจะพากลับไปหน้าแรกทันที