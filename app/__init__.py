from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()
app = Flask(__name__) # Declaração de 'app'

def create_app(config_class=Config):
    app.config.from_object(config_class)
    db.init_app(app)

    with app.app_context():
        from . import routes
        # db.create_all() # Opcional: criar tabelas se não existirem ao iniciar
        return app
