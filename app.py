import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, render_template, request, redirect, url_for, session
from models import Usuario, Mensaje, db
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

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        mensaje = request.form['mensaje']

        # Crear una nueva instancia de Mensaje
        nuevo_mensaje = Mensaje(nombre=nombre, email=email, mensaje=mensaje)

        try:
            db.session.add(nuevo_mensaje)
            db.session.commit()
            return render_template('contacto.html', success="Mensaje enviado correctamente.")
        except Exception as e:
            db.session.rollback()
            print(f"Error al guardar el mensaje: {str(e)}")
            return render_template('contacto.html', error="Hubo un error al enviar el mensaje.")

    return render_template('contacto.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Usuario.query.filter_by(username=username).first()

        if user is None:
            error = 'Usuario no encontrado'
        elif not check_password_hash(user.password, password):  # Verifica la contraseña hasheada
            error = 'Contraseña incorrecta'
        else:
            session['username'] = username
            return redirect(url_for('plataforma'))

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Verificar si el usuario ya existe
        user_exists = Usuario.query.filter_by(username=username).first()
        if user_exists:
            return render_template('login.html', error="El usuario ya existe")
        
        # Crear nuevo usuario con contraseña hasheada
        new_user = Usuario(
            name=name,
            username=username,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            print(f"Error al registrar usuario: {str(e)}")  # Para debugging
            return render_template('login.html', error="Error al registrar usuario")
            
    return render_template('login.html')

if __name__ == '__main__':
    with app.app_context():
        create_tables()  # Crear las tablas solo al iniciar la aplicación
    app.run(debug=True)