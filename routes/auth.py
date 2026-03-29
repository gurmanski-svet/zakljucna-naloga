from flask import Blueprint, render_template, request, jsonify, session, redirect
import sqlite3
import bcrypt

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        mail = request.form.get("mail")
        geslo = request.form.get("geslo")

        geslo_utf = geslo.encode('utf-8')
        hash_geslo = bcrypt.hashpw(geslo_utf, bcrypt.gensalt()).decode('utf-8')


        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        if username == "" or mail == "" or geslo == "":
            return jsonify({"message": "Izpolni vsa polja", "povezava": "/register"})

        if "@" not in mail and "." not in mail:
            return jsonify({"message": "Vnesi veljaven mail", "povezava": "/register"})

        c.execute("SELECT username FROM users WHERE username = ?", (username,))
        if c.fetchone():
            conn.close()
            return jsonify({"message": "Uporabnisko ime ze obstaja", "povezava": "/register"})

        c.execute("SELECT mail FROM users WHERE mail = ?", (mail,))
        if c.fetchone():
            conn.close()
            return jsonify({"message": "Registracija uspesna!", "povezava": "/register"})

        c.execute("INSERT INTO users (username, mail, geslo) VALUES (?, ?, ?)", (username, mail, hash_geslo))
        conn.commit()
        conn.close()
        return jsonify({"message": "Registracija uspesna!", "povezava": "/login"})
        
    
    else:
        return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        geslo = request.form.get("geslo")

        geslo_utf = geslo.encode('utf-8')

        baza = sqlite3.connect('users.db')
        c = baza.cursor()
        c.execute("SELECT username, geslo FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        baza.close()

        if user is not None:
            db_username = user[0]
            db_hash = user[1] 

            if bcrypt.checkpw(geslo_utf, db_hash.encode('utf-8')):  

                session["username"] = db_username
                return jsonify({"message": "Prijava uspešna!", "povezava": "/"})
            else:
                return jsonify({"message": "Napačno geslo.", "povezava": "/login"})
        else:
            return jsonify({"message": "Napačno uporabniško ime ali geslo.", "povezava": "/login"})



    else:
        return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")