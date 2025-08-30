from flask import render_template, request, jsonify, redirect, url_for, send_file
from . import app
from .services import process_commissions, import_month_data, get_available_months, sincronizar_produtos_oracle, buscar_produtos_cache, obter_estatisticas_cache
from .models import Vendedor, RegraComissao, ComissaoPadrao, ProdutoEspecial, db, AjusteFinanceiro, AjusteFaturamento
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO

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

@app.route('/produtos-especiais')
def produtos_especiais():
    """Página de cadastro de produtos especiais"""
    produtos = ProdutoEspecial.query.order_by(ProdutoEspecial.nome_produto).all()
    return render_template('produtos_especiais.html', produtos=produtos)

@app.route('/api/produtos-especiais', methods=['GET'])
def get_produtos_especiais():
    """API para buscar produtos especiais"""
    produtos = ProdutoEspecial.query.order_by(ProdutoEspecial.nome_produto).all()
    return jsonify([{
        'id': p.id,
        'codigo_produto': p.codigo_produto,
        'nome_produto': p.nome_produto,
        'taxa_comissao': p.taxa_comissao,
        'data_cadastro': p.data_cadastro.strftime('%d/%m/%Y %H:%M')
    } for p in produtos])

@app.route('/api/produtos-especiais', methods=['POST'])
def create_produto_especial():
    """API para criar novo produto especial"""
    try:
        data = request.get_json()
        
        # Verifica se já existe um produto com este código
        existing = ProdutoEspecial.query.filter_by(codigo_produto=data['codigo_produto']).first()
        if existing:
            return jsonify({'success': False, 'message': 'Já existe um produto com este código'}), 400
        
        produto = ProdutoEspecial(
            codigo_produto=data['codigo_produto'],
            nome_produto=data['nome_produto'],
            taxa_comissao=float(data['taxa_comissao'])
        )
        
        db.session.add(produto)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Produto especial criado com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao criar: {str(e)}'}), 500

@app.route('/api/produtos-especiais/<int:produto_id>', methods=['PUT'])
def update_produto_especial(produto_id):
    """API para atualizar produto especial"""
    try:
        data = request.get_json()
        produto = ProdutoEspecial.query.get(produto_id)
        
        if not produto:
            return jsonify({'success': False, 'message': 'Produto não encontrado'}), 404
        
        # Verifica se o código já existe em outro produto
        if 'codigo_produto' in data and data['codigo_produto'] != produto.codigo_produto:
            existing = ProdutoEspecial.query.filter_by(codigo_produto=data['codigo_produto']).first()
            if existing:
                return jsonify({'success': False, 'message': 'Já existe um produto com este código'}), 400
        
        # Atualiza os campos
        if 'codigo_produto' in data:
            produto.codigo_produto = data['codigo_produto']
        if 'nome_produto' in data:
            produto.nome_produto = data['nome_produto']
        if 'taxa_comissao' in data:
            produto.taxa_comissao = float(data['taxa_comissao'])
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Produto especial atualizado com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao atualizar: {str(e)}'}), 500

@app.route('/api/produtos-especiais/<int:produto_id>', methods=['DELETE'])
def delete_produto_especial(produto_id):
    """API para deletar produto especial"""
    try:
        produto = ProdutoEspecial.query.get(produto_id)
        
        if not produto:
            return jsonify({'success': False, 'message': 'Produto não encontrado'}), 404
        
        db.session.delete(produto)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Produto especial deletado com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao deletar: {str(e)}'}), 500

@app.route('/api/produtos-oracle')
def get_produtos_oracle():
    """API para buscar produtos únicos do Oracle"""
    try:
        import oracledb
        from flask import current_app
        
        config = current_app.config
        with oracledb.connect(user=config['ORACLE_USER'], password=config['ORACLE_PASSWORD'], dsn=config['ORACLE_DSN']) as connection:
            # Query para buscar produtos únicos
            query = """
            SELECT DISTINCT CODIGO_PRODUTO, DESCRICAO_PRODUTO 
            FROM DADOS_FATURAMENTO 
            WHERE CODIGO_PRODUTO IS NOT NULL 
            AND DESCRICAO_PRODUTO IS NOT NULL
            ORDER BY CODIGO_PRODUTO
            """
            
            cursor = connection.cursor()
            cursor.execute(query)
            produtos = []
            
            for row in cursor.fetchall():
                produtos.append({
                    'codigo': str(row[0]),
                    'descricao': str(row[1])
                })
            
            return jsonify({'success': True, 'produtos': produtos})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao buscar produtos: {str(e)}'}), 500

@app.route('/api/produtos-oracle-cached')
def get_produtos_oracle_cached():
    """API para buscar produtos do cache local com filtro"""
    try:
        filtro = request.args.get('filtro', '').strip()
        limite = request.args.get('limite', 50, type=int)
        
        produtos = buscar_produtos_cache(filtro, limite)
        
        return jsonify({
            'success': True, 
            'produtos': produtos,
            'total_encontrado': len(produtos)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao buscar produtos: {str(e)}'}), 500

@app.route('/api/sincronizar-produtos-oracle', methods=['POST'])
def sincronizar_produtos():
    """API para sincronizar produtos do Oracle com o cache local"""
    try:
        success, message = sincronizar_produtos_oracle()
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro na sincronização: {str(e)}'}), 500

@app.route('/api/estatisticas-cache')
def get_estatisticas_cache():
    """API para obter estatísticas do cache de produtos"""
    try:
        stats = obter_estatisticas_cache()
        return jsonify({
            'success': True,
            'estatisticas': stats
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao obter estatísticas: {str(e)}'}), 500

@app.route('/api/meses-disponiveis')
def api_available_months():
    """API para buscar meses disponíveis"""
    months = get_available_months()
    return jsonify([{'mes': m[0], 'ano': m[1]} for m in months])

@app.route('/api/ajuste-financeiro/<int:rca>/<int:ano>/<int:mes>', methods=['GET'])
def get_ajuste_financeiro(rca, ano, mes):
    """API para buscar ajustes financeiros de um vendedor em um período específico"""
    try:
        ajuste = AjusteFinanceiro.query.filter_by(
            vendedor_rca=rca, 
            ano=ano, 
            mes=mes
        ).first()
        
        if ajuste:
            return jsonify({
                'success': True,
                'ajuste': {
                    'id': ajuste.id,
                    'vendedor_rca': ajuste.vendedor_rca,
                    'mes': ajuste.mes,
                    'ano': ajuste.ano,
                    'valor_titulo_aberto': ajuste.valor_titulo_aberto,
                    'valor_ret_merc': ajuste.valor_ret_merc,
                    'valor_acresc_titulo_pago_mes_ant': ajuste.valor_acresc_titulo_pago_mes_ant,
                    'data_criacao': ajuste.data_criacao.strftime('%d/%m/%Y %H:%M'),
                    'data_atualizacao': ajuste.data_atualizacao.strftime('%d/%m/%Y %H:%M')
                }
            })
        else:
            return jsonify({
                'success': True,
                'ajuste': {
                    'vendedor_rca': rca,
                    'mes': mes,
                    'ano': ano,
                    'valor_titulo_aberto': 0.0,
                    'valor_ret_merc': 0.0,
                    'valor_acresc_titulo_pago_mes_ant': 0.0
                }
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao buscar ajuste: {str(e)}'}), 500

@app.route('/api/ajuste-financeiro', methods=['POST'])
def create_or_update_ajuste_financeiro():
    """API para criar ou atualizar ajustes financeiros"""
    try:
        data = request.get_json()
        
        # Busca ajuste existente
        ajuste = AjusteFinanceiro.query.filter_by(
            vendedor_rca=data['vendedor_rca'],
            ano=data['ano'],
            mes=data['mes']
        ).first()
        
        if ajuste:
            # Atualiza ajuste existente
            ajuste.valor_titulo_aberto = float(data['valor_titulo_aberto'])
            ajuste.valor_ret_merc = float(data['valor_ret_merc'])
            ajuste.valor_acresc_titulo_pago_mes_ant = float(data['valor_acresc_titulo_pago_mes_ant'])
            ajuste.data_atualizacao = datetime.utcnow()
            message = 'Ajuste financeiro atualizado com sucesso'
        else:
            # Cria novo ajuste
            ajuste = AjusteFinanceiro(
                vendedor_rca=data['vendedor_rca'],
                ano=data['ano'],
                mes=data['mes'],
                valor_titulo_aberto=float(data['valor_titulo_aberto']),
                valor_ret_merc=float(data['valor_ret_merc']),
                valor_acresc_titulo_pago_mes_ant=float(data['valor_acresc_titulo_pago_mes_ant'])
            )
            db.session.add(ajuste)
            message = 'Ajuste financeiro criado com sucesso'
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': message,
            'ajuste_id': ajuste.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao salvar ajuste: {str(e)}'}), 500

@app.route('/relatorio/pdf')
def gerar_pdf_relatorio():
    """Gera e retorna um PDF do relatório de comissões"""
    try:
        mes = request.args.get('mes', type=int)
        ano = request.args.get('ano', type=int)
        
        if not mes or not ano:
            return jsonify({'success': False, 'message': 'Mês e ano são obrigatórios'}), 400
        
        # Obter dados do relatório
        commission_data, message = process_commissions(mes, ano)
        
        if not commission_data:
            return jsonify({'success': False, 'message': 'Nenhum dado encontrado para o período especificado'}), 404
        
        # Criar buffer de memória para o PDF
        pdf_buffer = BytesIO()
        
        # Criar documento PDF em orientação paisagem
        doc = SimpleDocTemplate(pdf_buffer, pagesize=landscape(A4))
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Center
            textColor=colors.darkblue
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=1,  # Center
            textColor=colors.grey
        )
        
        # Título do relatório
        story.append(Paragraph(f"Relatório de Comissões", title_style))
        story.append(Paragraph(f"{mes}/{ano}", subtitle_style))
        story.append(Spacer(1, 20))
        
        # NOVA LÓGICA PARA A TABELA ÚNICA

        # 1. Definir os cabeçalhos da tabela
        table_headers = [
            'VENDEDOR', 'FAT. ORACLE', 'AJUSTE FAT.', 'FAT. TOTAL', 
            'COM. ORACLE', 'COM. AJUSTE', 'COM. BASE', 
            '(+) PAGO MÊS ANT.', '(-) DEV.', '(-) TÍT. ABERTO', 'COM. FINAL'
        ]

        # 2. Preparar os dados da tabela, uma linha por vendedor
        table_data = [table_headers]

        for seller_code, seller in commission_data.items():
            # Consolidar dados das filiais para o PDF
            faturamento_oracle_total = 0
            comissao_oracle_total = 0
            
            # Verificar se filiais_data existe e acessar os dados
            if 'filiais_data' in seller:
                faturamento_oracle_total = (
                    seller['filiais_data'].get(1, {}).get('faturamentoOracle', 0) +
                    seller['filiais_data'].get(98, {}).get('faturamentoOracle', 0)
                )
                comissao_oracle_total = (
                    seller['filiais_data'].get(1, {}).get('comissaoBaseOracle', 0) +
                    seller['filiais_data'].get(98, {}).get('comissaoBaseOracle', 0)
                )
            else:
                # Fallback para estrutura antiga
                faturamento_oracle_total = seller.get('faturamentoOracle', 0)
                comissao_oracle_total = seller.get('comissaoBaseOracle', 0)

            # Formatar os valores como strings para o PDF
            row = [
                Paragraph(f"{seller['name']} ({seller_code})", styles['Normal']),
                f"R$ {faturamento_oracle_total:,.2f}",
                f"R$ {seller['ajusteFaturamento']['valorAjuste']:,.2f}",
                f"R$ {seller['faturamentoTotalConsolidado']:,.2f}",
                f"R$ {comissao_oracle_total:,.2f}",
                f"R$ {seller['comissaoDoAjuste']:,.2f}",
                f"R$ {seller['totalCommission']:,.2f}",
                f"R$ {seller['ajustesFinanceiros']['valorAcrescTituloPagoMesAnt']:,.2f}",
                f"R$ {seller['ajustesFinanceiros']['valorRetMerc']:,.2f}",
                f"R$ {seller['ajustesFinanceiros']['valorTituloAberto']:,.2f}",
                f"R$ {seller['comissaoFinalConsolidada']:,.2f}",
            ]
            table_data.append(row)

        # 3. Criar o objeto Tabela
        # Ajustar a largura das colunas conforme necessário
        col_widths = [2.2*inch, 1*inch, 0.9*inch, 1*inch, 0.9*inch, 0.9*inch, 0.9*inch, 1*inch, 0.8*inch, 0.9*inch, 1*inch]

        if len(table_data) > 1: # Só cria a tabela se houver dados
            table = Table(table_data, colWidths=col_widths)

            # 4. Aplicar um estilo de planilha
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),

                # Alinhamento das colunas de valores à direita
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                # Alinhamento da coluna de vendedor à esquerda
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),

                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white]),
            ])

            # Estilo para a última coluna (Comissão Final)
            table_style.add('BACKGROUND', (10, 1), (10, -1), colors.lightgreen)
            table_style.add('FONTNAME', (10, 1), (10, -1), 'Helvetica-Bold')

            table.setStyle(table_style)
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Resumo geral
        story.append(Paragraph("Resumo Geral", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        total_vendedores = len(commission_data)
        total_faturamento = sum(seller['faturamentoTotalConsolidado'] for seller in commission_data.values())
        total_comissao_base = sum(seller['totalCommission'] for seller in commission_data.values())
        total_comissao_final = sum(seller['comissaoFinalConsolidada'] for seller in commission_data.values())
        
        summary_data = [
            ['Total de Vendedores', 'Faturamento Total', 'Comissões Base', 'Comissões Finais'],
            [str(total_vendedores), f"R$ {total_faturamento:,.2f}", f"R$ {total_comissao_base:,.2f}", f"R$ {total_comissao_final:,.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch, 2*inch, 2*inch])
        summary_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ])
        summary_table.setStyle(summary_style)
        story.append(summary_table)
        
        # Rodapé
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=1,  # Center
            textColor=colors.grey
        )
        story.append(Paragraph(f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", footer_style))
        story.append(Paragraph("Sistema de Comissões - Versão 1.0", footer_style))
        
        # Gerar PDF
        doc.build(story)
        pdf_buffer.seek(0)
        
        # Nome do arquivo
        nome_arquivo = f"Relatorio_Comissoes_{mes:02d}_{ano}.pdf"
        
        # Retornar PDF para download
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=nome_arquivo,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao gerar PDF: {str(e)}'}), 500

@app.route('/api/ajuste-faturamento/<int:rca>/<int:ano>/<int:mes>', methods=['GET'])
def get_ajuste_faturamento(rca, ano, mes):
    """API para buscar ajustes de faturamento de um vendedor em um período específico"""
    try:
        ajuste = AjusteFaturamento.query.filter_by(
            vendedor_rca=rca, 
            ano=ano, 
            mes=mes
        ).first()
        
        if ajuste:
            return jsonify({
                'success': True,
                'ajuste': {
                    'id': ajuste.id,
                    'vendedor_rca': ajuste.vendedor_rca,
                    'mes': ajuste.mes,
                    'ano': ajuste.ano,
                    'valor_ajuste': ajuste.valor_ajuste,
                    'taxa_comissao_ajuste': ajuste.taxa_comissao_ajuste,
                    'motivo': ajuste.motivo,
                    'data_criacao': ajuste.data_criacao.strftime('%d/%m/%Y %H:%M'),
                    'data_atualizacao': ajuste.data_atualizacao.strftime('%d/%m/%Y %H:%M')
                }
            })
        else:
            return jsonify({
                'success': True,
                'ajuste': {
                    'vendedor_rca': rca,
                    'mes': mes,
                    'ano': ano,
                    'valor_ajuste': 0.0,
                    'taxa_comissao_ajuste': 0.0,
                    'motivo': None
                }
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao buscar ajuste: {str(e)}'}), 500

@app.route('/api/ajuste-faturamento', methods=['POST'])
def create_or_update_ajuste_faturamento():
    """API para criar ou atualizar ajustes de faturamento"""
    try:
        data = request.get_json()
        
        # Busca ajuste existente
        ajuste = AjusteFaturamento.query.filter_by(
            vendedor_rca=data['vendedor_rca'],
            ano=data['ano'],
            mes=data['mes']
        ).first()
        
        if ajuste:
            # Atualiza ajuste existente
            ajuste.valor_ajuste = float(data['valor_ajuste'])
            ajuste.taxa_comissao_ajuste = float(data['taxa_comissao_ajuste'])
            ajuste.motivo = data.get('motivo', '')
            ajuste.data_atualizacao = datetime.utcnow()
            message = 'Ajuste de faturamento atualizado com sucesso'
        else:
            # Cria novo ajuste
            ajuste = AjusteFaturamento(
                vendedor_rca=data['vendedor_rca'],
                ano=data['ano'],
                mes=data['mes'],
                valor_ajuste=float(data['valor_ajuste']),
                taxa_comissao_ajuste=float(data['taxa_comissao_ajuste']),
                motivo=data.get('motivo', '')
            )
            db.session.add(ajuste)
            message = 'Ajuste de faturamento criado com sucesso'
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': message,
            'ajuste_id': ajuste.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao salvar ajuste: {str(e)}'}), 500
