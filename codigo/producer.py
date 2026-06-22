from flask import Flask, request, jsonify
from broker import MessageBroker
from datetime import datetime
import uuid

app = Flask(__name__)
broker = MessageBroker(host='localhost', port=5672)
broker.declare_exchange_and_queues()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'servico': 'Produtor de Eventos Acadêmicos'})

@app.route('/alunos', methods=['POST'])
def criar_aluno():
    try:
        data = request.get_json()

        if not data or 'nome' not in data or 'email' not in data:
            return jsonify({'erro': 'Nome e email são obrigatórios'}), 400

        aluno_id = str(uuid.uuid4())
        aluno_data = {
            'aluno_id': aluno_id,
            'nome': data['nome'],
            'email': data['email'],
            'matricula': data.get('matricula'),
            'curso': data.get('curso', 'Engenharia de Software')
        }

        print(f"\n{'='*60}")
        print(f"[AÇÃO PRINCIPAL] Cadastrando novo aluno")
        print(f"{'='*60}")

        broker.publish_message('evento.aluno.criado', aluno_data)

        return jsonify({
            'mensagem': 'Aluno cadastrado com sucesso',
            'aluno_id': aluno_id,
            'timestamp': datetime.now().isoformat()
        }), 201

    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/matriculas', methods=['POST'])
def criar_matricula():
    try:
        data = request.get_json()

        if not data or 'aluno_id' not in data or 'disciplina' not in data:
            return jsonify({'erro': 'aluno_id e disciplina são obrigatórios'}), 400

        matricula_data = {
            'aluno_id': data['aluno_id'],
            'disciplina': data['disciplina'],
            'semestre': data.get('semestre', '2024.1'),
            'data_matricula': datetime.now().isoformat()
        }

        print(f"\n{'='*60}")
        print(f"[AÇÃO PRINCIPAL] Registrando nova matrícula")
        print(f"{'='*60}")

        broker.publish_message('evento.aluno.matriculado', matricula_data)

        return jsonify({
            'mensagem': 'Matrícula registrada com sucesso',
            'timestamp': datetime.now().isoformat()
        }), 201

    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/eventos', methods=['GET'])
def listar_eventos():
    return jsonify({
        'eventos_disponiveis': [
            {
                'tipo': 'evento.aluno.criado',
                'descricao': 'Disparado quando um novo aluno é cadastrado',
                'consumidores': ['notificacoes', 'auditoria', 'relatorios']
            },
            {
                'tipo': 'evento.aluno.matriculado',
                'descricao': 'Disparado quando um aluno realiza matrícula',
                'consumidores': ['auditoria', 'relatorios']
            }
        ]
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("PRODUTOR DE EVENTOS - PLATAFORMA ACADÊMICA")
    print("="*60)
    print("\nEndpoints disponíveis:")
    print("  POST /alunos - Cadastrar novo aluno")
    print("  POST /matriculas - Registrar matrícula")
    print("  GET /eventos - Listar eventos disponíveis")
    print("  GET /health - Verificar saúde da API")
    print("\nAPI iniciada em http://localhost:5000")
    print("="*60 + "\n")

    app.run(debug=True, port=5000)
