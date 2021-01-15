from flask import Flask, render_template, request, redirect, url_for, flash
import numpy as np
import datetime

n_rom = ["I", "II", "III", "IV", "V", "VI"]
cloud = ["Despejado", "Medio nublado", "Nublado"]
today = datetime.date.today()
# <---------------------------------------------->
# Calcula el dia consecutivo
# <---------------------------------------------->


def consecutive_day(year, month, day):
    date = datetime.date(year, month, day)
    day_1 = datetime.date(year, 1, 1)
    conse_day = (date-day_1).days
    if conse_day > 364:
        conse_day = 364
    return conse_day, str(date)
# <---------------------------------------------->
# Verifica si se cumple la dosis o si no existe riesgo
# <---------------------------------------------->


def text_warming(time, text):
    if int(str(time)[0:2]) >= 21:
        time = text
    return time
# <---------------------------------------------->
# Funcion que lee la hora y el tiempo de la dosis y la da con el formato hh:mm
# <---------------------------------------------->


def format_result(time, hour):
    n = int(time/60)
    time += -n*60
    time = datetime.time(hour+n, time)
    return time
# <---------------------------------------------->
# Busca la informacion de las dosis en los archivos y los prepara con el formato
# <---------------------------------------------->


def searchdata(minute, hour, day, month, year, skin, n_cloud, treatment):
    date_num, date = consecutive_day(year, month, day)
    hour_num = (hour-8)*60+minute
    date = date[8:10]+"/"+date[5:7]+"/"+date[0:4]
    """
    <---------------------------------------------->
    Se suma 2 a la dosis para tener un rango efectivo
    Se suman los minutos para obtener los minutos medidos desde la hora de inicio
    <---------------------------------------------->
    """
    time_dosis = int(np.loadtxt("Data/dosis-"+treatment+"-"+str(n_cloud) +
                                ".txt", skiprows=hour_num, max_rows=1, usecols=date_num)+2+minute)
    time_max = int(np.loadtxt("Data/Max-"+n_rom[skin]+"-"+str(
        n_cloud)+".txt", skiprows=hour_num, max_rows=1, usecols=date_num)+2+minute)
    # <---------------------------------------------->
    # Da formato a el tiempo maximo y de dosis
    time_max = format_result(time_max, hour)
    time_dosis = format_result(time_dosis, hour)
    # <---------------------------------------------->
    hour = datetime.time(hour, minute)
    # <---------------------------------------------->
    #
    time_dosis = text_warming(time_dosis, "No se completará la dosis")
    time_max = text_warming(time_max, "Sin riesgo")
    # <---------------------------------------------->
    return time_dosis, time_max, date, hour


app = Flask(__name__,static_folder='static', static_url_path='/static')

app.secret_key = "mykey"
# <---------------------------------------------->
# Realiza el render del home

#Cambio para fondo de año nuevo
# @app.route('/')
# def home():
#     return render_template("newyear.html")

# @app.route('/home')
# def calc():
#     return render_template("home.html", today=today)

@app.route('/')
def calc():
    return render_template("home.html", today=today)
# <---------------------------------------------->
# <---------------------------------------------->
# Realiza el render de la informacion de los contactos


@app.route('/contact', strict_slashes=False)
def error():
    return render_template("contact.html")
# <---------------------------------------------->
# Renderiza la informacion de la plataforma


@app.route("/information", strict_slashes=False)
def info():
    return render_template("information.html")
# <---------------------------------------------->
# Renderiza la apertura de la seccion de condiciones de cielo


@app.route('/cloud', methods=["POST"])
def values():
    if request.method == "POST":
        treatment = request.form["treatment"]
        date = request.form["date"]
        hour = request.form["hour"]
        skin = int(request.form["skin"])
        info = (date, hour, skin, treatment)
    return render_template("cloud.html", info=info)
# <---------------------------------------------->
# Renderiza la pagina de recomendaciones


@app.route("/recommend", methods=["POST"])
def cont():
    if request.method == "POST":
        treatment = request.form["treatment"]
        date = request.form["date"]
        hour = request.form["hour"]
        n_cloud = int(request.form["cloud"])
        skin = int(request.form["skin"])
        year = int((date)[0:4])
        month = int((date)[5:7])
        day = int((date)[8:10])
        hour, minute = int(hour[0:2]), int(hour[3:5])
        time_d, time_max, hour, date = searchdata(
            minute, hour, day, month, year, skin, n_cloud, treatment)
        info = (time_d, time_max, hour, date, n_rom[skin], cloud[n_cloud])
    return render_template("results.html", info=info)


# <---------------------------------------------->
if __name__ == '__main__':
    app.run(debug=True)
