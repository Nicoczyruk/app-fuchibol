import pyodbc
from flask import Flask, current_app

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    app.secret_key = "clave-secreta-local-unica"


    # Registrar Blueprints
    with app.app_context():
        from .routes import main
        app.register_blueprint(main)

    return app

def get_db_connection():
    connection_string = current_app.config['DATABASE_CONNECTION']
    return pyodbc.connect(connection_string)