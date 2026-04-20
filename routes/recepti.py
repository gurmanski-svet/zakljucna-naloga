from flask import Blueprint, render_template, request, redirect, session, jsonify, flash
from werkzeug.utils import secure_filename
from supabase import create_client, Client

recepti_bp = Blueprint("recepti", __name__)


url: str = "https://vraixcshjsgfobltfvpu.supabase.co"
key: str = "sb_publishable_i4bIososUGqTVjhVGjZu_Q_x7UkMYYw"
supabase: Client = create_client(url, key)

@recepti_bp.route("/recepti")
def recepti():
    if "username" in session:
        username = session["username"]
        if  username == "admin":
            response = supabase.table("recepti") \
                .select("id, naslov, sestavine, navodila, status") \
                .execute()

            recept = response.data
            return render_template("recepti.html", recepti=recept)
        
        else:
            return render_template("index.html", username=username)

    else:
        return redirect("/login")
    


@recepti_bp.route("/izbrisi_recept/<int:id>", methods=["POST"])
def izbrisi_recept(id):
    if "username" in session and session["username"] == "admin":
        supabase.table("recepti").delete().eq("id", id).execute()
        return redirect("/recepti")  
    else:
        return redirect("/login")




@recepti_bp.route("/getDodajRecept", methods=["POST"])
def getDodajRecept():
    if "username" not in session:
        flash("Za dodajanje recepta se prijavi.")
        return redirect("/login")

    naslov = request.form.get("naslov")
    sestavine = request.form.get("sestavine")
    navodila = request.form.get("navodila")
    tezavnost = request.form.get("tezavnost")
    cas_priprave = request.form.get("casPriprave")
    osebe = request.form.get("osebe")

    izpis_sestavin = "<br>".join(sestavine.split("\n"))

    file = request.files.get("slika")
    image_url = None

    if file and file.filename != "":
        filename = secure_filename(file.filename)

        supabase.storage.from_("slike").upload(filename, file)

        image_url = supabase.storage.from_("slike").get_public_url(filename)

    supabase.table("recepti").insert({
        "naslov": naslov,
        "slika": image_url,
        "sestavine": izpis_sestavin,
        "navodila": navodila,
        "tezavnost": tezavnost,
        "cas_priprave": cas_priprave,
        "osebe": osebe,
        "status": "pending"
    }).execute()

    flash("Recept je bil uspešno oddan v pregled!")
    return redirect("/")


@recepti_bp.route("/dodajRecept")
def dodajRecept():
    if "username" not in session:
        flash("Za dodajanje recepta se moraš prijaviti.")
        return redirect("/login")
    return render_template("dodaj_recept.html")



@recepti_bp.route("/potrdi/<int:id>", methods=["POST"])
def potrdi(id):
    if "username" not in session or session["username"] != "admin":
        return "Unauthorized", 403

    supabase.table("recepti") \
    .update({"status": "approved"}) \
    .eq("id", id) \
    .execute()
    return "", 204


@recepti_bp.route("/zavrni/<int:id>", methods=["POST"])
def zavrni(id):
    if "username" not in session or session["username"] != "admin":
        return "Unauthorized", 403
    
    supabase.table("recepti") \
        .update({"status": "rejected"}) \
        .eq("id", id) \
        .execute()
    return "", 204

@recepti_bp.route("/predlagani_recepti")
def predlagani_recepti():
    response = supabase.table("recepti") \
    .select("naslov, sestavine, navodila, slika, tezavnost, cas_priprave, osebe") \
    .eq("status", "approved") \
    .execute()

    recepti = response.data

    return render_template("predlagani_recepti.html", recepti=recepti)


@recepti_bp.route("/search")
def search():
    query = request.args.get("q")

    response = supabase.table("recepti") \
        .select("naslov, sestavine, navodila, slika, tezavnost, cas_priprave, osebe") \
        .ilike("naslov", f"%{query}%") \
        .execute()

    return jsonify(response.data)



  