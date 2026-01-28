import sys
import io
import os
import pytest

# Permite importar app.py da raiz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, Usuario, Documento

# ================= CONFIGURAÇÃO =================

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

# ================= TESTE: CRIAR USUÁRIO =================

def test_criar_usuario(client):
    resposta = client.post('/api/usuarios', json={
        'cpf': '12345678900'
    })

    assert resposta.status_code in [201, 409]

# ================= TESTE: USUÁRIO DUPLICADO =================

def test_usuario_duplicado(client):
    client.post('/api/usuarios', json={'cpf': '12345678900'})

    resposta = client.post('/api/usuarios', json={'cpf': '12345678900'})

    assert resposta.status_code == 409

# ================= TESTE: UPLOAD =================

def test_upload_documento(client):
    arquivo_fake = (io.BytesIO(b"PDF fake"), 'teste.pdf')

    resposta = client.post('/api/documentos',
        data={
            'cpf': '12345678900',
            'tipo': 'rg',
            'file': arquivo_fake
        },
        content_type='multipart/form-data'
    )

    assert resposta.status_code == 201
    assert 'Documento enviado' in resposta.get_data(as_text=True)

# ================= TESTE: LISTAR =================

def test_listar_documentos(client):
    arquivo_fake = (io.BytesIO(b"PDF fake"), 'teste.pdf')

    client.post('/api/documentos',
        data={
            'cpf': '12345678900',
            'tipo': 'cpf',
            'file': arquivo_fake
        },
        content_type='multipart/form-data'
    )

    resposta = client.get('/api/documentos/12345678900')

    assert resposta.status_code == 200
    assert 'cpf_12345678900.pdf' in resposta.get_data(as_text=True)

# ================= TESTE: EDITAR =================

def test_editar_documento(client):
    arquivo = (io.BytesIO(b"PDF fake"), 'a.pdf')

    client.post('/api/documentos',
        data={
            'cpf': '12345678900',
            'tipo': 'rg',
            'file': arquivo
        },
        content_type='multipart/form-data'
    )

    novo = (io.BytesIO(b"PDF novo"), 'b.pdf')

    resposta = client.put('/api/documentos/rg_12345678900.pdf',
        data={
            'tipo': 'cpf',
            'file': novo
        },
        content_type='multipart/form-data'
    )

    assert resposta.status_code == 200

# ================= TESTE: DELETAR =================

def test_deletar_documento(client):
    arquivo = (io.BytesIO(b"PDF fake"), 'a.pdf')

    client.post('/api/documentos',
        data={
            'cpf': '12345678900',
            'tipo': 'rg',
            'file': arquivo
        },
        content_type='multipart/form-data'
    )

    resposta = client.delete('/api/documentos/rg_12345678900.pdf')

    assert resposta.status_code == 200
