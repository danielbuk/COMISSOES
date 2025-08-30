#!/usr/bin/env python3
"""
Script para atualizar o banco de dados com a nova tabela ProdutoOracleCache
"""

from app import create_app, db
from app.models import Vendedor, RegraComissao, ComissaoPadrao, ProdutoEspecial, DadosVendas, ProdutoOracleCache, AjusteFinanceiro

def update_database():
    """Atualiza o banco de dados criando todas as tabelas necessárias"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Atualizando banco de dados...")
        
        # Criar todas as tabelas
        db.create_all()
        
        print("✅ Banco de dados atualizado com sucesso!")
        print("📋 Tabelas criadas:")
        print("   - vendedor")
        print("   - regra_comissao")
        print("   - comissao_padrao")
        print("   - produto_especial")
        print("   - dados_vendas")
        print("   - produto_oracle_cache")
        print("   - ajuste_financeiro")

if __name__ == '__main__':
    update_database()
