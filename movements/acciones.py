from movements import app
import sqlite3
import time
import datetime

DBFILE = app.config['DBFILE'] 


def consulta(query, params=()):
    conn = sqlite3.connect(DBFILE)
    c = conn.cursor()

    c.execute(query, params)
    conn.commit()

    filas = c.fetchall()

    conn.close()

    if len(filas) == 0:
        return filas

    columnNames = []
    for columnName in c.description:
        columnNames.append(columnName[0])

    listaDeDiccionarios = []

    for fila in filas:
        d = {}
        for ix, columnName in enumerate(columnNames):
            d[columnName] = fila[ix]
        listaDeDiccionarios.append(d)

    return listaDeDiccionarios

def hora():
    hora=time.strftime("%X")
    return hora

def fecha():
    fecha=datetime.date.today()
    return fecha

def listaMonedas(lista):
    listamonedas=[]
    for clave,valor in lista.items():
        if valor > 0:
            listamonedas.append(clave)
    if not 'EUR' in listamonedas:
        listamonedas.append('EUR')
    return listamonedas


def totales():
    diccionario = consulta('SELECT  monedafrom, cantidadfrom, monedato, cantidadto FROM movimientos;')
    dicResultado = {}
    for a in diccionario:
        clavefrom = a.get("monedafrom")
        cantidadfrom = a.get("cantidadfrom")
        claveto = a.get("monedato")
        cantidadto = a.get("cantidadto")
        if dicResultado.get(claveto) == None:
            dicResultado[claveto]=cantidadto
        else:
            dicResultado[claveto]=cantidadto+dicResultado[claveto]
        if dicResultado.get(clavefrom) == None:
            dicResultado[clavefrom]=-cantidadfrom
        else:
            dicResultado[clavefrom]=dicResultado[clavefrom]-cantidadfrom
    return dicResultado
