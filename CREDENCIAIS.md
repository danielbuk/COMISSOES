# Configuração de Credenciais

## Arquivo .env

Crie um arquivo `.env` na raiz do projeto com as seguintes informações:

```ini
# Credenciais do Banco de Dados Oracle (Fonte de Dados)
ORACLE_USER="dicon"
ORACLE_PASSWORD="wdicon01"
ORACLE_DSN="10.0.0.10:1521/WINT"

# URI do Banco de Dados Local (Regras de Negócio)
DATABASE_URL="sqlite:///business_rules.db"

# Chave secreta para sessões Flask (opcional)
SECRET_KEY="uma-chave-secreta-bem-dificil"
```

## Importante

- **NUNCA** commite o arquivo `.env` no repositório
- O arquivo `.env` já está incluído no `.gitignore`
- Use credenciais reais apenas no arquivo `.env`
- Para desenvolvimento, você pode usar as credenciais padrão do `config.py`

## Teste de Conexão

Após configurar as credenciais, execute:

```bash
python test_setup.py
```

Isso verificará se todas as dependências e configurações estão corretas.
