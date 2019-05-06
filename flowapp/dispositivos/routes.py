from flowapp.dispositivos.forms import (PostForm, DateForm)
from flowapp.models import Device, UserDevice, Categoria, DeviceConsumption, DeviceConfiguration
from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from flowapp import db
from sqlalchemy import text, and_, func, cast, Date
from datetime import datetime, timedelta
from flowapp.dispositivos.utilitarioGraficas import graficar_bar_diagrama, graficar_torta_diagrama, graficar_date_diagrama, graficar_consumo_dia


dispositivos = Blueprint('dispositivos', __name__)


@dispositivos.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        # Commit al Device - Se esta creando un nuevo
        device = Device(serialID=form.title.data)
        db.session.add(device)
        db.session.commit()
        # Obtencion Categoria Seleccionada
        id_categoria = form.category.data
        categoria = Categoria.query.filter_by(id=id_categoria).first()
        # Obtencion Zona
        zona = form.content.data
        device_user = UserDevice(dispUser=device, dispositivo=current_user,
                                 active='S', dispCategoria=categoria, zona=zona)
        db.session.add(device_user)
        db.session.commit()
        # Insercion de la informacion de la configuracion del Dispositivo
        user_device_limit = DeviceConfiguration(limitDefined=form.limiteConsumo.data, startDateConfig=form.dateInicioConsumo.data,
                                                endDateConfig=form.dateInicioConsumo.data + timedelta(days=form.periocidad.data), userDeviceConfigParent=device_user)
        db.session.add(user_device_limit)
        db.session.commit()
        flash('Su dispositivo se ha registrado!', 'success')
        return redirect(url_for('principal.home'))
    return render_template('create_post.html', title='Nuevo Dispositivo',
                           form=form, legend='Nuevo Dispositivo')


@dispositivos.route("/post/<int:post_id>", methods=['POST', 'GET'])
def post(post_id):
    form = DateForm()
    # Se obtiene el device que ha seleccionado el usuario
    device = UserDevice.query.get_or_404(post_id)
    # Ejemplificacion de Variables
    list_consumos = None
    diagrama_barra = None
    diagrama_torta = None
    diagrama_fechas = None
    diagrama_consumo_dia = None

    # Obtener total consumo del dispositivo
    total_consumo = db.session.query(func.sum(DeviceConsumption.quantity)).filter(
        DeviceConsumption.idUserDevice == device.id)
    # Obtener limite del consumo del dispositivo
    limite_definido = db.session.query(DeviceConfiguration.limitDefined).filter(
        DeviceConfiguration.idUserDevice == device.id)
    # Obtener consumos agrupados por fecha
    lista_consumo_dia = db.session.query(DeviceConsumption.date, db.func.count(DeviceConsumption.idUserDevice)).filter(
        DeviceConsumption.idUserDevice == device.id).group_by((cast(DeviceConsumption.date, Date))).all()
    # Obtener lista de dias para dispositivo
    list_consumo_dia_fechas = db.session.query(DeviceConsumption.date).filter(
        DeviceConsumption.idUserDevice == device.id).group_by((cast(DeviceConsumption.date, Date)))

    if request.method == 'GET':

        # Obtener Lista de Consumos
        list_consumos = DeviceConsumption.query.filter_by(
            idUserDevice=device.id)
        if (list_consumos.all()):
            diagrama_barra = graficar_bar_diagrama(
                total_consumo.scalar(), limite_definido.scalar())
            diagrama_torta = graficar_torta_diagrama(
                total_consumo.scalar(), limite_definido.scalar())
            diagrama_fechas = graficar_date_diagrama(list_consumos)
            diagrama_consumo_dia = graficar_consumo_dia(
                lista_consumo_dia)
            if total_consumo.scalar() > limite_definido.scalar():
                flash('Usted ha excedido el consumo límite en: ' +
                      str(total_consumo.scalar()-limite_definido.scalar())+' C.C !!!', 'warning')

    elif form.validate_on_submit():
        list_consumos = db.session.query(DeviceConsumption).filter(and_((func.date(
            DeviceConsumption.date) >= form.dateInicio.data), func.date(DeviceConsumption.date) <= form.dateFin.data))
        diagrama_fechas = graficar_date_diagrama(list_consumos)
        return render_template('post.html', device=device, listConsumos=list_consumos, form=form, diagrama_fechas=diagrama_fechas)

    else:
        flash('La fecha inicial no puede ser mayor que la final', 'warning')
        list_consumos = DeviceConsumption.query.filter_by(
            idUserDevice=device.id)
        return render_template('post.html', device=device, listConsumos=list_consumos, form=form)

    return render_template('post.html', device=device, listConsumos=list_consumos, form=form, diagrama_barra=diagrama_barra, diagrama_torta=diagrama_torta, diagrama_fechas=diagrama_fechas, diagrama_consumo_dia=diagrama_consumo_dia)


@dispositivos.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    # Se busca El dispositivo_User
    device = UserDevice.query.get_or_404(post_id)
    # Se busca la configuracion del Dispositivo
    device_config = DeviceConfiguration.query.filter_by(
        userDeviceConfigParent=device).first()
    if device.dispositivo != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        device.zona = form.content.data  # Se actualiza la zona
        device.dispUser.serialID = form.title.data  # Se actualiza el SerialID
        device.idDeviceCategoryFK = form.category.data  # Se actualiza la categoria
        device_config.limitDefined = form.limiteConsumo.data
        device_config.startDateConfig = form.dateInicioConsumo.data
        device_config.endDateConfig = form.dateInicioConsumo.data + \
            timedelta(days=form.periocidad.data)
        db.session.commit()
        flash('Se ha actualizado la información de tu dispositivo!', 'success')
        return redirect(url_for('dispositivos.post', post_id=device.id))

    elif request.method == 'GET':
        form.title.data = device.dispUser.serialID
        form.content.data = device.zona
        form.category.data = device.idDeviceCategoryFK
        form.limiteConsumo.data = device_config.limitDefined
    return render_template('create_post.html', title='Actualizar Dispositivo',
                           form=form, legend='Actualizar Dispositivo')


@dispositivos.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    user_device = UserDevice.query.get_or_404(post_id)
    # Se busca la configuracion del Dispositivo asociado
    device_config = DeviceConfiguration.query.filter_by(
        userDeviceConfigParent=user_device).first()
    if user_device.dispositivo != current_user:
        abort(403)
    db.session.delete(device_config)
    db.session.delete(user_device)
    db.session.delete(user_device.dispUser)
    db.session.commit()
    flash('Se ha eliminado el dispositivo de tu cuenta!', 'success')
    return redirect(url_for('principal.home'))
