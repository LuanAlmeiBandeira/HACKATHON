# OrganizadorDeArquivos - Hackathon

## Descrição
Sistema web para gerenciamento de documentos pessoais em PDF,
organizados por CPF, com CRUD completo.

## Tecnologias
- Python (Flask)
- HTML, CSS, JavaScript
- SQLite (compatível com PostgreSQL)
- Git e GitHub

## Funcionalidades
- Cadastro de usuário por CPF
- Upload de documentos obrigatórios
- Renomeação automática
- Busca por CPF
- Edição e exclusão com backup
- API RESTful
- Testes automatizados

## Modelagem do Banco
[DER explicado]

## Testes
Testes automatizados com pytest cobrindo CRUD completo.
python3 -m pytest

## Segurança
Validação de dados, proteção contra duplicidade e backup automático.

## Acessibilidade
Interface acessível conforme WCAG.

## Como Executar
sudo apt update
sudo apt install python-is-python3
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
