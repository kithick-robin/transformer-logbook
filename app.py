from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    return sqlite3.connect("database.db")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.form

        con = get_db()
        cur = con.cursor()

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
            result TEXT
        )
        """)

        # PASS / FAIL LOGIC (simple & viva-friendly)
        result = "PASS"
        if float(data["ir_hv"]) < 200 or float(data["ir_lv"]) < 200:
            result = "FAIL"
        if float(data["ttr"]) < 0.98 or float(data["ttr"]) > 1.02:
            result = "FAIL"

        cur.execute("""
        INSERT INTO transformer
        (rating, hv, lv, vector, ir_hv, ir_lv, wr_hv, wr_lv, ttr, result)
        VALUES (?,?,?,?,?,?,?,?,?,?)
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
            result
        ))

        con.commit()
        con.close()
        return redirect("/report")

    return render_template("index.html")

@app.route("/report")
def report():
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM transformer ORDER BY id DESC LIMIT 1")
    data = cur.fetchone()
    con.close()
    return render_template("report.html", data=data)
    if __name__ == "__main__":
    app.run()
