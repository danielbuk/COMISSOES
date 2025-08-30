import pandas as pd
import oracledb
from flask import current_app
from .models import Vendedor, RegraComissao, ComissaoPadrao, DadosVendas, TipoVendedor, ProdutoEspecial
from . import db
from datetime import datetime
import os

# Inicializa o Oracle Instant Client
def init_oracle_client():
    """Inicializa o Oracle Instant Client"""
    try:
        # Caminho para o Oracle Instant Client
        instant_client_path = r"C:\oracle\instantclient_23_9"
        
        if os.path.exists(instant_client_path):
            # Adiciona o caminho ao PATH do sistema
            if instant_client_path not in os.environ.get('PATH', ''):
                os.environ['PATH'] = instant_client_path + os.pathsep + os.environ.get('PATH', '')
            
            # Inicializa o cliente Oracle
            oracledb.init_oracle_client(lib_dir=instant_client_path)
            print(f"✓ Oracle Instant Client inicializado: {instant_client_path}")
            return True
        else:
            print(f"⚠️ Oracle Instant Client não encontrado em: {instant_client_path}")
            return False
    except Exception as e:
        print(f"⚠️ Erro ao inicializar Oracle Instant Client: {e}")
        return False

# Inicializa o cliente na importação do módulo
init_oracle_client()

def fetch_sales_data_from_oracle(mes, ano):
    """Conecta ao Oracle, executa a query e retorna um DataFrame Pandas."""
    config = current_app.config
    try:
        with oracledb.connect(user=config['ORACLE_USER'], password=config['ORACLE_PASSWORD'], dsn=config['ORACLE_DSN']) as connection:
            # Query com filtro por mês e ano usando DATA_VENDA
            query = f"""
            SELECT * FROM DADOS_FATURAMENTO 
            WHERE EXTRACT(MONTH FROM DATA_VENDA) = {mes}
            AND EXTRACT(YEAR FROM DATA_VENDA) = {ano}
            """
            df = pd.read_sql(query, connection)
            
            # Renomear colunas para corresponder à lógica do script original
            column_mapping = {
                'CODIGO_VENDEDOR': 'sellerCode',
                'NOME_VENDEDOR': 'sellerName',
                'CODIGO_PRODUTO': 'productCode',
                'DESCRICAO_PRODUTO': 'productDesc',
                'FATURAMENTO_LIQUIDO': 'revenue',  # Usando FATURAMENTO_LIQUIDO para ficar certinho
                'DEVOLUCAO': 'valorRetMerc',
                'CUSTO_FIN_FAT': 'valorTituloAberto',
                'CUSTO_FIN_DEV': 'valorAcrescTituloPagoMesAnt'
            }
            df.rename(columns=column_mapping, inplace=True)

            # Garantir que os tipos de dados estejam corretos
            df['sellerCode'] = pd.to_numeric(df['sellerCode'], errors='coerce')
            df['productCode'] = df['productCode'].astype(str)
            numeric_cols = ['revenue', 'valorRetMerc', 'valorTituloAberto', 'valorAcrescTituloPagoMesAnt']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Garantir que os nomes dos vendedores não estejam vazios
            df['sellerName'] = df['sellerName'].fillna('Vendedor Desconhecido')
            
            print(f"Dados do Oracle carregados: {len(df)} registros")
            print(f"Vendedores únicos: {df['sellerCode'].nunique()}")
            print(f"Primeiros nomes de vendedores: {df['sellerName'].head().tolist()}")
            
            return df
    except Exception as e:
        print(f"Erro ao conectar ou buscar dados do Oracle: {e}")
        return pd.DataFrame()

def save_sales_data_to_cache(df, mes, ano):
    """Salva os dados do DataFrame no cache local e atualiza nomes de vendedores."""
    if df.empty:
        return False
    
    try:
        # Primeiro, remove dados existentes para este mês/ano
        DadosVendas.query.filter_by(mes=mes, ano=ano).delete()
        
        # APAGA TODOS os vendedores existentes e adiciona apenas os do Oracle
        print("🗑️ Apagando todos os vendedores existentes...")
        Vendedor.query.delete()
        
        # Adiciona apenas os vendedores que vêm do Oracle
        vendedores_no_df = df[['sellerCode', 'sellerName']].drop_duplicates().to_dict('records')
        print(f"➕ Adicionando {len(vendedores_no_df)} vendedores do Oracle:")
        
        for v_data in vendedores_no_df:
            print(f"   - RCA {v_data['sellerCode']}: {v_data['sellerName']}")
            novo_vendedor = Vendedor(
                rca=v_data['sellerCode'], 
                nome=v_data['sellerName'],
                tipo=TipoVendedor.EXTERNO,
                is_cooperativa=False,
                ignorar_no_relatorio=False
            )
            db.session.add(novo_vendedor)

        db.session.commit()
        
        # Insere os novos dados de vendas
        for _, row in df.iterrows():
            dados = DadosVendas(
                mes=mes,
                ano=ano,
                seller_code=int(row['sellerCode']),
                seller_name=str(row['sellerName']),
                product_code=str(row['productCode']),
                product_desc=str(row['productDesc']),
                revenue=float(row['revenue']),
                valor_ret_merc=float(row['valorRetMerc']),
                valor_titulo_aberto=float(row['valorTituloAberto']),
                valor_acresc_titulo_pago_mes_ant=float(row['valorAcrescTituloPagoMesAnt'])
            )
            db.session.add(dados)
        
        db.session.commit()
        return True
    except Exception as e:
        print(f"Erro ao salvar dados no cache: {e}")
        db.session.rollback()
        return False

def get_sales_data_from_cache(mes, ano):
    """Busca dados de vendas do cache local"""
    try:
        dados = DadosVendas.query.filter_by(mes=mes, ano=ano).all()
        if not dados:
            return pd.DataFrame()
        
        # Converte para DataFrame
        df_data = []
        for d in dados:
            df_data.append({
                'sellerCode': d.seller_code,
                'sellerName': d.seller_name,
                'productCode': d.product_code,
                'productDesc': d.product_desc,
                'revenue': d.revenue,
                'valorRetMerc': d.valor_ret_merc,
                'valorTituloAberto': d.valor_titulo_aberto,
                'valorAcrescTituloPagoMesAnt': d.valor_acresc_titulo_pago_mes_ant
            })
        
        return pd.DataFrame(df_data)
    except Exception as e:
        print(f"Erro ao buscar dados do cache: {e}")
        return pd.DataFrame()

def import_month_data(mes, ano):
    """Importa dados de um mês específico do Oracle para o cache local"""
    print(f"🔄 Importando dados para {mes}/{ano}...")
    
    # Busca dados do Oracle
    df = fetch_sales_data_from_oracle(mes, ano)
    
    if df.empty:
        return False, "Nenhum dado encontrado no Oracle para este período"
    
    print(f"📊 Encontrados {len(df)} registros no Oracle")
    print(f"👥 Vendedores únicos encontrados: {df['sellerCode'].nunique()}")
    print(f"📋 Lista de vendedores do Oracle:")
    vendedores_unicos = df[['sellerCode', 'sellerName']].drop_duplicates().sort_values('sellerCode')
    for _, v in vendedores_unicos.iterrows():
        print(f"   - RCA {v['sellerCode']}: {v['sellerName']}")
    
    # Salva no cache local
    success = save_sales_data_to_cache(df, mes, ano)
    
    if success:
        return True, f"✅ Dados importados com sucesso: {len(df)} registros"
    else:
        return False, "❌ Erro ao salvar dados no cache local"

def get_available_months():
    """Retorna lista de meses/anos disponíveis no cache"""
    try:
        # Busca meses únicos no cache
        meses = db.session.query(DadosVendas.mes, DadosVendas.ano).distinct().all()
        return sorted(meses, key=lambda x: (x[1], x[0]))  # Ordena por ano, depois mês
    except Exception as e:
        print(f"Erro ao buscar meses disponíveis: {e}")
        return []

def get_commission_rate(vendedor_rca, product_code):
    """Busca a taxa de comissão correta seguindo a hierarquia de prioridades."""
    session = db.session
    
    # 1. Regra mais específica: Vendedor + Produto específico
    rule = session.query(RegraComissao).filter_by(
        vendedor_rca=vendedor_rca, 
        codigo_produto=product_code
    ).first()
    if rule:
        return rule.taxa_comissao

    # 2. Produto especial (aplica-se a todos os vendedores)
    produto_especial = session.query(ProdutoEspecial).filter_by(codigo_produto=product_code).first()
    if produto_especial:
        return produto_especial.taxa_comissao

    # 3. Regra por Produto (aplica-se a todos os vendedores) - mantido para compatibilidade
    rule = session.query(RegraComissao).filter_by(
        vendedor_rca=None, 
        codigo_produto=product_code
    ).first()
    if rule:
        return rule.taxa_comissao

    # 4. Comissão padrão do vendedor
    comissao_padrao = session.query(ComissaoPadrao).filter_by(vendedor_rca=vendedor_rca).first()
    if comissao_padrao:
        return comissao_padrao.taxa_comissao
        
    # 5. Taxa padrão fallback (não deveria acontecer se o banco estiver bem populado)
    return 0.015

def process_commissions(mes=None, ano=None):
    """Orquestra o processo: busca dados, aplica regras, calcula e estrutura o resultado."""
    # Se não especificou mês/ano, usa o mês atual
    if mes is None or ano is None:
        now = datetime.now()
        mes = now.month
        ano = now.year
    
    # Busca dados do cache local
    sales_df = get_sales_data_from_cache(mes, ano)
    
    if sales_df.empty:
        return {}, f"Nenhum dado encontrado para {mes}/{ano}. Importe os dados primeiro."
    
    # Obter lista de vendedores a serem ignorados
    ignored_sellers = [v.rca for v in Vendedor.query.filter_by(ignorar_no_relatorio=True).all()]
    sales_df = sales_df[~sales_df['sellerCode'].isin(ignored_sellers)]
    
    # Aplicar a função get_commission_rate para cada linha para obter a taxa
    sales_df['commissionRate'] = sales_df.apply(
        lambda row: get_commission_rate(row['sellerCode'], row['productCode']),
        axis=1
    )
    
    # Calcular a comissão
    sales_df['commission'] = sales_df['revenue'] * sales_df['commissionRate']
    
    # Agrupar e agregar os resultados por vendedor
    grouped = sales_df.groupby('sellerCode')
    
    seller_data = {}
    
    # Produtos com comissão modificada (produtos especiais + regras específicas)
    produtos_especiais_cod = [p.codigo_produto for p in ProdutoEspecial.query.all()]
    regras_especiais_cod = [r.codigo_produto for r in RegraComissao.query.filter(
        RegraComissao.vendedor_rca == None, 
        RegraComissao.codigo_produto != None
    ).all()]
    produtos_comissao_modificada = list(set(produtos_especiais_cod + regras_especiais_cod))

    for seller_code, group in grouped:
        seller_info = Vendedor.query.filter_by(rca=seller_code).first()
        if not seller_info:
            continue

        # Pega o nome do vendedor do DataFrame, que veio do Oracle
        seller_name = group['sellerName'].iloc[0] if not group.empty else seller_info.nome
            
        # Separar produtos em apenas duas categorias
        produtos_comissao_modificada_df = group[group['productCode'].isin(produtos_comissao_modificada)]
        outros_produtos = group[~group['productCode'].isin(produtos_comissao_modificada)]

        seller_data[seller_code] = {
            'name': seller_name,
            'type': seller_info.tipo.value,
            'is_cooperativa': seller_info.is_cooperativa,
            'totalRevenue': group['revenue'].sum(),
            'details': {
                'produtos_comissao_modificada': {
                    'revenue': produtos_comissao_modificada_df['revenue'].sum() if not produtos_comissao_modificada_df.empty else 0,
                    'commission': produtos_comissao_modificada_df['commission'].sum() if not produtos_comissao_modificada_df.empty else 0,
                    'valorRetMerc': produtos_comissao_modificada_df['valorRetMerc'].sum() if not produtos_comissao_modificada_df.empty else 0,
                    'valorTituloAberto': produtos_comissao_modificada_df['valorTituloAberto'].sum() if not produtos_comissao_modificada_df.empty else 0,
                    'valorAcrescTituloPagoMesAnt': produtos_comissao_modificada_df['valorAcrescTituloPagoMesAnt'].sum() if not produtos_comissao_modificada_df.empty else 0,
                },
                'outros_produtos': {
                    'revenue': outros_produtos['revenue'].sum() if not outros_produtos.empty else 0,
                    'commission': outros_produtos['commission'].sum() if not outros_produtos.empty else 0,
                    'valorRetMerc': outros_produtos['valorRetMerc'].sum() if not outros_produtos.empty else 0,
                    'valorTituloAberto': outros_produtos['valorTituloAberto'].sum() if not outros_produtos.empty else 0,
                    'valorAcrescTituloPagoMesAnt': outros_produtos['valorAcrescTituloPagoMesAnt'].sum() if not outros_produtos.empty else 0,
                }
            },
            'totalCommission': group['commission'].sum(),
            'totalRetMerc': group['valorRetMerc'].sum(),
            'totalTitleOpen': group['valorTituloAberto'].sum(),
            'totalTitleAdded': group['valorAcrescTituloPagoMesAnt'].sum(),
        }

    # Ordenar vendedores por faturamento total (do maior para o menor)
    sorted_sellers = dict(sorted(seller_data.items(), key=lambda item: item[1]['totalRevenue'], reverse=True))

    return sorted_sellers, f"Relatório gerado para {mes}/{ano}"
