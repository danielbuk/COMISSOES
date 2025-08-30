from . import db
import enum
from datetime import datetime

class TipoVendedor(enum.Enum):
    INTERNO = "Interno"
    EXTERNO = "Externo"

class Vendedor(db.Model):
    """Modelo para vendedores"""
    rca = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.Enum(TipoVendedor), nullable=False, default=TipoVendedor.EXTERNO)
    is_cooperativa = db.Column(db.Boolean, default=False)  # Novo campo para cooperativa
    ignorar_no_relatorio = db.Column(db.Boolean, default=False)

class ComissaoPadrao(db.Model):
    """Modelo para comissões padrão por vendedor"""
    id = db.Column(db.Integer, primary_key=True)
    vendedor_rca = db.Column(db.Integer, db.ForeignKey('vendedor.rca'), nullable=False, unique=True)
    taxa_comissao = db.Column(db.Float, nullable=False)
    
    # Relacionamento
    vendedor = db.relationship('Vendedor', backref='comissao_padrao')

class RegraComissao(db.Model):
    """Modelo para regras de comissão específicas por produto"""
    id = db.Column(db.Integer, primary_key=True)
    vendedor_rca = db.Column(db.Integer, db.ForeignKey('vendedor.rca'), nullable=True)
    codigo_produto = db.Column(db.String(50), nullable=False)
    taxa_comissao = db.Column(db.Float, nullable=False)
    
    # Relacionamento
    vendedor = db.relationship('Vendedor', backref='regras_comissao')
    
    # Índice único para evitar duplicatas
    __table_args__ = (
        db.UniqueConstraint('vendedor_rca', 'codigo_produto', name='uq_vendedor_produto'),
    )

class ProdutoEspecial(db.Model):
    """Modelo para produtos com comissão especial"""
    id = db.Column(db.Integer, primary_key=True)
    codigo_produto = db.Column(db.String(50), nullable=False, unique=True)
    nome_produto = db.Column(db.String(255), nullable=False)
    taxa_comissao = db.Column(db.Float, nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

class ProdutoOracleCache(db.Model):
    """Modelo para cache local de produtos do Oracle"""
    id = db.Column(db.Integer, primary_key=True)
    codigo_produto = db.Column(db.String(50), nullable=False, unique=True)
    nome_produto = db.Column(db.String(255), nullable=False)
    data_sincronizacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Índice para busca rápida
    __table_args__ = (
        db.Index('idx_codigo_produto', 'codigo_produto'),
        db.Index('idx_nome_produto', 'nome_produto'),
    )

class DadosVendas(db.Model):
    """Modelo para armazenar dados de vendas em cache local"""
    id = db.Column(db.Integer, primary_key=True)
    mes = db.Column(db.Integer, nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    seller_code = db.Column(db.Integer, nullable=False)
    seller_name = db.Column(db.String(150), nullable=False)
    product_code = db.Column(db.String(50), nullable=False)
    product_desc = db.Column(db.String(255), nullable=False)
    revenue = db.Column(db.Float, default=0.0)
    valor_ret_merc = db.Column(db.Float, default=0.0)
    valor_titulo_aberto = db.Column(db.Float, default=0.0)
    valor_acresc_titulo_pago_mes_ant = db.Column(db.Float, default=0.0)
    data_importacao = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (
        db.Index('idx_mes_ano_vendedor_produto', 'mes', 'ano', 'seller_code', 'product_code'),
    )

class AjusteFinanceiro(db.Model):
    """Modelo para armazenar ajustes financeiros manuais por vendedor e período"""
    id = db.Column(db.Integer, primary_key=True)
    vendedor_rca = db.Column(db.Integer, db.ForeignKey('vendedor.rca'), nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    valor_titulo_aberto = db.Column(db.Float, default=0.0)
    valor_ret_merc = db.Column(db.Float, default=0.0)
    valor_acresc_titulo_pago_mes_ant = db.Column(db.Float, default=0.0)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    vendedor = db.relationship('Vendedor', backref='ajustes_financeiros')
    
    # Índice único para evitar duplicatas por vendedor/período
    __table_args__ = (
        db.UniqueConstraint('vendedor_rca', 'mes', 'ano', name='uq_vendedor_mes_ano'),
        db.Index('idx_vendedor_mes_ano', 'vendedor_rca', 'mes', 'ano'),
    )
