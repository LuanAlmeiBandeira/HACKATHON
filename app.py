
# IMPORTAÇÕES
from flask import Flask, request, jsonify
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import os
import shutil
from datetime import datetime


# CONFIGURAÇÃO
app = Flask(__name__, static_folder='frontend', static_url_path='')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'storage', 'arquivos')
BACKUP_DIR = os.path.join(BASE_DIR, 'storage', 'backup')

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)


# REFERENCIAR O FRONTEND
@app.route('/')
def index():
    return render_template('index.html') 

# MODELOS (BANCO)
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(11), unique=True, nullable=False)

class Documento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    nome_arquivo = db.Column(db.String(200), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# TIPOS PERMITIDOS
TIPOS = ['cpf', 'rg', 'historico', 'certidao', 'residencia']


# API — USUÁRIOS
@app.route('/api/usuarios', methods=['POST'])
def criar_usuario():
    data = request.json
    cpf = data.get('cpf')

    if not cpf:
        return jsonify({'erro': 'CPF obrigatório'}), 400

    if Usuario.query.filter_by(cpf=cpf).first():
        return jsonify({'erro': 'Usuário já existe'}), 409

    usuario = Usuario(cpf=cpf)
    db.session.add(usuario)
    db.session.commit()

    return jsonify({'mensagem': 'Usuário criado', 'cpf': cpf}), 201


@app.route('/api/usuarios/<cpf>', methods=['GET'])
def buscar_usuario(cpf):
    usuario = Usuario.query.filter_by(cpf=cpf).first()

    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado'}), 404

    return jsonify({'cpf': usuario.cpf})


# API — DOCUMENTOS (CRUD)
@app.route('/api/documentos', methods=['POST'])
def upload_documento():
    cpf = request.form.get('cpf')
    tipo = request.form.get('tipo')
    arquivo = request.files.get('file')

    if not cpf or not tipo or not arquivo:
        return jsonify({'erro': 'Dados incompletos'}), 400

    if tipo not in TIPOS:
        return jsonify({'erro': 'Tipo inválido'}), 400

    if not arquivo.filename.lower().endswith('.pdf'):
        return jsonify({'erro': 'Apenas PDF'}), 400

    usuario = Usuario.query.filter_by(cpf=cpf).first()
    if not usuario:
        usuario = Usuario(cpf=cpf)
        db.session.add(usuario)
        db.session.commit()

    nome = f"{tipo}_{cpf}.pdf"
    caminho = os.path.join(UPLOAD_DIR, nome)

    if os.path.exists(caminho):
        shutil.copy2(caminho, os.path.join(BACKUP_DIR, nome))

    arquivo.save(caminho)

    Documento.query.filter_by(usuario_id=usuario.id, tipo=tipo).delete()

    doc = Documento(
        tipo=tipo,
        nome_arquivo=nome,
        usuario_id=usuario.id
    )
    db.session.add(doc)
    db.session.commit()

    return jsonify({'mensagem': 'Documento enviado', 'arquivo': nome}), 201


@app.route('/api/documentos/<cpf>', methods=['GET'])
def listar_documentos(cpf):
    usuario = Usuario.query.filter_by(cpf=cpf).first()

    if not usuario:
        return jsonify({'documentos': []})

    docs = Documento.query.filter_by(usuario_id=usuario.id).all()

    return jsonify({
        'cpf': cpf,
        'documentos': [
            {'tipo': d.tipo, 'arquivo': d.nome_arquivo}
            for d in docs
        ]
    })


@app.route('/api/documentos/<arquivo>', methods=['PUT'])
def atualizar_documento(arquivo):
    novo = request.files.get('file')
    tipo = request.form.get('tipo')

    caminho_antigo = os.path.join(UPLOAD_DIR, arquivo)

    if not os.path.exists(caminho_antigo):
        return jsonify({'erro': 'Arquivo não encontrado'}), 404

    if not novo or not novo.filename.endswith('.pdf'):
        return jsonify({'erro': 'PDF inválido'}), 400

    if tipo not in TIPOS:
        return jsonify({'erro': 'Tipo inválido'}), 400

    cpf = arquivo.split('_')[1].replace('.pdf', '')
    novo_nome = f"{tipo}_{cpf}.pdf"
    novo_caminho = os.path.join(UPLOAD_DIR, novo_nome)

    # Backup
    shutil.copy2(caminho_antigo, os.path.join(BACKUP_DIR, arquivo))
    os.remove(caminho_antigo)

    # Salvar novo
    novo.save(novo_caminho)

    doc = Documento.query.filter_by(nome_arquivo=arquivo).first()
    doc.nome_arquivo = novo_nome
    doc.tipo = tipo
    db.session.commit()

    return jsonify({'mensagem': 'Documento atualizado com sucesso'})


@app.route('/api/documentos/<arquivo>', methods=['DELETE'])
def deletar_documento(arquivo):
    caminho = os.path.join(UPLOAD_DIR, arquivo)

    if not os.path.exists(caminho):
        return jsonify({'erro': 'Arquivo não encontrado'}), 404

    shutil.copy2(caminho, os.path.join(BACKUP_DIR, arquivo))
    os.remove(caminho)

    Documento.query.filter_by(nome_arquivo=arquivo).delete()
    db.session.commit()

    return jsonify({'mensagem': 'Documento excluído'})


# INIT
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=False)

