from flask import Blueprint, render_template, request, redirect, session, jsonify, flash
import sqlite3
import os
from werkzeug.utils import secure_filename

recepti_bp = Blueprint("recepti", __name__)

@recepti_bp.route("/recepti")
def recepti():
    if "username" in session:
        username = session["username"]
        if  username == "admin":
            conn = sqlite3.connect('recepti.db')
            c = conn.cursor()
            c.execute("SELECT id, naslov, sestavine, navodila, status FROM recepti")
            recept = c.fetchall()
            conn.close()
            return render_template("recepti.html", recepti=recept)
        
        else:
            return render_template("index.html", username=username)

    else:
        return redirect("/login")
    


@recepti_bp.route("/izbrisi_recept/<int:id>", methods=["POST"])
def izbrisi_recept(id):
    if "username" in session and session["username"] == "admin":
        with sqlite3.connect('recepti.db') as conn:
            c = conn.cursor()
            c.execute("DELETE FROM recepti WHERE id = ?", (id,))
            conn.commit()
        return redirect("/recepti")  
    else:
        return redirect("/login")




@recepti_bp.route("/getDodajRecept", methods=["POST"])
def getDodajRecept():

    naslov = request.form.get("naslov")
    sestavine = request.form.get("sestavine")
    navodila = request.form.get("navodila")
    tezavnost = request.form.get("tezavnost")
    cas_priprave = request.form.get("casPriprave")
    osebe = request.form.get("osebe")
    izpis_sestavin = ""
    seznam_sestavin = []

    seznam_sestavin = sestavine.split("\n")
    for sestavina in seznam_sestavin:
        izpis_sestavin += sestavina + ", "
    

    file = request.files.get("slika")

    filename = None

    if file and file.filename != "":
        filename = secure_filename(file.filename)
        filepath = os.path.join("static/uploads", filename)
        file.save(filepath)

    conn = sqlite3.connect('recepti.db') 
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO recepti 
        (naslov, slika, sestavine, navodila, tezavnost, cas_priprave, osebe)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (naslov, filename, izpis_sestavin, navodila, tezavnost, cas_priprave, osebe))

    conn.commit()
    conn.close()

    flash("Recept je bil uspešno oddan v pregled!")
    return redirect("/")


@recepti_bp.route("/dodajRecept")
def dodajRecept():
    return render_template("dodaj_recept.html")



@recepti_bp.route("/potrdi/<int:id>", methods=["POST"])
def potrdi(id):
    conn = sqlite3.connect("recepti.db")
    c = conn.cursor()
    c.execute("UPDATE recepti SET status='approved' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return "", 204


@recepti_bp.route("/zavrni/<int:id>", methods=["POST"])
def zavrni(id):
    conn = sqlite3.connect("recepti.db")
    c = conn.cursor()
    c.execute("UPDATE recepti SET status='rejected' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return "", 204

@recepti_bp.route("/predlagani_recepti")
def predlagani_recepti():
    conn = sqlite3.connect('recepti.db')
    c = conn.cursor()

    c.execute(""" SELECT naslov, sestavine, navodila, slika, tezavnost, cas_priprave, osebe FROM recepti WHERE status='approved' """)
    recepti = c.fetchall()

    conn.close()

    return render_template("predlagani_recepti.html", recepti=recepti)


@recepti_bp.route("/search")
def search():
    query = request.args.get("q")

    conn = sqlite3.connect("recepti.db")
    c = conn.cursor()

    c.execute("""
        SELECT naslov, sestavine, navodila, slika, tezavnost, cas_priprave, osebe
        FROM recepti
        WHERE naslov LIKE ?
    """, ('%' + query + '%',))

    recepti = c.fetchall()
    conn.close()

    return jsonify(recepti)

  