#!/usr/bin/env python3
"""
Script para atualizar o banco de dados com a nova tabela de produtos especiais.
"""

from app import create_app, db
from app.models import ProdutoEspecial

app = create_app()

with app.app_context():
    print("🔄 Atualizando banco de dados...")
    
    # Criar a nova tabela de produtos especiais
    try:
        db.create_all()
        print("✅ Tabela de produtos especiais criada com sucesso!")
        
        # Verificar se a tabela foi criada
        produtos_count = ProdutoEspecial.query.count()
        print(f"📊 Produtos especiais cadastrados: {produtos_count}")
        
        print("\n🚀 Sistema atualizado com sucesso!")
        print("📋 Próximos passos:")
        print("1. Acesse a nova tela de Produtos Especiais")
        print("2. Cadastre produtos com comissões especiais")
        print("3. Os relatórios agora mostrarão apenas 2 categorias:")
        print("   - PRODUTOS COM COMISSÃO MODIFICADA")
        print("   - OUTROS PRODUTOS")
        
    except Exception as e:
        print(f"❌ Erro ao atualizar banco de dados: {e}")
        db.session.rollback()
