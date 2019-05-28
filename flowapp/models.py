from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flowapp import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):

    __tablename__ = 'user'

    id = db.Column('IdUser', db.Integer, primary_key=True)
    username = db.Column('UserName', db.String(30))
    dateCreation = db.Column('CreatedDate', db.DateTime, nullable=False,
                             default=datetime.utcnow)
    password = db.Column('password', db.String(100))
    active = db.Column('Active', db.String(100), default='S')
    rol = db.Column('IdRole', db.Integer, default='111')
    profile = db.relationship('UserProfile', backref='usuario', uselist=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    deviceUsuario = db.relationship('UserDevice', backref='dispositivo')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    # def __repr__(self):
        # return f"User('{self.username}')"
        # return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class UserProfile(db.Model):
    __tablename__ = "userprofile"

    id = db.Column('IdUser', db.Integer, db.ForeignKey(
        'user.IdUser'), primary_key=True)
    firstName = db.Column('FirstName', db.String(100))
    lastName = db.Column('LastName', db.String(100))
    email = db.Column('Email', db.String(100))
    phone = db.Column('Phone', db.Integer)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default2.jpg')

    def __repr__(self):
        return f"UserProfile('{self.firstName}','{self.lastName}','{self.email}')"


class Post(db.Model):

    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.IdUser'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Categoria(db.Model):

    __tablename__ = 'devicecategory'

    id = db.Column('IdDeviceCategory', db.Integer, primary_key=True)
    title = db.Column('Description', db.String(100), nullable=False)
    deviceCategoria = db.relationship('UserDevice', backref='dispCategoria')

    def __repr__(self):
        return "<Categoria(id='%s', name='%s')>" % (self.id, self.title)


class Device(db.Model):

    __tablename__ = 'device'
    id = db.Column('IdDevice', db.Integer, primary_key=True)
    serialID = db.Column('SerialID', db.String(25))
    deviceUsuario = db.relationship('UserDevice', backref='dispUser')


class UserDevice(db.Model):

    __tablename__ = 'userdevice'

    id = db.Column('IdUserDevice', db.Integer, primary_key=True)
    linkDate = db.Column('LinkDate', db.DateTime, nullable=False,
                         default=datetime.utcnow)
    idDeviceFK = db.Column('IdDevice', db.Integer, db.ForeignKey(
        'device.IdDevice'))  # Como se llama en la tabla
    idUserFK = db.Column('IdUser', db.Integer, db.ForeignKey(
        'user.IdUser'))
    active = db.Column('Active', db.String(1))
    idDeviceCategoryFK = db.Column('IdDeviceCategory', db.Integer, db.ForeignKey(
        'devicecategory.IdDeviceCategory'))
    zona = db.Column('Zone', db.String(100))
    consumosDispositivo = db.relationship(
        'DeviceConsumption', backref='userDevice', cascade="all, delete-orphan")
    configLimiteDispositivo = db.relationship(
        'DeviceConfiguration', backref='userDeviceConfigParent', uselist=False, cascade="all, delete-orphan")


class Unit(db.Model):
    __tablename__ = 'unit'
    id = db.Column('IdUnit', db.Integer, primary_key=True)
    name = db.Column('Name', db.String(45))
    deviceConsumptionChild = db.relationship(
        'DeviceConsumption', backref='unit')


class DeviceConsumption(db.Model):
    __tablename__ = 'deviceconsumption'

    id = db.Column('IdConsumption', db.Integer, primary_key=True)
    date = db.Column('Date', db.DateTime, nullable=False,
                     default=datetime.utcnow)
    quantity = db.Column('Quantity', db.Float)
    idUnitFk = db.Column('IdUnit', db.Integer, db.ForeignKey('unit.IdUnit'))
    idUserDevice = db.Column('IdUserDevice', db.Integer,
                             db.ForeignKey('userdevice.IdUserDevice'))


class DeviceConfiguration(db.Model):
    __tablename__ = 'deviceconfiguration'

    id = db.Column('IdDeviceConfiguration', db.Integer, primary_key=True)
    limitDefined = db.Column('LimitDefined', db.Float)
    startDateConfig = db.Column('StartDate', db.DateTime, nullable=False)
    endDateConfig = db.Column('EndDate', db.DateTime, nullable=False)
    isPeriodic = db.Column('IsPeriodic', db.Integer, default=1)
    idUserDevice = db.Column('IdUserDevice', db.Integer,
                             db.ForeignKey('userdevice.IdUserDevice'))
    estrato_id = db.Column('estrato',db.Integer, db.ForeignKey('estratocostocc.idcosto'))


class EstratoCosto(db.Model):
    __tablename__ = 'estratocostocc'
    id = db.Column('idcosto', db.Integer, primary_key=True)
    estrato = db.Column('estrato', db.String(100), nullable=False)
    costo = db.Column('costo', db.Float)
    dispositivo_estrato = db.relationship(
        'DeviceConfiguration', uselist=False, backref='estrato')

class Recomendacion(db.Model):
    __tablename__ = 'recommendation'
    id = db.Column('IdTip', db.Integer, primary_key=True)
    msg_tip = db.Column('Recommendation', db.String(500), nullable=False)
    idTipe = db.Column('IdType',db.Integer, db.ForeignKey('recommendationtype.IdType'))