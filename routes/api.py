from flask import Blueprint, request, jsonify, render_template
from routes.utils import api_request
import random

api_bp = Blueprint("api", __name__)


#glavne funkcije
@api_bp.route("/randomRecipe")
def randomRecipe():
    return render_template("randomRecipe.html")


#dost za dones prisel sem na limit za API
@api_bp.route("/getRandomRecipe")
def getRandomRecipe():
    sestavine = request.args.get("sestavine")
    vrsta = request.args.get("vrsta")
    url = f"https://api.spoonacular.com/recipes/complexSearch?query={sestavine}&cuisine={vrsta}"
    call = api_request(url)

    if call["totalResults"] == 0:
        return jsonify({"message": "Recept s takimi sestavinami ne obstaja."})
    
    else:
        get_recept = random.choice(call["results"])
        id_recepta = get_recept["id"]

        recept_url = f"https://api.spoonacular.com/recipes/{id_recepta}/information?"
        recept = api_request(recept_url)

        amount = []

        for ingredient in recept["extendedIngredients"]:
            if "nameClean" in ingredient:
                amount.append(ingredient["original"])


        #print(ing,amount )

    slika_url = recept.get("image")

    if not slika_url:
        slika_html = '<img src="/static/slike/ni_slike.png" width="300">'
    else:
        slika_html = f'''
        <img src="{slika_url}" width="300"
             onerror="this.onerror=null; this.src='/static/slike/ni_slike.png';">
        '''

    return jsonify({
        "slika": slika_html,
        "ime": recept["title"],
        "ingredients": amount,
        "navodila": recept["instructions"]
    })



@api_bp.route("/getHladilnik")
def getHladilnik():
    sestavina1 = request.args.get("sestavina1")
    sestavina2 = request.args.get("sestavina2")
    sestavina3 = request.args.get("sestavina3")
    sestavina4 = request.args.get("sestavina4")

    sestavine = f"{sestavina1},{sestavina2},{sestavina3},{sestavina4}"

    url = f"https://api.spoonacular.com/recipes/complexSearch?query={sestavine}"
    call = api_request(url)

    if call.get("totalResults", 0) == 0:
        return jsonify({"message": "Recept s takimi sestavinami ne obstaja."})

    id = call["results"][0]["id"]

    url2 = f"https://api.spoonacular.com/recipes/{id}/information?"
    call_recept = api_request(url2)

    amount = []
    for ingredient in call_recept["extendedIngredients"]:
        if "nameClean" in ingredient:
            amount.append(ingredient["original"])

    return jsonify({
        "slika": f'<img src="{call_recept["image"]}">',
        "ime": call_recept["title"],
        "sestavine": amount,
        "navodila": call_recept["instructions"]
    })

    
@api_bp.route("/hladilnik")
def hladilnik():
    return render_template("hladilnik.html")


@api_bp.route("/getInfo")
def getInfo():
    sestavina = request.args.get("sestavina")

    url = f"https://api.spoonacular.com/food/ingredients/search?query={sestavina}"
    call = api_request(url)

    id_sestavine = call["results"][0]["id"]

    url_info = f"https://api.spoonacular.com/food/ingredients/{id_sestavine}/information?amount=1"
    call_info = api_request(url_info)

    sez_info = [
        "Protein",
        "Carbohydrates",
        "Fiber",
        "Fat",
        "Sugar",
        "Calories",
        "Vitamin C",
        "Vitamin A",
        "Vitamin B6",
        "Vitamin B12",
        "Iron",
        "Magnesium",
        "Potassium",
        "Calcium"
    ]

    nutrition = {
        "name": call_info["name"]
    }

    for item in call_info["nutrition"]["nutrients"]:
        if item["name"] in sez_info:
            nutrition[item["name"]] = {
                "amount": item["amount"],
                "unit": item["unit"]
            }

    print(nutrition)
    return jsonify(nutrition)


@api_bp.route("/info")
def info():
    return render_template("info_sestavine.html")



@api_bp.route("/getIdSearch")
def getIdSearch():

    id = request.args.get("id")
    url = f"https://api.spoonacular.com/recipes/{id}/information?"
    call = api_request(url)
    #nedelujoc id: 154726

    if "extendedIngredients" not in call:
        return jsonify({
            "message": "Napaka pri pridobivanju recepta (ID ne obstaja)"
        })

    amount = []
    for ingredient in call["extendedIngredients"]:
        if "nameClean" in ingredient:
            amount.append(ingredient["original"])


    #print(ing,amount )

    return jsonify({"slika": f'<img src={call["image"]}>',
                    "ime": call["title"],
                    "ingredients": amount,
                    "navodila": call["instructions"]})


@api_bp.route("/idSearch")
def idSearch():
    return render_template("id_search.html")

@api_bp.route("/pretvori")
def pretvori():
    return render_template("pretvori.html")


@api_bp.route("/getPretvori")
def getPretvori():

    ing = request.args.get("ing") + " "
    amount = request.args.get("amount")
    enota = request.args.get("enota")
    pretvorjena = request.args.get("pretvorjena")
    url = f"https://api.spoonacular.com/recipes/convert?ingredientName={ing}&sourceAmount={amount}&sourceUnit={enota}&targetUnit={pretvorjena}"
    call = api_request(url)

    #print(call)
    if "answer" not in call:
        return "Napaka pri pretvorbi (napačni podatki)"

    return call["answer"]


@api_bp.route("/getZdravi")
def getZdravi():
    proteini = request.args.get("proteini")
    mascobe = request.args.get("mascobe")
    kalorije = request.args.get("kalorije")

    if proteini == "":
        proteini = 0

    if mascobe == "":
        mascobe = 0

    if kalorije == "":
        kalorije = 800


    #print(proteini,mascobe,kalorije)
    api2 = f"c3903212f7594031bab178a65e5940a1"
    # testni url = f"https://api.spoonacular.com/recipes/complexSearch?query={sestavine}&cuisine={vrsta}&apiKey={api2}"
    url2 = f"https://api.spoonacular.com/recipes/complexSearch?minProtein={proteini}&maxCalories={kalorije}&minFat={mascobe}&apiKey={api2}"
    call = api_request(url2)
    #print(call)

    if call["totalResults"] == 0:
        return jsonify({'message': "Ustreznih receptov ni bilo najdenih."})
    
    else:
        sez_recipes = []

        for recipe in call["results"]:
            recipe_info = {
                "id": recipe["id"],
                "title": recipe["title"],
                "calories": None,
                "protein": None
            }

            for nutrient in recipe["nutrition"]["nutrients"]:
                if nutrient["name"] == "Calories":
                    recipe_info["calories"] = nutrient["amount"]
                if nutrient["name"] == "Protein":
                    recipe_info["protein"] = nutrient["amount"]

            sez_recipes.append(recipe_info)

        #(sez_recipes)
        return jsonify({'recipes': sez_recipes})

@api_bp.route("/zdravi")
def zdravi():
    return render_template("zdravi_obrok.html")