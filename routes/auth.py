from flask import Blueprint, render_template, request, session, redirect, flash
import bcrypt
from db import supabase

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        mail = request.form.get("mail")
        geslo = request.form.get("geslo")

        if not username or not mail or not geslo:
            flash("Izpolni vsa polja.")
            return redirect("/register")

        if "@" not in mail or "." not in mail:
            flash("Vnesi veljaven email.")
            return redirect("/register")

        user_check = supabase.table("users") \
            .select("username") \
            .eq("username", username) \
            .execute()

        if user_check.data:
            flash("Uporabniško ime že obstaja.")
            return redirect("/register")

        mail_check = supabase.table("users") \
            .select("mail") \
            .eq("mail", mail) \
            .execute()

        if mail_check.data:
            flash("Email že obstaja.")
            return redirect("/register")

        hash_geslo = bcrypt.hashpw(
            geslo.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        supabase.table("users").insert({
            "username": username,
            "mail": mail,
            "geslo": hash_geslo
        }).execute()

        flash("Registracija uspešna! Sedaj se lahko prijaviš.")
        return redirect("/login")

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        geslo = request.form.get("geslo")

        response = supabase.table("users") \
            .select("username, geslo") \
            .eq("username", username) \
            .execute()

        if not response.data:
            flash("Napačno uporabniško ime ali geslo.")
            return redirect("/login")

        user = response.data[0]
        db_hash = user["geslo"]

        if not bcrypt.checkpw(
            geslo.encode("utf-8"),
            db_hash.encode("utf-8")
        ):
            flash("Napačno uporabniško ime ali geslo.")
            return redirect("/login")

        session["username"] = user["username"]
        flash("Uspešno si se prijavil.")
        return redirect("/")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Odjavljen si.")
    return redirect("/login")