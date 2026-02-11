from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__, template_folder="templates")

DB_NAME = "/tmp/database.db"

def get_db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.form

        con = get_db()
        cur = con.cursor()

        # Create table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS transformer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rating TEXT,
            hv TEXT,
            lv TEXT,
            vector TEXT,
            ir_hv REAL,
            ir_lv REAL,
            wr_hv REAL,
            wr_lv REAL,
            ttr REAL,
            result TEXT,
            diagnosis TEXT
        )
        """)

        result = "PASS"
        diagnosis_list = []

        # IR Check
        if float(data["ir_hv"]) < 200 or float(data["ir_lv"]) < 200:
            result = "FAIL"
            diagnosis_list.append("Low Insulation Resistance → Possible insulation deterioration")

        # TTR Check
        if float(data["ttr"]) < 0.98 or float(data["ttr"]) > 1.02:
            result = "FAIL"
            diagnosis_list.append("TTR Deviation → Possible tap changer issue")

        # WR Check
        if float(data["wr_hv"]) <= 0 or float(data["wr_lv"]) <= 0:
            result = "FAIL"
            diagnosis_list.append("Abnormal Winding Resistance → Loose joint or bad contact")

        if result == "PASS":
            diagnosis = "All parameters within acceptable limits."
        else:
            diagnosis = " | ".join(diagnosis_list)

        cur.execute("""
        INSERT INTO transformer
        (rating, hv, lv, vector, ir_hv, ir_lv, wr_hv, wr_lv, ttr, result, diagnosis)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data["rating"],
            data["hv"],
            data["lv"],
            data["vector"],
            data["ir_hv"],
            data["ir_lv"],
            data["wr_hv"],
            data["wr_lv"],
            data["ttr"],
            result,
            diagnosis
        ))

        con.commit()
        con.close()

        return redirect(url_for("report"))

    return render_template("index.html")

@app.route("/report")
def report():
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM transformer ORDER BY id DESC LIMIT 1")
    data = cur.fetchone()
    con.close()
    return render_template("report.html", data=data)

