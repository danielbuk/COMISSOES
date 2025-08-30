from flask import render_template, request, jsonify, redirect, url_for
from . import app
from .services import process_commissions, import_month_data, get_available_months
from .models import Vendedor, RegraComissao, ComissaoPadrao, db
from datetime import datetime

@app.route('/')
def index():
    """Página inicial com seleção de mês"""
    # Busca meses disponíveis no cache
    available_months = get_available_months()
    
    # Mês atual como padrão
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    return render_template('index.html', 
                         available_months=available_months,
                         current_month=current_month,
                         current_year=current_year)

@app.route('/relatorio')
def report():
    """Página do relatório com seleção de mês"""
    mes = request.args.get('mes', type=int)
    ano = request.args.get('ano', type=int)
    
    if not mes or not ano:
        # Redireciona para a página inicial se não especificou mês/ano
        return redirect(url_for('index'))
    
    commission_data, message = process_commissions(mes, ano)
    
    return render_template('relatorio.html', 
                         sellers=commission_data, 
                         mes=mes, 
                         ano=ano, 
                         message=message)

@app.route('/importar', methods=['POST'])
def import_data():
    """Importa dados de um mês específico do Oracle"""
    mes = request.form.get('mes', type=int)
    ano = request.form.get('ano', type=int)
    
    if not mes or not ano:
        return jsonify({'success': False, 'message': 'Mês e ano são obrigatórios'})
    
    success, message = import_month_data(mes, ano)
    
    return jsonify({'success': success, 'message': message})

@app.route('/cadastro')
def cadastro():
    """Página de cadastro de vendedores da cooperativa"""
    vendedores = Vendedor.query.order_by(Vendedor.nome).all()
    return render_template('cadastro.html', vendedores=vendedores)

@app.route('/comissoes')
def comissoes():
    """Página de cadastro de comissões"""
    vendedores = Vendedor.query.order_by(Vendedor.nome).all()
    comissoes_padrao = ComissaoPadrao.query.all()
    regras_comissao = RegraComissao.query.all()
    
    return render_template('comissoes.html', 
                         vendedores=vendedores,
                         comissoes_padrao=comissoes_padrao,
                         regras_comissao=regras_comissao)

@app.route('/api/vendedores', methods=['GET'])
def get_vendedores():
    """API para buscar vendedores"""
    vendedores = Vendedor.query.order_by(Vendedor.nome).all()
    return jsonify([{
        'rca': v.rca,
        'nome': v.nome,
        'tipo': v.tipo.value,
        'is_cooperativa': v.is_cooperativa,
        'ignorar_no_relatorio': v.ignorar_no_relatorio
    } for v in vendedores])

@app.route('/api/vendedores/<int:rca>', methods=['PUT'])
def update_vendedor(rca):
    """API para atualizar vendedor"""
    try:
        data = request.get_json()
        vendedor = Vendedor.query.filter_by(rca=rca).first()
        
        if not vendedor:
            return jsonify({'success': False, 'message': 'Vendedor não encontrado'}), 404
        
        # Atualiza os campos
        if 'is_cooperativa' in data:
            vendedor.is_cooperativa = data['is_cooperativa']
        if 'ignorar_no_relatorio' in data:
            vendedor.ignorar_no_relatorio = data['ignorar_no_relatorio']
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Vendedor atualizado com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao atualizar: {str(e)}'}), 500

@app.route('/api/comissoes-padrao', methods=['GET'])
def get_comissoes_padrao():
    """API para buscar comissões padrão"""
    comissoes = ComissaoPadrao.query.all()
    return jsonify([{
        'id': c.id,
        'vendedor_rca': c.vendedor_rca,
        'vendedor_nome': c.vendedor.nome,
        'taxa_comissao': c.taxa_comissao
    } for c in comissoes])

@app.route('/api/comissoes-padrao/<int:rca>', methods=['PUT'])
def update_comissao_padrao(rca):
    """API para atualizar comissão padrão"""
    try:
        data = request.get_json()
        comissao = ComissaoPadrao.query.filter_by(vendedor_rca=rca).first()
        
        if not comissao:
            return jsonify({'success': False, 'message': 'Comissão padrão não encontrada'}), 404
        
        if 'taxa_comissao' in data:
            comissao.taxa_comissao = float(data['taxa_comissao'])
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Comissão padrão atualizada com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao atualizar: {str(e)}'}), 500

@app.route('/api/regras-comissao', methods=['GET'])
def get_regras_comissao():
    """API para buscar regras de comissão"""
    regras = RegraComissao.query.all()
    return jsonify([{
        'id': r.id,
        'vendedor_rca': r.vendedor_rca,
        'vendedor_nome': r.vendedor.nome if r.vendedor else 'Todos',
        'codigo_produto': r.codigo_produto,
        'taxa_comissao': r.taxa_comissao
    } for r in regras])

@app.route('/api/regras-comissao', methods=['POST'])
def create_regra_comissao():
    """API para criar nova regra de comissão"""
    try:
        data = request.get_json()
        
        # Verifica se já existe uma regra para este vendedor/produto
        existing = RegraComissao.query.filter_by(
            vendedor_rca=data.get('vendedor_rca'),
            codigo_produto=data['codigo_produto']
        ).first()
        
        if existing:
            return jsonify({'success': False, 'message': 'Já existe uma regra para este vendedor/produto'}), 400
        
        regra = RegraComissao(
            vendedor_rca=data.get('vendedor_rca'),
            codigo_produto=data['codigo_produto'],
            taxa_comissao=float(data['taxa_comissao'])
        )
        
        db.session.add(regra)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Regra de comissão criada com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao criar: {str(e)}'}), 500

@app.route('/api/regras-comissao/<int:regra_id>', methods=['DELETE'])
def delete_regra_comissao(regra_id):
    """API para deletar regra de comissão"""
    try:
        regra = RegraComissao.query.get(regra_id)
        
        if not regra:
            return jsonify({'success': False, 'message': 'Regra não encontrada'}), 404
        
        db.session.delete(regra)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Regra de comissão deletada com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao deletar: {str(e)}'}), 500

@app.route('/api/meses-disponiveis')
def api_available_months():
    """API para buscar meses disponíveis"""
    months = get_available_months()
    return jsonify([{'mes': m[0], 'ano': m[1]} for m in months])
