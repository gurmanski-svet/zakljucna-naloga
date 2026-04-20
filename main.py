from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, redirect, session
import os
from supabase import create_client, Client
from routes.auth import auth_bp
from routes.api import api_bp
from routes.recepti import recepti_bp


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_key")

# registracija blueprintov
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)
app.register_blueprint(recepti_bp)

#supabase povezava
#url: str = "https://vraixcshjsgfobltfvpu.supabase.co"
#key: str = "sb_publishable_i4bIososUGqTVjhVGjZu_Q_x7UkMYYw"

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.route("/dashboard")
def dashboard():
    if "username" in session:
        username = session["username"]
        if  username == "admin":
            return render_template("dashboard.html", username=username)
        else:
            return render_template("index.html", username=username)
        
    else:
        return redirect("/login")

@app.route("/uporabniki")
def uporabniki():
    if "username" in session:
        username = session["username"]
        if  username == "admin":
            response = supabase.table("users").select("id, username, mail").execute()
            users = response.data

            return render_template("uporabniki.html", users=users)
        
        else:
            return render_template("index.html", username=username)

    else:
        return redirect("/login")




@app.route("/izbrisi/<int:id>", methods=["POST"])
def izbrisi(id):
    if "username" not in session:
        return redirect("/")

    if session["username"] != "admin":
        return redirect("/")

    supabase.table("users").delete().eq("id", id).execute()
    return redirect("/uporabniki")


@app.context_processor
def inject_user():
    return dict(username=session.get("username"))

#---------------druge strani-------------------
#------------------------------------------------------
#------------------------------------------------------
@app.route("/")
def index():
    if "username" in session:
        username = session["username"]
        if  username == "admin":
            return render_template("admin_index.html", username=username)
        else:
            return render_template("index.html", username=username)
    
    else:
        return render_template("index.html")


@app.route("/getKalkulator")
def getKalkulator():
    kolicina1 = request.args.get("kolicina1")
    kolicina2 = request.args.get("kolicina2")
    kolicina3 = request.args.get("kolicina3")
    kolicina4 = request.args.get("kolicina4")
    kolicina5 = request.args.get("kolicina5")
    kolicina6 = request.args.get("kolicina6")

    stevilo = request.args.get("stevilo")


    sez_kolicin = [kolicina1, kolicina2, kolicina3, kolicina4, kolicina5, kolicina6]
    pretvorjene = []

    for sestavina in sez_kolicin:
        if sestavina == "":
            pretvorjene.append(0)
        else:
            pretvorjene.append(round(int(sestavina) / int(stevilo)))


    print(pretvorjene)

    return {"pretvorjene": pretvorjene}


@app.route("/kalkulator")
def kalkulator():
    return render_template("kalkulator.html")


@app.route("/getTecaji")
def getTecaji():
    return "x"

@app.route("/tecaji")
def tecaji():
    return render_template("kuharski_tecaji.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

    #app.run(debug=True)