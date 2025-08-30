#!/usr/bin/env python3
"""
Script de teste para verificar se a configuração do sistema está correta.
Execute este script antes de rodar a aplicação principal.
"""

import sys
import os

def test_imports():
    """Testa se todas as dependências estão instaladas."""
    print("Testando importações...")
    
    try:
        import flask
        print("✓ Flask importado com sucesso")
    except ImportError:
        print("✗ Erro: Flask não encontrado. Execute: pip install Flask")
        return False
    
    try:
        import flask_sqlalchemy
        print("✓ Flask-SQLAlchemy importado com sucesso")
    except ImportError:
        print("✗ Erro: Flask-SQLAlchemy não encontrado. Execute: pip install Flask-SQLAlchemy")
        return False
    
    try:
        import pandas
        print("✓ Pandas importado com sucesso")
    except ImportError:
        print("✗ Erro: Pandas não encontrado. Execute: pip install pandas")
        return False
    
    try:
        import oracledb
        print("✓ OracleDB importado com sucesso")
    except ImportError:
        print("✗ Erro: OracleDB não encontrado. Execute: pip install python-oracledb")
        return False
    
    try:
        import dotenv
        print("✓ Python-dotenv importado com sucesso")
    except ImportError:
        print("✗ Erro: Python-dotenv não encontrado. Execute: pip install python-dotenv")
        return False
    
    return True

def test_app_structure():
    """Testa se a estrutura da aplicação está correta."""
    print("\nTestando estrutura da aplicação...")
    
    required_files = [
        'app/__init__.py',
        'app/models.py',
        'app/services.py',
        'app/routes.py',
        'app/templates/base.html',
        'app/templates/relatorio.html',
        'app/static/styles.css',
        'config.py',
        'run.py',
        'seed_database.py'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} encontrado")
        else:
            print(f"✗ {file_path} não encontrado")
            return False
    
    return True

def test_app_creation():
    """Testa se a aplicação Flask pode ser criada."""
    print("\nTestando criação da aplicação...")
    
    try:
        from app import create_app
        app = create_app()
        print("✓ Aplicação Flask criada com sucesso")
        return True
    except Exception as e:
        print(f"✗ Erro ao criar aplicação: {e}")
        return False

def test_database_models():
    """Testa se os modelos do banco de dados estão corretos."""
    print("\nTestando modelos do banco de dados...")
    
    try:
        from app import create_app, db
        from app.models import Vendedor, RegraComissao, TipoVendedor
        
        app = create_app()
        with app.app_context():
            # Testa se as tabelas podem ser criadas
            db.create_all()
            print("✓ Modelos do banco de dados criados com sucesso")
            
            # Testa se um vendedor pode ser criado
            vendedor = Vendedor(
                rca=999,
                nome="Vendedor Teste",
                tipo=TipoVendedor.NORMAL,
                ignorar_no_relatorio=False
            )
            db.session.add(vendedor)
            db.session.commit()
            print("✓ Vendedor criado com sucesso")
            
            # Limpa o teste
            db.session.delete(vendedor)
            db.session.commit()
            
        return True
    except Exception as e:
        print(f"✗ Erro nos modelos do banco de dados: {e}")
        return False

def main():
    """Função principal do teste."""
    print("=== TESTE DE CONFIGURAÇÃO DO SISTEMA DE COMISSÕES ===\n")
    
    tests = [
        test_imports,
        test_app_structure,
        test_app_creation,
        test_database_models
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! O sistema está pronto para uso.")
        print("\nPróximos passos:")
        print("1. Execute: python seed_database.py")
        print("2. Execute: python run.py")
        print("3. Acesse: http://127.0.0.1:5000")
    else:
        print("❌ Alguns testes falharam. Verifique os erros acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()
