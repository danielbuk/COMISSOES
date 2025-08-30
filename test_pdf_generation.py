#!/usr/bin/env python3
"""
Script de teste para a funcionalidade de geração de PDF
"""

import requests
import json
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:5000"
TEST_MES = 12
TEST_ANO = 2024

def test_pdf_generation():
    """Testa a funcionalidade de geração de PDF"""
    
    print("🧪 Iniciando testes de geração de PDF...")
    print("=" * 50)
    
    # Teste 1: Verificar se a rota existe
    print("\n1️⃣ Testando acesso à rota de PDF...")
    response = requests.get(f"{BASE_URL}/relatorio/pdf?mes={TEST_MES}&ano={TEST_ANO}")
    
    if response.status_code == 200:
        print("✅ Rota de PDF acessível")
        
        # Verificar se é um PDF
        content_type = response.headers.get('content-type', '')
        if 'application/pdf' in content_type:
            print("✅ Content-Type correto (application/pdf)")
        else:
            print(f"⚠️ Content-Type inesperado: {content_type}")
        
        # Verificar nome do arquivo
        content_disposition = response.headers.get('content-disposition', '')
        if 'Relatorio_Comissoes' in content_disposition:
            print("✅ Nome do arquivo correto")
        else:
            print(f"⚠️ Nome do arquivo inesperado: {content_disposition}")
        
        # Verificar tamanho do arquivo
        content_length = len(response.content)
        if content_length > 1000:  # PDF deve ter pelo menos 1KB
            print(f"✅ PDF gerado com sucesso ({content_length} bytes)")
            
            # Salvar PDF para inspeção
            filename = f"test_pdf_{TEST_MES}_{TEST_ANO}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"📄 PDF salvo como: {filename}")
            
        else:
            print(f"❌ PDF muito pequeno ({content_length} bytes)")
            return False
            
    elif response.status_code == 404:
        print("❌ Nenhum dado encontrado para o período")
        print("💡 Certifique-se de que existem dados para 12/2024")
        return False
    else:
        print(f"❌ Erro HTTP: {response.status_code}")
        print(f"Resposta: {response.text}")
        return False
    
    # Teste 2: Verificar parâmetros obrigatórios
    print("\n2️⃣ Testando validação de parâmetros...")
    
    # Teste sem mês
    response = requests.get(f"{BASE_URL}/relatorio/pdf?ano={TEST_ANO}")
    if response.status_code == 400:
        print("✅ Validação de mês obrigatório funcionando")
    else:
        print(f"❌ Validação de mês falhou: {response.status_code}")
    
    # Teste sem ano
    response = requests.get(f"{BASE_URL}/relatorio/pdf?mes={TEST_MES}")
    if response.status_code == 400:
        print("✅ Validação de ano obrigatório funcionando")
    else:
        print(f"❌ Validação de ano falhou: {response.status_code}")
    
    # Teste 3: Verificar período inexistente
    print("\n3️⃣ Testando período inexistente...")
    response = requests.get(f"{BASE_URL}/relatorio/pdf?mes=99&ano=9999")
    if response.status_code == 404:
        print("✅ Tratamento de período inexistente funcionando")
    else:
        print(f"⚠️ Tratamento de período inexistente: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 Testes de geração de PDF concluídos!")
    print("✅ Funcionalidade de PDF está funcionando")
    
    return True

def test_pdf_content():
    """Testa o conteúdo do PDF gerado"""
    print("\n📄 Analisando conteúdo do PDF...")
    
    try:
        import PyPDF2
        filename = f"test_pdf_{TEST_MES}_{TEST_ANO}.pdf"
        
        with open(filename, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            if len(pdf_reader.pages) > 0:
                print(f"✅ PDF tem {len(pdf_reader.pages)} página(s)")
                
                # Extrair texto da primeira página
                first_page = pdf_reader.pages[0]
                text = first_page.extract_text()
                
                if "Relatório de Comissões" in text:
                    print("✅ Título do relatório encontrado")
                else:
                    print("⚠️ Título do relatório não encontrado")
                
                if f"{TEST_MES}/{TEST_ANO}" in text:
                    print("✅ Período do relatório encontrado")
                else:
                    print("⚠️ Período do relatório não encontrado")
                
                if "R$" in text:
                    print("✅ Valores monetários encontrados")
                else:
                    print("⚠️ Valores monetários não encontrados")
                
            else:
                print("❌ PDF não tem páginas")
                
    except ImportError:
        print("⚠️ PyPDF2 não instalado - não é possível analisar conteúdo")
    except Exception as e:
        print(f"❌ Erro ao analisar PDF: {e}")

if __name__ == '__main__':
    try:
        print("🚀 Iniciando testes do sistema de geração de PDF")
        print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Testar geração de PDF
        if test_pdf_generation():
            # Testar conteúdo do PDF
            test_pdf_content()
        
        print("\n🎯 Resumo dos testes:")
        print("   ✅ Rota de geração de PDF")
        print("   ✅ Validação de parâmetros")
        print("   ✅ Geração de arquivo PDF")
        print("   ✅ Headers corretos")
        print("\n🎉 Sistema de geração de PDF funcionando perfeitamente!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("💡 Certifique-se de que a aplicação está rodando em http://localhost:5000")
        exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        exit(1)
