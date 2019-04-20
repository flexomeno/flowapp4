from flowapp.dispositivos.forms import (PostForm, DateForm)
from flowapp.models import  Device, UserDevice, Categoria, DeviceConsumption
from flask import render_template, url_for, flash, redirect, request, abort,Blueprint
from flask_login import current_user,login_required
from flowapp import db
from sqlalchemy import text, and_, func

dispositivos = Blueprint('dispositivos', __name__)


@dispositivos.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        # Commit al Device - Se esta creando un nuevo
        print('IdCatergoria', form.category.data)
        device = Device(serialID=form.title.data)
        db.session.add(device)
        db.session.commit()
        # Obtencion Categoria Seleccionada
        idCategoria = form.category.data
        categoria = Categoria.query.filter_by(id=idCategoria).first()
        # Obtencion Zona
        zona = form.content.data
        deviceUser = UserDevice(dispUser=device, dispositivo=current_user,
                                active='S', dispCategoria=categoria, zona=zona)
        db.session.add(deviceUser)
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
    listConsumos = None

    if request.method == 'GET':
        listConsumos = DeviceConsumption.query.filter_by(
            idUserDevice=device.id)

    elif form.validate_on_submit():
        listConsumos = db.session.query(DeviceConsumption).filter(and_((func.date(
            DeviceConsumption.date) >= form.dateInicio.data), func.date(DeviceConsumption.date) <= form.dateFin.data))
    else:
        flash('La fecha inicial no puede ser mayor que la final', 'warning')
        listConsumos = DeviceConsumption.query.filter_by(
            idUserDevice=device.id)

    return render_template('post.html', device=device, listConsumos=listConsumos, form=form)


@dispositivos.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    device = UserDevice.query.get_or_404(post_id)
    if device.dispositivo != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        device.zona = form.content.data  # Se actualiza la zona
        device.dispUser.serialID = form.title.data  # Se actualiza el SerialID
        device.idDeviceCategoryFK = form.category.data  # Se actualiza la categoria
        db.session.commit()
        flash('Se ha actualizado la información de tu dispositivo!', 'success')
        return redirect(url_for('dispositivos.post', post_id=device.id))
    
    elif request.method == 'GET':
        form.title.data = device.dispUser.serialID
        form.content.data = device.zona
    return render_template('create_post.html', title='Actualizar Dispositivo',
                           form=form, legend='Actualizar Dispositivo')


@dispositivos.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    userDevice = UserDevice.query.get_or_404(post_id)

    if userDevice.dispositivo != current_user:
        abort(403)
    db.session.delete(userDevice)
    db.session.delete(userDevice.dispUser)
    db.session.commit()
    flash('Se ha eliminado el dispositivo de tu cuenta!', 'success')
    return redirect(url_for('principal.home'))