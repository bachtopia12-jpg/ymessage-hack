from flask import Flask, render_template, request, redirect, session, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config['SECRET_KEY'] = 'R09maW5nQG9uZQ=='
socketio = SocketIO(app)

salles = {}

def générer_code_unique(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in salles:
            break
    
    return code

@app.route("/", methods=["GET", "POST"])
def accueil():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("accueil.html", error="Veuillez entrer un nom.", code=code, name=name)

        if join != False and not code:
            return render_template("accueil.html", error="Veuillez entrer un code de salle.", code=code, name=name)
        
        salle = code
        if create != False:
            salle = générer_code_unique(4)
            salles[salle] = {"membres": 0, "messages": []}
        elif code not in salles:
            return render_template("accueil.html", error="Cette salle n'existe pas.", code=code, name=name)
        
        session["salle"] = salle
        session["name"] = name
        return redirect(url_for("salle"))

    return render_template("accueil.html")

@app.route("/salle")
def salle():
    salle = session.get("salle")
    if salle is None or session.get("name") is None or salle not in salles:
        return redirect(url_for("accueil"))

    return render_template("salle.html", 
                         code=salle, 
                         messages=salles[salle]["messages"])

@socketio.on("message")
def message(données):
    salle = session.get("salle")
    if salle not in salles:
        return 
    
    contenu = {
        "name": session.get("name"),
        "message": données["data"]
    }
    send(contenu, to=salle)
    salles[salle]["messages"].append(contenu)
    print(f"{session.get('name')} a dit : {données['data']}")

@socketio.on("connect")
def connecter(auth):
    salle = session.get("salle")
    name = session.get("name")
    if not salle or not name:
        return
    if salle not in salles:
        leave_room(salle)
        return
    
    join_room(salle)
    send({"name": name, "message": "a rejoint la salle"}, to=salle)
    salles[salle]["membres"] += 1
    print(f"{name} a rejoint la salle {salle}")

@socketio.on("disconnect")
def déconnecter():
    salle = session.get("salle")
    name = session.get("name")
    leave_room(salle)

    if salle in salles:
        salles[salle]["membres"] -= 1
        if salles[salle]["membres"] <= 0:
            del salles[salle]
    
    send({"name": name, "message": "a quitté la salle"}, to=salle)
    print(f"{name} a quitté la salle {salle}")

if __name__ == '__main__':
    socketio.run(app, debug=True)