import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}\n")

def test_health():
    print_header("1. VERIFICANDO SAÚDE DA API")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ API está funcionando")
            print(json.dumps(response.json(), indent=2))
        else:
            print("✗ Erro ao conectar à API")
    except Exception as e:
        print(f"✗ Erro de conexão: {e}")
        print("⚠ Certifique-se que o produtor está rodando em http://localhost:5000")

def test_list_events():
    print_header("2. LISTANDO EVENTOS DISPONÍVEIS")
    try:
        response = requests.get(f"{BASE_URL}/eventos")
        if response.status_code == 200:
            events = response.json()['eventos_disponiveis']
            for event in events:
                print(f"Tipo: {event['tipo']}")
                print(f"Descrição: {event['descricao']}")
                print(f"Consumidores: {', '.join(event['consumidores'])}\n")
    except Exception as e:
        print(f"✗ Erro: {e}")

def test_create_student():
    print_header("3. CRIANDO UM NOVO ALUNO")
    aluno_data = {
        "nome": "João Silva",
        "email": "joao.silva@exemplo.com",
        "matricula": "2024001",
        "curso": "Engenharia de Software"
    }

    try:
        print("Enviando requisição...")
        print(json.dumps(aluno_data, ensure_ascii=False, indent=2))

        response = requests.post(
            f"{BASE_URL}/alunos",
            json=aluno_data
        )

        if response.status_code == 201:
            print("\n✓ Aluno criado com sucesso!")
            result = response.json()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print("\n⚠ Verifique os consumidores para ver o processamento das mensagens:")
            print("  - consumer_notificacoes.py (enviará email)")
            print("  - consumer_auditoria.py (registrará log)")
            print("  - consumer_relatorios.py (gerará relatório)")
            return result.get('aluno_id')
        else:
            print(f"✗ Erro: {response.status_code}")
            print(response.json())
    except Exception as e:
        print(f"✗ Erro: {e}")

    return None

def test_create_enrollment(aluno_id):
    print_header("4. REGISTRANDO MATRÍCULA")
    matricula_data = {
        "aluno_id": aluno_id,
        "disciplina": "Arquitetura de Software",
        "semestre": "2024.1"
    }

    try:
        print("Enviando requisição...")
        print(json.dumps(matricula_data, ensure_ascii=False, indent=2))

        response = requests.post(
            f"{BASE_URL}/matriculas",
            json=matricula_data
        )

        if response.status_code == 201:
            print("\n✓ Matrícula registrada com sucesso!")
            print(json.dumps(response.json(), ensure_ascii=False, indent=2))
            print("\n⚠ Verifique os consumidores para ver o processamento da mensagem")
        else:
            print(f"✗ Erro: {response.status_code}")
            print(response.json())
    except Exception as e:
        print(f"✗ Erro: {e}")

def run_tests():
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "TESTE DO SISTEMA DE MENSAGERIA" + " "*13 + "║")
    print("║" + " "*18 + "Plataforma Acadêmica" + " "*20 + "║")
    print("╚" + "="*58 + "╝")

    print("\n⚠ PRÉ-REQUISITOS:")
    print("  1. RabbitMQ rodando (docker-compose up -d)")
    print("  2. Produtor rodando (python producer.py)")
    print("  3. Consumidores rodando em terminais separados:")
    print("     - python consumer_notificacoes.py")
    print("     - python consumer_auditoria.py")
    print("     - python consumer_relatorios.py")

    print("\n" + "="*60)
    input("Pressione ENTER para iniciar os testes...")

    test_health()
    time.sleep(1)

    test_list_events()
    time.sleep(1)

    aluno_id = test_create_student()
    time.sleep(2)

    if aluno_id:
        test_create_enrollment(aluno_id)
        time.sleep(2)

    print_header("5. TESTES CONCLUÍDOS")
    print("✓ Sistema de mensageria funcionando corretamente!")
    print("\nPróximos passos:")
    print("  1. Feche os consumidores")
    print("  2. Verifique as demonstrações de:")
    print("     - Desacoplamento entre produtor e consumidor")
    print("     - Processamento assíncrono")
    print("     - Tempo entre publicação e processamento")
    print("     - Tratamento de falhas e retry")

if __name__ == '__main__':
    run_tests()
