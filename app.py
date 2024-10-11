import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, render_template, request, redirect, url_for, session
from models import Usuario, db
from config import Config
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_secret_key'  # Llave secreta para manejar sesiones
db.init_app(app)

def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/servicios')
def servicios():
    return render_template('servicios.html')

@app.route('/productos')
def productos():
    return render_template('productos.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Busca al usuario por nombre de usuario
        user = Usuario.query.filter_by(username=username).first()

        if user is None:
            error = 'Usuario no encontrado'
        elif user.password != password:  # Compara contraseñas en texto plano
            error = 'Contraseña incorrecta'
        else:
            session['username'] = username  # Guarda la sesión
            return redirect(url_for('plataforma'))  # Redirige al área privada

    return render_template('login.html', error=error)

@app.route('/plataforma')
def plataforma():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirigir al login si no está autenticado
    return render_template('plataforma.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)  # Eliminar la sesión
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        create_tables()  # Crear las tablas solo al iniciar la aplicación
    app.run(debug=True)