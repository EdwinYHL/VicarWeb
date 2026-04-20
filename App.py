from flask import Flask, render_template, redirect, url_for, flash, request, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from Models import db, User, Vehicle, Driver, Rental, Maintenance
from Forms import LoginForm, VehicleForm, DriverForm, RentalForm, MaintenanceForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-super-segura-cambiar-en-produccion'
# Configuración de PostgreSQL local (ajusta usuario, contraseña, host, puerto)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:contraseña@localhost/vicar_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicie sesión para acceder.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------- Rutas de autenticación ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f'Bienvenido {user.username}', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('Login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    total_vehicles = Vehicle.query.count()
    total_drivers = Driver.query.count()
    active_rentals = Rental.query.filter(Rental.end_date.is_(None)).count()
    pending_maintenance = Maintenance.query.filter(Maintenance.next_maintenance_date >= datetime.today()).count()
    return render_template('dashboard.html',
                           total_vehicles=total_vehicles,
                           total_drivers=total_drivers,
                           active_rentals=active_rentals,
                           pending_maintenance=pending_maintenance)

# ---------- Módulo Vehículos ----------
@app.route('/vehicles')
@login_required
def vehicles_list():
    vehicles = Vehicle.query.all()
    return render_template('vehicles/list.html', vehicles=vehicles)

@app.route('/vehicles/add', methods=['GET', 'POST'])
@login_required
def vehicle_add():
    form = VehicleForm()
    if form.validate_on_submit():
        vehicle = Vehicle(
            brand=form.brand.data,
            model=form.model.data,
            year=form.year.data,
            plate=form.plate.data,
            serial=form.serial.data,
            status=form.status.data
        )
        db.session.add(vehicle)
        db.session.commit()
        flash('Vehículo registrado exitosamente', 'success')
        return redirect(url_for('vehicles_list'))
    return render_template('vehicles/add.html', form=form)

@app.route('/vehicles/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def vehicle_edit(id):
    vehicle = Vehicle.query.get_or_404(id)
    form = VehicleForm(obj=vehicle)
    if form.validate_on_submit():
        vehicle.brand = form.brand.data
        vehicle.model = form.model.data
        vehicle.year = form.year.data
        vehicle.plate = form.plate.data
        vehicle.serial = form.serial.data
        vehicle.status = form.status.data
        db.session.commit()
        flash('Vehículo actualizado', 'success')
        return redirect(url_for('vehicles_list'))
    return render_template('vehicles/edit.html', form=form, vehicle=vehicle)

@app.route('/vehicles/delete/<int:id>')
@login_required
def vehicle_delete(id):
    vehicle = Vehicle.query.get_or_404(id)
    # Verificar que no tenga rentas activas
    if Rental.query.filter_by(vehicle_id=id, end_date=None).first():
        flash('No se puede eliminar un vehículo con renta activa', 'danger')
    else:
        db.session.delete(vehicle)
        db.session.commit()
        flash('Vehículo eliminado', 'info')
    return redirect(url_for('vehicles_list'))

# ---------- Módulo Conductores (Drivers) ----------
@app.route('/drivers')
@login_required
def drivers_list():
    drivers = Driver.query.all()
    return render_template('drivers/list.html', drivers=drivers)

@app.route('/drivers/add', methods=['GET', 'POST'])
@login_required
def driver_add():
    form = DriverForm()
    if form.validate_on_submit():
        driver = Driver(
            name=form.name.data,
            license_number=form.license_number.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data
        )
        db.session.add(driver)
        db.session.commit()
        flash('Conductor registrado', 'success')
        return redirect(url_for('drivers_list'))
    return render_template('drivers/add.html', form=form)

@app.route('/drivers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def driver_edit(id):
    driver = Driver.query.get_or_404(id)
    form = DriverForm(obj=driver)
    if form.validate_on_submit():
        driver.name = form.name.data
        driver.license_number = form.license_number.data
        driver.phone = form.phone.data
        driver.email = form.email.data
        driver.address = form.address.data
        db.session.commit()
        flash('Conductor actualizado', 'success')
        return redirect(url_for('drivers_list'))
    return render_template('drivers/edit.html', form=form, driver=driver)

@app.route('/drivers/delete/<int:id>')
@login_required
def driver_delete(id):
    driver = Driver.query.get_or_404(id)
    if Rental.query.filter_by(driver_id=id, end_date=None).first():
        flash('No se puede eliminar un conductor con renta activa', 'danger')
    else:
        db.session.delete(driver)
        db.session.commit()
        flash('Conductor eliminado', 'info')
    return redirect(url_for('drivers_list'))

# ---------- Módulo Rentas ----------
@app.route('/rentals')
@login_required
def rentals_list():
    rentals = Rental.query.order_by(Rental.start_date.desc()).all()
    return render_template('rentals/list.html', rentals=rentals)

@app.route('/rentals/add', methods=['GET', 'POST'])
@login_required
def rental_add():
    form = RentalForm()
    # Llenar los choices de vehículos y conductores disponibles
    form.vehicle_id.choices = [(v.id, f"{v.brand} {v.model} - {v.plate}") for v in Vehicle.query.filter_by(status='Disponible').all()]
    form.driver_id.choices = [(d.id, d.name) for d in Driver.query.all()]
    if form.validate_on_submit():
        rental = Rental(
            vehicle_id=form.vehicle_id.data,
            driver_id=form.driver_id.data,
            start_date=form.start_date.data,
            end_date=None,  # Aún no ha finalizado
            origin=form.origin.data,
            destination=form.destination.data,
            amount=form.amount.data
        )
        # Cambiar estado del vehículo a 'Rentado'
        vehicle = Vehicle.query.get(form.vehicle_id.data)
        vehicle.status = 'Rentado'
        db.session.add(rental)
        db.session.commit()
        flash('Renta registrada exitosamente', 'success')
        return redirect(url_for('rentals_list'))
    return render_template('rentals/add.html', form=form)

@app.route('/rentals/end/<int:id>')
@login_required
def rental_end(id):
    rental = Rental.query.get_or_404(id)
    if rental.end_date is None:
        rental.end_date = datetime.now()
        # Liberar vehículo
        vehicle = Vehicle.query.get(rental.vehicle_id)
        vehicle.status = 'Disponible'
        db.session.commit()
        flash('Renta finalizada', 'success')
    else:
        flash('Esta renta ya estaba finalizada', 'warning')
    return redirect(url_for('rentals_list'))

# ---------- Módulo Mantenimiento ----------
@app.route('/maintenance')
@login_required
def maintenance_list():
    maintenances = Maintenance.query.order_by(Maintenance.date.desc()).all()
    return render_template('maintenance/list.html', maintenances=maintenances)

@app.route('/maintenance/add', methods=['GET', 'POST'])
@login_required
def maintenance_add():
    form = MaintenanceForm()
    form.vehicle_id.choices = [(v.id, f"{v.brand} {v.model} - {v.plate}") for v in Vehicle.query.all()]
    if form.validate_on_submit():
        maintenance = Maintenance(
            vehicle_id=form.vehicle_id.data,
            date=form.date.data,
            type=form.type.data,
            workshop=form.workshop.data,
            description=form.description.data,
            cost=form.cost.data,
            next_maintenance_date=form.next_maintenance_date.data
        )
        db.session.add(maintenance)
        db.session.commit()
        flash('Mantenimiento registrado', 'success')
        return redirect(url_for('maintenance_list'))
    return render_template('maintenance/add.html', form=form)

# ---------- Módulo Reportes ----------
@app.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    format = request.args.get('format', 'html')  # html, excel, pdf
    rentals = []
    maintenances = []
    total_income = 0
    total_expenses = 0
    if start_date and end_date:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        rentals = Rental.query.filter(Rental.start_date >= start, Rental.start_date <= end).all()
        maintenances = Maintenance.query.filter(Maintenance.date >= start, Maintenance.date <= end).all()
        total_income = sum(r.amount for r in rentals)
        total_expenses = sum(m.cost for m in maintenances)
        if format == 'excel':
            # Exportar a Excel
            data_rentals = [{'Fecha': r.start_date, 'Vehículo': r.vehicle.brand + ' ' + r.vehicle.model,
                             'Conductor': r.driver.name, 'Origen': r.origin, 'Destino': r.destination,
                             'Monto': r.amount} for r in rentals]
            data_maintenance = [{'Fecha': m.date, 'Vehículo': m.vehicle.brand + ' ' + m.vehicle.model,
                                 'Tipo': m.type, 'Taller': m.workshop, 'Costo': m.cost} for m in maintenances]
            df1 = pd.DataFrame(data_rentals)
            df2 = pd.DataFrame(data_maintenance)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df1.to_excel(writer, sheet_name='Rentas', index=False)
                df2.to_excel(writer, sheet_name='Mantenimientos', index=False)
            output.seek(0)
            return send_file(output, download_name=f'reporte_{start_date}_{end_date}.xlsx', as_attachment=True)
        elif format == 'pdf':
            # Exportar a PDF simplificado
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.drawString(100, 750, f"Reporte VICAR del {start_date} al {end_date}")
            c.drawString(100, 730, f"Total Ingresos (Rentas): ${total_income}")
            c.drawString(100, 710, f"Total Egresos (Mantenimientos): ${total_expenses}")
            c.drawString(100, 690, f"Balance: ${total_income - total_expenses}")
            c.save()
            buffer.seek(0)
            return send_file(buffer, download_name=f'reporte_{start_date}_{end_date}.pdf', as_attachment=True)
    return render_template('reports/index.html', rentals=rentals, maintenances=maintenances,
                           total_income=total_income, total_expenses=total_expenses,
                           start_date=start_date, end_date=end_date)

# ---------- Crear tablas y usuario admin por defecto ----------
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password=generate_password_hash('admin123'), role='admin')
        db.session.add(admin)
        db.session.commit()
        print("Usuario admin creado: admin / admin123")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
