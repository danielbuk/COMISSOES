#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados iniciais.
"""

from app import create_app, db
from app.models import Vendedor, TipoVendedor, RegraComissao, ComissaoPadrao, DadosVendas

# Lista de RCAs (vendedores) - apenas CODIGO_VENDEDOR e NOME_VENDEDOR
rcas = [
    (1, "LEANDRO FIALHO TRINDADE"),
    (2, "LEONARDO MARINHO VALLADAO"),
    (3, "MARCELO AUGUSTO SILVA"),
    (4, "RODRIGO FERREIRA SANTOS"),
    (5, "CARLOS EDUARDO LIMA"),
    (6, "FERNANDO COSTA OLIVEIRA"),
    (7, "RAFAEL MARTINS PEREIRA"),
    (8, "GUSTAVO HENRIQUE SOUZA"),
    (9, "LUCAS GABRIEL RODRIGUES"),
    (10, "MATHEUS ARAUJO FERREIRA"),
    (11, "BRUNO SILVA COSTA"),
    (12, "GABRIEL OLIVEIRA SANTOS"),
    (13, "PEDRO HENRIQUE LIMA"),
    (14, "THIAGO MARTINS PEREIRA"),
    (15, "VICTOR GABRIEL SOUZA"),
    (16, "DIEGO FERREIRA RODRIGUES"),
    (17, "ANDRE LIMA COSTA"),
    (18, "RICARDO SANTOS OLIVEIRA"),
    (19, "FELIPE MARTINS PEREIRA"),
    (20, "DANIEL SOUZA FERREIRA"),
    (21, "JOÃO PEDRO RODRIGUES"),
    (22, "MIGUEL LIMA COSTA"),
    (23, "ARTHUR SANTOS OLIVEIRA"),
    (24, "BERNARDO MARTINS PEREIRA"),
    (25, "HEITOR SOUZA FERREIRA"),
    (26, "DANTE RODRIGUES LIMA"),
    (27, "CAIO COSTA SANTOS"),
    (28, "ENZO OLIVEIRA MARTINS"),
    (29, "VALENTIM PEREIRA SOUZA"),
    (30, "BENJAMIN FERREIRA RODRIGUES"),
    (31, "DAVI LIMA COSTA"),
    (32, "THEO SANTOS OLIVEIRA"),
    (33, "NOAH MARTINS PEREIRA"),
    (34, "NICOLAS SOUZA FERREIRA"),
    (35, "SAMUEL RODRIGUES LIMA"),
    (36, "BENICIO COSTA SANTOS"),
    (37, "GABRIEL OLIVEIRA MARTINS"),
    (38, "RAFAEL PEREIRA SOUZA"),
    (39, "JOAQUIM FERREIRA RODRIGUES"),
    (40, "ISAAC LIMA COSTA"),
    (41, "ANTHONY SANTOS OLIVEIRA"),
    (42, "ISAAC MARTINS PEREIRA"),
    (43, "ALFREDO SOUZA FERREIRA"),
    (44, "OSCAR RODRIGUES LIMA"),
    (45, "THEODORO COSTA SANTOS"),
    (46, "JAYDEN OLIVEIRA MARTINS"),
    (47, "BENNETT PEREIRA SOUZA"),
    (48, "CHRISTIAN FERREIRA RODRIGUES"),
    (49, "ANDREW LIMA COSTA"),
    (50, "JUDE SANTOS OLIVEIRA"),
    (51, "FINN MARTINS PEREIRA"),
    (52, "BRODY SOUZA FERREIRA"),
    (53, "SEAN RODRIGUES LIMA"),
    (54, "RONAN COSTA SANTOS"),
    (55, "CALLEN OLIVEIRA MARTINS"),
    (56, "TRIX PEREIRA SOUZA"),
    (57, "BRENDIS FERREIRA RODRIGUES"),
    (58, "JAXON LIMA COSTA"),
    (59, "SANTOS OLIVEIRA MARTINS"),
    (60, "BOWEN PEREIRA SOUZA"),
    (61, "DORIAN FERREIRA RODRIGUES"),
    (62, "EDEN LIMA COSTA"),
    (63, "KAI SANTOS OLIVEIRA"),
    (64, "CALVIN MARTINS PEREIRA"),
    (65, "CHANDLER SOUZA FERREIRA"),
    (66, "MYLES RODRIGUES LIMA"),
    (67, "CHRISTOPHER COSTA SANTOS"),
    (68, "MAXWELL OLIVEIRA MARTINS"),
    (69, "RYAN PEREIRA SOUZA"),
    (70, "MILES FERREIRA RODRIGUES"),
    (71, "MICHAEL LIMA COSTA"),
    (72, "JASON SANTOS OLIVEIRA"),
    (73, "EMMETT MARTINS PEREIRA"),
    (74, "JAYCE SOUZA FERREIRA"),
    (75, "BRANTLEY RODRIGUES LIMA"),
    (76, "AXEL COSTA SANTOS"),
    (77, "EMERY OLIVEIRA MARTINS"),
    (78, "MAXIMUS PEREIRA SOUZA"),
    (79, "HANK FERREIRA RODRIGUES"),
    (80, "LEONIDAS LIMA COSTA"),
    (81, "SULLIVAN SANTOS OLIVEIRA"),
    (82, "CHANDLER MARTINS PEREIRA"),
    (83, "MICHELLE SOUZA FERREIRA"),  # PEPSICO
    (84, "COOPERATIVA A"),  # Cooperativa
    (85, "COOPERATIVA B"),  # Cooperativa
    (86, "COOPERATIVA C"),  # Cooperativa
]

# Comissões padrão por vendedor
comissoes_padrao = [
    # RCA 1 e 2 têm 2% de comissão padrão
    (1, 0.02),
    (2, 0.02),
    # Demais vendedores têm 1,5% de comissão padrão
    (3, 0.015), (4, 0.015), (5, 0.015), (6, 0.015), (7, 0.015), (8, 0.015), (9, 0.015), (10, 0.015),
    (11, 0.015), (12, 0.015), (13, 0.015), (14, 0.015), (15, 0.015), (16, 0.015), (17, 0.015), (18, 0.015),
    (19, 0.015), (20, 0.015), (21, 0.015), (22, 0.015), (23, 0.015), (24, 0.015), (25, 0.015), (26, 0.015),
    (27, 0.015), (28, 0.015), (29, 0.015), (30, 0.015), (31, 0.015), (32, 0.015), (33, 0.015), (34, 0.015),
    (35, 0.015), (36, 0.015), (37, 0.015), (38, 0.015), (39, 0.015), (40, 0.015), (41, 0.015), (42, 0.015),
    (43, 0.015), (44, 0.015), (45, 0.015), (46, 0.015), (47, 0.015), (48, 0.015), (49, 0.015), (50, 0.015),
    (51, 0.015), (52, 0.015), (53, 0.015), (54, 0.015), (55, 0.015), (56, 0.015), (57, 0.015), (58, 0.015),
    (59, 0.015), (60, 0.015), (61, 0.015), (62, 0.015), (63, 0.015), (64, 0.015), (65, 0.015), (66, 0.015),
    (67, 0.015), (68, 0.015), (69, 0.015), (70, 0.015), (71, 0.015), (72, 0.015), (73, 0.015), (74, 0.015),
    (75, 0.015), (76, 0.015), (77, 0.015), (78, 0.015), (79, 0.015), (80, 0.015), (81, 0.015), (82, 0.015),
    (83, 0.015), (84, 0.015), (85, 0.015), (86, 0.015),
]

# Regras de comissão específicas por produto (exemplos)
regras_comissao = [
    # Michelle (RCA 83) - produtos PEPSICO
    (83, "123", 0.025),  # Michelle + Produto 123 = 2.5%
    (83, "456", 0.025),  # Michelle + Produto 456 = 2.5%
    (83, "789", 0.025),  # Michelle + Produto 789 = 2.5%
    
    # Produtos especiais (aplicam-se a todos os vendedores)
    (None, "100", 0.03),   # Produto 100 = 3% para todos
    (None, "200", 0.025),  # Produto 200 = 2.5% para todos
    (None, "300", 0.02),   # Produto 300 = 2% para todos
    (None, "400", 0.015),  # Produto 400 = 1.5% para todos
    (None, "500", 0.01),   # Produto 500 = 1% para todos
]

app = create_app()

with app.app_context():
    # Limpa o banco de dados
    print("🗑️ Limpando banco de dados...")
    db.drop_all()
    db.create_all()
    
    # Adiciona vendedores
    print("👥 Adicionando vendedores...")
    for rca, nome in rcas:
        vendedor = Vendedor(
            rca=rca,
            nome=nome,
            tipo=TipoVendedor.EXTERNO,
            is_cooperativa=rca >= 84,  # RCAs 84+ são cooperativas
            ignorar_no_relatorio=False
        )
        db.session.add(vendedor)
    
    # Adiciona comissões padrão
    print("💰 Adicionando comissões padrão...")
    for vendedor_rca, taxa_comissao in comissoes_padrao:
        comissao = ComissaoPadrao(
            vendedor_rca=vendedor_rca,
            taxa_comissao=taxa_comissao
        )
        db.session.add(comissao)
    
    # Adiciona regras de comissão específicas
    print("📋 Adicionando regras de comissão específicas...")
    for vendedor_rca, codigo_produto, taxa_comissao in regras_comissao:
        regra = RegraComissao(
            vendedor_rca=vendedor_rca,
            codigo_produto=codigo_produto,
            taxa_comissao=taxa_comissao
        )
        db.session.add(regra)
    
    # Commit das alterações
    db.session.commit()
    
    print("✅ Banco de dados populado com sucesso!")
    print("📊 Estatísticas:")
    print(f"   - {len(rcas)} vendedores cadastrados")
    print(f"   - {len(comissoes_padrao)} comissões padrão criadas")
    print(f"   - {len(regras_comissao)} regras de comissão específicas criadas")
    print(f"   - {len([r for r in rcas if r[0] >= 84])} vendedores da cooperativa")
    print("\n🚀 Próximos passos:")
    print("1. Executar: python run.py")
    print("2. Acessar: http://127.0.0.1:5000")
    print("3. Importar dados de meses específicos do Oracle")
    print("4. Gerenciar vendedores da cooperativa em /cadastro")
    print("5. Gerenciar comissões em /comissoes")
