# Robô de Prospecção

Scripts em Python que automatizam a busca de contatos de empresas para prospecção comercial B2B, substituindo pesquisas manuais feitas uma a uma.

## Scripts

### `consulta_cnpj_completa.py`: enriquecimento por CNPJ
1. Lê uma planilha (`entrada_dados.xlsx`) com CNPJs.
2. Extrai, para cada empresa, o quadro de sócios e o estado em uma consulta pública de CNPJ.
3. Busca o telefone do sócio principal na base de contatos (Deskdata).
4. Salva o resultado em `saida_dados.xlsx`.

### `BUSCASIMPLIFICADA.py`: busca de celulares por nome e estado
1. Lê uma planilha (`entrada_nomes.xlsx`) com as colunas `Nome` e `Estado` (sigla da UF).
2. Faz login automático, aplica os filtros de nome e endereço e extrai apenas os números de celular.
3. Trata erros e tempos de espera (`WebDriverWait`) para rodar listas longas sem intervenção.
4. Salva o resultado em `saida_telefones_por_nome.xlsx`.

## Tecnologias
Python · Selenium · pandas · openpyxl · python-dotenv

## Como rodar
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install selenium pandas openpyxl python-dotenv webdriver-manager
```

Copie `.env.example` para `.env` e preencha suas credenciais:
```
EMAIL_DESKDATA=seu_email@exemplo.com
SENHA_DESKDATA=sua_senha
```

Depois:
```bash
python BUSCASIMPLIFICADA.py
```

> O `.env` e as planilhas com dados de contatos não são versionados (ver `.gitignore`).

## Autor
Davi Spindola · [LinkedIn](https://www.linkedin.com/in/davi-spindola-13ab01359/)
