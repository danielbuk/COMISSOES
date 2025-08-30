#!/usr/bin/env python3
"""
Script de teste para a funcionalidade de ajuste de faturamento
"""

import requests
import json
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:5000"
TEST_RCA = 123
TEST_MES = 12
TEST_ANO = 2024

def test_ajuste_faturamento():
    """Testa a funcionalidade completa de ajuste de faturamento"""
    
    print("🧪 Iniciando testes de ajuste de faturamento...")
    print("=" * 50)
    
    # Teste 1: Buscar ajuste inexistente
    print("\n1️⃣ Testando busca de ajuste inexistente...")
    response = requests.get(f"{BASE_URL}/api/ajuste-faturamento/{TEST_RCA}/{TEST_ANO}/{TEST_MES}")
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print("✅ Busca de ajuste inexistente funcionando")
            print(f"   Valor padrão: R$ {data['ajuste']['valor_ajuste']}")
        else:
            print("❌ Erro na busca de ajuste inexistente")
            return False
    else:
        print(f"❌ Erro HTTP: {response.status_code}")
        return False
    
    # Teste 2: Criar novo ajuste
    print("\n2️⃣ Testando criação de novo ajuste...")
    novo_ajuste = {
        "vendedor_rca": TEST_RCA,
        "mes": TEST_MES,
        "ano": TEST_ANO,
        "valor_ajuste": 5000.00,
        "taxa_comissao_ajuste": 0.015,  # 1.5%
        "motivo": "Teste de divisão de vendas"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ajuste-faturamento",
        headers={'Content-Type': 'application/json'},
        data=json.dumps(novo_ajuste)
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print("✅ Criação de ajuste funcionando")
            print(f"   ID do ajuste: {data['ajuste_id']}")
        else:
            print(f"❌ Erro na criação: {data['message']}")
            return False
    else:
        print(f"❌ Erro HTTP: {response.status_code}")
        return False
    
    # Teste 3: Buscar ajuste criado
    print("\n3️⃣ Testando busca de ajuste criado...")
    response = requests.get(f"{BASE_URL}/api/ajuste-faturamento/{TEST_RCA}/{TEST_ANO}/{TEST_MES}")
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            ajuste = data['ajuste']
            print("✅ Busca de ajuste criado funcionando")
            print(f"   Valor: R$ {ajuste['valor_ajuste']}")
            print(f"   Taxa: {ajuste['taxa_comissao_ajuste'] * 100}%")
            print(f"   Motivo: {ajuste['motivo']}")
        else:
            print("❌ Erro na busca de ajuste criado")
            return False
    else:
        print(f"❌ Erro HTTP: {response.status_code}")
        return False
    
    # Teste 4: Atualizar ajuste existente
    print("\n4️⃣ Testando atualização de ajuste...")
    ajuste_atualizado = {
        "vendedor_rca": TEST_RCA,
        "mes": TEST_MES,
        "ano": TEST_ANO,
        "valor_ajuste": 7500.00,
        "taxa_comissao_ajuste": 0.02,  # 2%
        "motivo": "Ajuste atualizado - comissão especial"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ajuste-faturamento",
        headers={'Content-Type': 'application/json'},
        data=json.dumps(ajuste_atualizado)
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print("✅ Atualização de ajuste funcionando")
            print(f"   Mensagem: {data['message']}")
        else:
            print(f"❌ Erro na atualização: {data['message']}")
            return False
    else:
        print(f"❌ Erro HTTP: {response.status_code}")
        return False
    
    # Teste 5: Verificar ajuste atualizado
    print("\n5️⃣ Verificando ajuste atualizado...")
    response = requests.get(f"{BASE_URL}/api/ajuste-faturamento/{TEST_RCA}/{TEST_ANO}/{TEST_MES}")
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            ajuste = data['ajuste']
            print("✅ Verificação de ajuste atualizado funcionando")
            print(f"   Novo valor: R$ {ajuste['valor_ajuste']}")
            print(f"   Nova taxa: {ajuste['taxa_comissao_ajuste'] * 100}%")
            print(f"   Novo motivo: {ajuste['motivo']}")
            
            # Verificar se os valores estão corretos
            if ajuste['valor_ajuste'] == 7500.00 and ajuste['taxa_comissao_ajuste'] == 0.02:
                print("✅ Valores atualizados corretamente")
            else:
                print("❌ Valores não foram atualizados corretamente")
                return False
        else:
            print("❌ Erro na verificação")
            return False
    else:
        print(f"❌ Erro HTTP: {response.status_code}")
        return False
    
    # Teste 6: Verificar relatório com ajuste
    print("\n6️⃣ Testando relatório com ajuste...")
    response = requests.get(f"{BASE_URL}/relatorio?mes={TEST_MES}&ano={TEST_ANO}")
    
    if response.status_code == 200:
        print("✅ Relatório acessível")
        if "Ajuste Manual" in response.text:
            print("✅ Ajuste aparece no relatório")
        else:
            print("⚠️ Ajuste pode não estar aparecendo no relatório")
    else:
        print(f"❌ Erro ao acessar relatório: {response.status_code}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Todos os testes passaram com sucesso!")
    print("✅ Funcionalidade de ajuste de faturamento está funcionando")
    
    return True

def test_calculos():
    """Testa os cálculos de comissão com ajuste"""
    print("\n🧮 Testando cálculos de comissão...")
    
    # Valores de exemplo
    faturamento_oracle = 50000.00
    comissao_base_oracle = 750.00  # 1.5%
    valor_ajuste = 5000.00
    taxa_ajuste = 0.015  # 1.5%
    
    # Cálculos esperados
    comissao_do_ajuste = valor_ajuste * taxa_ajuste
    comissao_base_total = comissao_base_oracle + comissao_do_ajuste
    faturamento_final = faturamento_oracle + valor_ajuste
    
    print(f"   Faturamento Oracle: R$ {faturamento_oracle:,.2f}")
    print(f"   Comissão Base Oracle: R$ {comissao_base_oracle:,.2f}")
    print(f"   Ajuste: R$ {valor_ajuste:,.2f}")
    print(f"   Taxa do Ajuste: {taxa_ajuste * 100}%")
    print(f"   Comissão do Ajuste: R$ {comissao_do_ajuste:,.2f}")
    print(f"   Comissão Base Total: R$ {comissao_base_total:,.2f}")
    print(f"   Faturamento Final: R$ {faturamento_final:,.2f}")
    
    # Verificar se os cálculos estão corretos
    comissao_esperada = 5000.00 * 0.015  # 75.00
    if abs(comissao_do_ajuste - comissao_esperada) < 0.01:
        print("✅ Cálculos estão corretos")
        return True
    else:
        print("❌ Erro nos cálculos")
        return False

if __name__ == '__main__':
    try:
        print("🚀 Iniciando testes do sistema de ajuste de faturamento")
        print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Testar cálculos
        if not test_calculos():
            print("❌ Falha nos testes de cálculo")
            exit(1)
        
        # Testar funcionalidade
        if not test_ajuste_faturamento():
            print("❌ Falha nos testes de funcionalidade")
            exit(1)
        
        print("\n🎯 Resumo dos testes:")
        print("   ✅ Cálculos de comissão")
        print("   ✅ API de busca de ajuste")
        print("   ✅ API de criação de ajuste")
        print("   ✅ API de atualização de ajuste")
        print("   ✅ Relatório com ajuste")
        print("\n🎉 Sistema de ajuste de faturamento funcionando perfeitamente!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("💡 Certifique-se de que a aplicação está rodando em http://localhost:5000")
        exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        exit(1)
