import os
import shutil
from flask import Flask, request, jsonify, send_from_directory # type: ignore

app = Flask(__name__, static_folder='frontend', static_url_path='')

# CONFIGURAÇÕES DE DIRETÓRIO
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ARQUIVOS_DIR = os.path.join(BASE_DIR, 'storage', 'arquivos')
BACKUP_DIR = os.path.join(BASE_DIR, 'storage', 'backup')

os.makedirs(ARQUIVOS_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

@app.route('/')
def frontend():
    return send_from_directory('frontend', 'index.html')

# ENDPOINT: UPLOAD DE PDF
@app.route('/upload', methods=['POST'])
def upload_pdf():
    cpf = request.form.get('cpf')
    arquivo = request.files.get('file')

    if not cpf or not arquivo:
        return jsonify({'erro': 'CPF e arquivo são obrigatórios'}), 400

    if not arquivo.filename.lower().endswith('.pdf'):
        return jsonify({'erro': 'Somente arquivos PDF são permitidos'}), 400

    nome_final = f"{cpf}_{arquivo.filename}"
    caminho = os.path.join(ARQUIVOS_DIR, nome_final)

    arquivo.save(caminho)

    return jsonify({
        'mensagem': 'Arquivo salvo com sucesso',
        'arquivo': nome_final
    }), 201


# ENDPOINT: BUSCAR PDF POR CPF
@app.route('/buscar/<cpf>', methods=['GET'])
def buscar_por_cpf(cpf):
    documentos = [
        f for f in os.listdir(ARQUIVOS_DIR)
        if f.lower().endswith('.pdf') and cpf in f
    ]

    return jsonify({
        'cpf': cpf,
        'quantidade': len(documentos),
        'documentos': documentos
    }), 200


# ENDPOINT: DOWNLOAD / VISUALIZAR
@app.route('/download/<nome_arquivo>', methods=['GET'])
def download_pdf(nome_arquivo):
    caminho = os.path.join(ARQUIVOS_DIR, nome_arquivo)

    if not os.path.exists(caminho):
        return jsonify({'erro': 'Arquivo não encontrado'}), 404

    return send_from_directory(ARQUIVOS_DIR, nome_arquivo)


# ENDPOINT: EDITAR (SUBSTITUIR)
@app.route('/editar/<nome_arquivo>', methods=['PUT'])
def editar_pdf(nome_arquivo):
    novo_arquivo = request.files.get('file')
    caminho_original = os.path.join(ARQUIVOS_DIR, nome_arquivo)

    if not os.path.exists(caminho_original):
        return jsonify({'erro': 'Arquivo não encontrado'}), 404

    if not novo_arquivo or not novo_arquivo.filename.lower().endswith('.pdf'):
        return jsonify({'erro': 'Novo arquivo PDF é obrigatório'}), 400

    # Backup antes de editar
    shutil.copy2(
        caminho_original,
        os.path.join(BACKUP_DIR, nome_arquivo)
    )

    # Substituição
    novo_arquivo.save(caminho_original)

    return jsonify({'mensagem': 'Arquivo atualizado com sucesso'}), 200

# ENDPOINT: DELETAR COM BACKUP

@app.route('/deletar/<nome_arquivo>', methods=['DELETE'])
def deletar_pdf(nome_arquivo):
    caminho = os.path.join(ARQUIVOS_DIR, nome_arquivo)

    if not os.path.exists(caminho):
        return jsonify({'erro': 'Arquivo não encontrado'}), 404

    # Backup antes de deletar
    shutil.copy2(
        caminho,
        os.path.join(BACKUP_DIR, nome_arquivo)
    )

    os.remove(caminho)

    return jsonify({'mensagem': 'Arquivo deletado com backup realizado'}), 200

# INICIALIZAÇÃO DO SERVIDOR
if __name__ == '__main__':
    app.run(debug=True)
