import os
import secrets
from PIL import Image
from flask import url_for
from flask_mail import Message
from flowapp import app, mail
import pygal
from pygal.style import Style

custom_style = Style(
  label_font_size=35,
  value_font_size = 35,
  value_label_font_size = 69,
  legend_font_size = 35,
  tooltip_font_size = 35,
  title_font_size = 30,
  font_family = 'googlefont:Josefin Sans',
  colors=('#7D3C98', '#17A589', '#2E86C1', '#E74C3C', '#E89B53')
  )

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Solicitud de cambio de clave FLOWAPP',
                  sender='noreply@demo.com',
                  recipients=[user.profile.email])
    msg.body = f'''Haga Click en el siguiente link para resetar tu password:
{url_for('usuarios.reset_token', token=token, _external=True)}

Si no realizó esta solicitud, simplemente ignore este correo electrónico y no se realizarán cambios.
'''
    mail.send(msg)

def graficar_resumen_dispositivos(lista_consumos_consolidado):
    lista_categorias_labels = []
    lista_consumos=[]

    for dispositivo in lista_consumos_consolidado:
        lista_categorias_labels.append(dispositivo[2]+"-"+dispositivo[1])
        lista_consumos.append(dispositivo[1])
    
    diagrama_barra_vertical = pygal.Bar(style=custom_style,legend_at_bottom=True,height=950)
    diagrama_barra_vertical.title = 'Consumo Global'
    #diagrama_barra_vertical.x_labels = lista_categorias_labels

    for informacion in lista_consumos_consolidado:
        diagrama_barra_vertical.add(informacion[2]+"-"+informacion[1],informacion[3])
    diagrama_barra_vertical.render()
    diagrama_renderizado = diagrama_barra_vertical.render_data_uri()

    return (diagrama_renderizado)

