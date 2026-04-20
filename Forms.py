from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, FloatField, DateTimeField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Optional

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class VehicleForm(FlaskForm):
    brand = StringField('Marca', validators=[DataRequired(), Length(max=50)])
    model = StringField('Modelo', validators=[DataRequired(), Length(max=50)])
    year = IntegerField('Año', validators=[Optional()])
    plate = StringField('Placa', validators=[DataRequired(), Length(max=20)])
    serial = StringField('Número de Serie', validators=[Length(max=50)])
    status = SelectField('Estado', choices=[('Disponible','Disponible'),('Rentado','Rentado'),('Mantenimiento','Mantenimiento')])
    submit = SubmitField('Guardar')

class DriverForm(FlaskForm):
    name = StringField('Nombre completo', validators=[DataRequired(), Length(max=100)])
    license_number = StringField('Número de licencia', validators=[Length(max=50)])
    phone = StringField('Teléfono', validators=[Length(max=20)])
    email = StringField('Correo', validators=[Optional(), Email()])
    address = StringField('Dirección', validators=[Length(max=200)])
    submit = SubmitField('Guardar')

class RentalForm(FlaskForm):
    vehicle_id = SelectField('Vehículo', coerce=int, validators=[DataRequired()])
    driver_id = SelectField('Conductor', coerce=int, validators=[DataRequired()])
    start_date = DateTimeField('Fecha y hora de inicio', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    origin = StringField('Origen', validators=[Length(max=200)])
    destination = StringField('Destino', validators=[Length(max=200)])
    amount = FloatField('Monto de la renta', validators=[DataRequired()])
    submit = SubmitField('Registrar Renta')

class MaintenanceForm(FlaskForm):
    vehicle_id = SelectField('Vehículo', coerce=int, validators=[DataRequired()])
    date = DateTimeField('Fecha del mantenimiento', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    type = SelectField('Tipo', choices=[('Preventivo','Preventivo'),('Correctivo','Correctivo')])
    workshop = StringField('Taller', validators=[Length(max=100)])
    description = TextAreaField('Descripción')
    cost = FloatField('Costo', validators=[DataRequired()])
    next_maintenance_date = DateTimeField('Próximo mantenimiento', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Guardar Mantenimiento')
