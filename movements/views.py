from movements import app, acciones
from movements.forms import Clasesforms
from flask import render_template, request, url_for, redirect 
import sqlite3
from config import *
import requests

url_crypto = "https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={}&symbol={}&convert={}&CMC_PRO_API_KEY={}"

def busquedaconversion(url):
    respuesta = requests.get(url)
    if respuesta.status_code==200:
        datos=respuesta.json()
        return datos


DBFILE = app.config['DBFILE'] 

@app.route('/')
def listadoMovimientos():
    form = Clasesforms()
    mensajes = []
    try:
        ingresos = acciones.consulta('SELECT fecha, hora, monedafrom, cantidadfrom, monedato, cantidadto, conversion FROM movimientos;')
    except Exception as e:
        print("**ERROR**:Acceso a base de datos-DBFILE:{} {}". format(type(e).__name__,e))
        mensajes.append("Error en acceso a base de datos. Consulte con el administrador.")

        return render_template("movimientos.html", form=form, mensajes=mensajes)

    return render_template("movimientos.html", datos=ingresos, form=form) 
    

@app.route('/nuevacompra', methods=['GET', 'POST'])
def transaccion():
    mensajes = []
    interruptor=False
    form = Clasesforms()
    fecha=acciones.fecha()
    hora=acciones.hora()
    try:
        dicResultado=acciones.totales()
    except Exception as e:
        print("**ERROR**:Acceso a base de datos-DBFILE:{} {}". format(type(e).__name__,e))
        mensajes.append("Error en acceso a base de datos. Consulte con el administrador.")
        return render_template("alta.html", form=form, mensajes=mensajes,interruptor=False)
    listamonedasdisponibles=[]
    
    for crypto,valor in dicResultado.items():
        if valor> 0:
            listamonedasdisponibles.append(crypto)
    if not 'EUR' in listamonedasdisponibles:
        listamonedasdisponibles.append('EUR')
    
    form.monedafrom.choices=listamonedasdisponibles
    
    if request.method == 'POST': 
        if form.validate():
            if form.calcular.data ==True: #pulsa el boton calculadora
                try:
                    resultado= busquedaconversion(url_crypto.format(form.cantidadfrom.data,form.monedafrom.data,form.monedato.data,API_KEY))
                    monedafrom=resultado["data"]["symbol"]
                    cantidadfrom=resultado["data"]["amount"]
                    monedato=(form.monedato.data)
                    cantidadto=resultado["data"]["quote"][monedato]["price"]
                    conversion=float(cantidadfrom)/float(cantidadto)
                    form.cantidadto.data = cantidadto
                    form.conversion.data = conversion                   
                except Exception as e:
                    print("**ERROR**:Acceso a consulta con la API:{} {}". format(type(e).__name__,e))
                    mensajes.append("Error en la consulta a la API. Consulte con el administrador.")
                    return render_template("alta.html", form=form, mensajes=mensajes,interruptor=False)
                
                return render_template("alta.html", form=form,interruptor=True)

            if form.submit.data:
                try:
                    acciones.consulta ('INSERT INTO movimientos (fecha, hora, monedafrom, monedato, cantidadfrom, cantidadto, conversion) VALUES (?,?, ?, ?, ?,?,?);',
                            (
                                fecha,
                                hora,
                                form.monedafrom.data,
                                form.monedato.data,
                                float(form.cantidadfrom.data),
                                round(float(form.cantidadto.data),8),
                                round(float(form.conversion.data),8)
                            )
                                    )
                except Exception as e:
                    print("**ERROR**:Acceso a base de datos-DBFILE:{} {}". format(type(e).__name__,e))
                    mensajes.append("Error en acceso a base de datos. Consulte con el administrador.")
                    return render_template("alta.html", form=form, mensajes=mensajes,interruptor=False)

                return redirect(url_for('listadoMovimientos'))
            else:
                return render_template("alta.html", form=form) 
    return render_template("alta.html" , form=form, interruptor=False )


@app.route('/status', methods=['GET', 'POST'])
def resumen():
    mensajes = []
    form = Clasesforms()
    try:
        euros1=acciones.consulta('SELECT SUM(cantidadfrom) AS total, monedafrom FROM movimientos WHERE monedafrom = "EUR" GROUP BY monedafrom;')
        euros1=euros1[0]['total']
        form.totalinvertido.data =euros1
        euros2=acciones.totales()["EUR"]
        valoractual=0
        dicResultado=acciones.totales()
    except Exception as e:
        print("**ERROR**:Puede que no se haya ejecutado ninguna operación.Acceso a base de datos-DBFILE:{} {}". format(type(e).__name__,e))
        mensajes.append("Consulte con el administrador, en caso de haber ejecutado alguna operación, en caso contrario vaya a la pantalla para empezar a invertir.")
        return render_template("resumen.html", form=form, mensajes=mensajes,interruptor=False)

    for crypto,valor in dicResultado.items():
            if crypto != 'EUR':
                try:
                    resultado= busquedaconversion(url_crypto.format(valor,crypto,"EUR",API_KEY))
                    eurosasumar=resultado["data"]["quote"]["EUR"]["price"]
                    valoractual+=float(eurosasumar)
                except Exception as e:
                    print("**ERROR**:Acceso a consulta con la API:{} {}". format(type(e).__name__,e))
                    mensajes.append("Error en la consulta a la API. Consulte con el administrador.")
                    return render_template("resumen.html", form=form, mensajes=mensajes,interruptor=False)
            
    totalesdefinitivos=round(valoractual+euros2+euros1,2)
    ganancias=round(totalesdefinitivos-euros1,2)

    form.valoractual.data = totalesdefinitivos
    form.neteo.data= ganancias
    return render_template("resumen.html", form=form)