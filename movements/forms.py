from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, Length,NumberRange,ValidationError
from movements import acciones

monedas=('EUR', 'ETH', 'LTC', 'BNB', 'EOS', 'XLM', 'TRX', 'BTC', 'XRP', 'BCH', 'USDT', 'BSV', 'ADA')

#objetos que se comunican con navegador

def compruebavalor(form,field):
    if form.monedafrom.data != 'EUR':
        available_cr = acciones.totales()
        currency = form.monedafrom.data
        if available_cr[currency] <=  field.data:
            raise ValidationError("No tiene saldo suficiente.")

def compruebamoneda(form,field):
    if form.monedafrom.data == form.monedato.data:
        raise ValidationError("No puede intercambiar la misma moneda")


class Clasesforms(FlaskForm):
    monedafrom = SelectField('Moneda de cambio',validators=[DataRequired(), compruebamoneda])
    monedato = SelectField('Moneda a cambiar', choices=monedas)
    cantidadfrom = FloatField('Cantidad', validators=[DataRequired(message="Introduzca una cantidad"),
    NumberRange (min=0.0000000001, max=10000000000, message="La cantidad que indica es muy elevada para operar"), compruebavalor])

    cantidadto=FloatField('Cantidad')
    conversion=DecimalField("P.U:")


    totalinvertido=FloatField("Euros totales invertidos:")
    valoractual=FloatField("Valor actual de todas sus inversiones:")
    neteo=FloatField("Resultado de su inversión:")

    calcular =SubmitField('Calcular')    
    submit = SubmitField('Aceptar')


