
from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import current_user
from flowapp.models import UserDevice, DeviceConsumption, Recomendacion, Categoria
from datetime import datetime, timedelta
from flowapp import db
from sqlalchemy import text, and_, func, cast, Date
from flowapp.usuarios.utilitarios import graficar_resumen_dispositivos

principal = Blueprint('principal', __name__)


@principal.route("/")
@principal.route("/home")
def home():
    page = None
    devices = None
    diagrama_barra = None
    lista_recomendacion = db.session.query(Recomendacion.msg_tip).all()
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        if (current_user.username == "admin"):
            devices = UserDevice.query.order_by(
                UserDevice.linkDate.desc()).paginate(page=page, per_page=5)
            print('Se ha autenticado el Administrador', current_user.username)
            return render_template('home.html', devices=devices, datetime=datetime, compare=compare, lista_recomendacion=lista_recomendacion)
        devices = UserDevice.query.filter_by(idUserFK=current_user.id).order_by(
            UserDevice.linkDate.desc()).paginate(page=page, per_page=5)
        lista_consumos_consolidado = db.session.query(DeviceConsumption.idUserDevice, UserDevice.zona, Categoria.title,  func.sum(DeviceConsumption.quantity)).join(
            UserDevice).join(Categoria).filter(UserDevice.idUserFK == current_user.id).group_by(DeviceConsumption.idUserDevice).all()
        diagrama_barra = graficar_resumen_dispositivos(
            lista_consumos_consolidado)
        return render_template('home.html', devices=devices, datetime=datetime, compare=compare, lista_recomendacion=lista_recomendacion, diagrama_barra=diagrama_barra)

    return render_template('about.html', title='Acerca de')


@principal.route("/about")
def about():
    return render_template('about.html', title='Recomendaciones de Ahorro')


def compare(date_ultimo_consumo):
    if (datetime.now() < date_ultimo_consumo + timedelta(minutes=5)):
        return True
    return False
