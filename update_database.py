#!/usr/bin/env python3
"""
Script para atualizar o banco de dados com a nova tabela AjusteFaturamento
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuração do Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/business_rules.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o banco de dados
db = SQLAlchemy(app)

# Importa os modelos
from app.models import AjusteFaturamento

def update_database():
    """Atualiza o banco de dados criando a nova tabela"""
    try:
        with app.app_context():
            print("🔄 Atualizando banco de dados...")
            
            # Cria a nova tabela AjusteFaturamento
            db.create_all()
            
            print("✅ Tabela AjusteFaturamento criada com sucesso!")
            print("📊 Banco de dados atualizado.")
            
    except Exception as e:
        print(f"❌ Erro ao atualizar banco de dados: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = update_database()
    if success:
        print("\n🎉 Atualização concluída com sucesso!")
        print("💡 A nova funcionalidade de ajuste de faturamento está disponível.")
    else:
        print("\n💥 Falha na atualização do banco de dados.")
        sys.exit(1)
