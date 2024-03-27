from flask import Flask, render_template, request, session, jsonify,redirect, url_for

app = Flask(__name__)
app.secret_key = 'azerty123@'

def total_to_time(total):
    heures=total//3600
    rest=total%3600
    minutes=rest//60
    secondes=rest%60
    if(heures<10):
        heures="0"+str(heures)
    if(minutes<10):
        minutes="0"+str(minutes)
    if(secondes<10):
        secondes="0"+str(secondes)
    return heures,minutes,secondes

@app.before_request
def before_request():
    session.modified = True
    
@app.route('/exit', methods=['GET', 'POST'])
def exit():
    session.pop('azerty123@',None)
    session.clear()
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/start_timer', methods=['GET', 'POST'])
def start_timer():
    if request.method == 'POST':  # Vérifier si le formulaire a été soumis
        work_time = request.form.get('work_time')
        rest_time_sets = request.form.get('rest_time_sets')
        rest_time_exercises = request.form.get('rest_time_exercises')
        sets = request.form.get('sets')
        exercises = request.form.get('exercises')

        if not all([work_time, rest_time_sets, rest_time_exercises, sets, exercises]):
            # Si l'un des champs du formulaire est vide
            return redirect(url_for('index'))
        # Convertir les valeurs en entiers
        work_time = int(work_time)
        rest_time_sets = int(rest_time_sets)
        rest_time_exercises = int(rest_time_exercises)
        sets = int(sets)
        exercises = int(exercises)

        # Ajouter les données à la session
        session['initial_work_time'] = work_time
        session['initial_rest_time_sets'] = rest_time_sets
        session['initial_rest_time_exercises'] = rest_time_exercises
        session['initial_sets'] = sets
        session['initial_exercises_per_set'] = exercises

        # Calculer d'autres valeurs de session
        total_time_per_set = (work_time + rest_time_exercises) * exercises
        total_rest_time_between_sets = rest_time_sets * (sets - 1)
        session['initial_total_work_time'] = (total_time_per_set * sets) + total_rest_time_between_sets
        session["initial_total_time_h"], session["initial_total_time_min"], session["initial_total_time_s"] = total_to_time(session["initial_total_work_time"])


        session["total_exercises"]=session["initial_exercises_per_set"]*session["initial_sets"];
        session['work_time'] = work_time + 1
        session['rest_time'] = rest_time_exercises + 1
        session['sets'] = 0
        session['exercises_per_set'] = 0
        session["total_work_time"] = 0

        # Convertir le temps en heures, minutes, secondes et ajouter à la session
        session["initial_work_time_h"], session["initial_work_time_min"], session["initial_work_time_s"] = total_to_time(work_time)
        session["initial_rest_exe_h"], session["initial_rest_ex_min"], session["initial_rest_ex_s"] = total_to_time(rest_time_exercises)

        # Rediriger vers la route timer
        return redirect(url_for('timer'))
    else:
        # Si la méthode de la requête n'est pas POST, rediriger vers la page d'accueil
        return redirect(url_for('index'))


@app.route('/timer', methods=['GET', 'POST'])
def timer():
    if 'initial_work_time' not in session:
        return redirect(url_for('index'))
    return render_template('timer.html',work_time=1,rest_time=0)

@app.route('/reload_timer', methods=['GET', 'POST'])
def reload_timer():
    if 'initial_work_time' not in session:
        return redirect(url_for('index'))
    total_time_per_set = (session["initial_work_time"] + session["initial_rest_time_exercises"]) * session["initial_exercises_per_set"]
    total_rest_time_between_sets = session["initial_rest_time_sets"] * (session["initial_sets"] - 1)
    session['initial_total_work_time'] = (total_time_per_set * session["initial_sets"]) + total_rest_time_between_sets
    
    session['work_time']=session['initial_work_time']+1
    session['rest_time']=session['initial_rest_time_exercises']+1
    session['sets']= 0
    session['exercises_per_set']=0
    session["total_work_time"]=0

    heures,minutes,secondes=total_to_time(session["initial_work_time"])
    session["initial_work_time_h"],session["initial_work_time_min"],session["initial_work_time_s"]=heures,minutes,secondes
    heures,minutes,secondes=total_to_time(session["initial_rest_time_exercises"])
    session["initial_rest_exe_h"],session["initial_rest_ex_min"],session["initial_rest_ex_s"]=heures,minutes,secondes
    return render_template('timer.html',work_time=1,rest_time=0)


# Fonction pour mettre à jour le temps de travail
def update_work():
    timer=True
    session["work_time"] -= 1
    session["total_work_time"]+=1
    total_time=session["total_work_time"]
    total_work_time = session["work_time"]
    if total_work_time > 0:
        work_time = True
        rest_time = False
    else:
        work_time = False
        rest_time = True
        if session["exercises_per_set"] < session["initial_exercises_per_set"]:
            session["exercises_per_set"] += 1
            if session["exercises_per_set"] == session["initial_exercises_per_set"]:
                if session["sets"] < session["initial_sets"] - 1:
                    session["sets"] += 1
                    session["rest_time"]=session['initial_rest_time_sets']+1
                else:
                    session["sets"] = session["initial_sets"]
                    session["exercises_per_set"] = session["initial_exercises_per_set"]
                    timer=False
                    rest_time=False 
                    work_time=False
        session['work_time']=session['initial_work_time']+1
    heures, minutes, secondes = total_to_time(total_work_time)
    total_heures,total_minutes,total_secondes=total_to_time(total_time)
    return heures, minutes, secondes, work_time, rest_time,total_time,total_heures,total_minutes,total_secondes,timer

# Fonction pour mettre à jour le temps de repos
def update_rest():
    session["rest_time"] -= 1
    session["total_work_time"]+=1
    total_time=session["total_work_time"]
    total_rest_time = session["rest_time"]
    if total_rest_time > 0:
        work_time = False
        rest_time = True
    else:
        session['rest_time']=session['initial_rest_time_exercises'] +1
        if session["exercises_per_set"] == session["initial_exercises_per_set"] and session["sets"] < session["initial_sets"]:
            session["exercises_per_set"] = 0
        work_time = True
        rest_time = False
    heures, minutes, secondes = total_to_time(total_rest_time)
    total_heures,total_minutes,total_secondes=total_to_time(total_time)
    return heures, minutes, secondes, work_time, rest_time,total_time,total_heures,total_minutes,total_secondes

# Route pour mettre à jour le temps de travail
@app.route("/update_work_time", methods=['GET', 'POST'])
def update_work_route():
    if 'initial_work_time' not in session:
        return redirect(url_for('index'))
    heures, minutes, secondes, work_time, rest_time,total_time,total_heures,total_minutes,total_secondes,timer = update_work()
    return jsonify({'heures': heures, 'minutes': minutes, 'secondes': secondes, 'work_time': work_time, 'rest_time': rest_time,'total_time':total_time,'total_heures':total_heures,'total_minutes':total_minutes,'total_secondes':total_secondes,'exercises': session["exercises_per_set"], 'sets': session["sets"],'timer':timer})

# Route pour mettre à jour le temps de repos
@app.route("/update_rest_time", methods=['GET', 'POST'])
def update_rest_route():
    if 'initial_work_time' not in session:
        return redirect(url_for('index'))
    heures, minutes, secondes, work_time, rest_time,total_time,total_heures,total_minutes,total_secondes = update_rest()
    return jsonify({'heures': heures, 'minutes': minutes, 'secondes': secondes, 'work_time': work_time, 'rest_time': rest_time,'total_time':total_time,'total_heures':total_heures,'total_minutes':total_minutes,'total_secondes':total_secondes, 'exercises': session["exercises_per_set"]})


if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')