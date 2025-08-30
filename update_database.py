#!/usr/bin/env python3
"""
Script para atualizar o banco de dados com a nova tabela ProdutoOracleCache
"""

from app import create_app, db
from app.models import ProdutoOracleCache

def update_database():
    """Atualiza o banco de dados criando a nova tabela"""
    app = create_app()
    
    with app.app_context():
        try:
            # Cria a nova tabela ProdutoOracleCache
            db.create_all()
            print("✅ Tabela ProdutoOracleCache criada com sucesso!")
            
            # Verifica se a tabela foi criada
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tabelas = inspector.get_table_names()
            
            if 'produto_oracle_cache' in tabelas:
                print("✅ Tabela 'produto_oracle_cache' encontrada no banco de dados")
            else:
                print("❌ Tabela 'produto_oracle_cache' não foi encontrada")
                
        except Exception as e:
            print(f"❌ Erro ao criar tabela: {str(e)}")

if __name__ == '__main__':
    update_database()
