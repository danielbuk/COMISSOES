import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'uma-chave-secreta-bem-dificil')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///business_rules.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configurações do Oracle
    ORACLE_USER = os.environ.get('ORACLE_USER', 'dicon')
    ORACLE_PASSWORD = os.environ.get('ORACLE_PASSWORD', 'wdicon01')
    ORACLE_DSN = os.environ.get('ORACLE_DSN', '10.0.0.10:1521/WINT')
