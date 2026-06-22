from broker import MessageBroker
import json
import time
from datetime import datetime

class ConsumidorNotificacoes:
    def __init__(self):
        self.broker = MessageBroker(host='localhost', port=5672)
        self.broker.declare_exchange_and_queues()
        self.retry_count = 0
        self.max_retries = 3

    def processar_evento(self, ch, method, properties, body):
        try:
            mensagem = json.loads(body)
            tempo_inicio = time.time()

            print(f"\n{'─'*60}")
            print(f"[CONSUMIDOR: NOTIFICAÇÕES]")
            print(f"{'─'*60}")
            print(f"→ Evento recebido: {method.routing_key}")
            print(f"→ Queue: notificacoes")
            print(f"→ Timestamp: {datetime.now().isoformat()}")
            print(f"\nDados da mensagem:")
            print(json.dumps(mensagem, ensure_ascii=False, indent=2))

            print(f"\n→ Processando notificação...")
            time.sleep(1)

            if mensagem.get('aluno_id'):
                email = mensagem.get('email')
                nome = mensagem.get('nome')
                print(f"  ✓ Email enviado para: {email}")
                print(f"  ✓ Assunto: Bem-vindo {nome}")
                print(f"  ✓ Conteúdo: Sua conta foi criada com sucesso!")

            tempo_fim = time.time()
            tempo_processamento = tempo_fim - tempo_inicio

            print(f"\n✓ Notificação processada com sucesso")
            print(f"  Tempo de processamento: {tempo_processamento:.2f}s")
            print(f"  Delivery tag: {method.delivery_tag}")

            ch.basic_ack(delivery_tag=method.delivery_tag)
            self.retry_count = 0

        except json.JSONDecodeError:
            print(f"✗ Erro ao decodificar JSON")
            self._handle_retry(ch, method)
        except Exception as e:
            print(f"✗ Erro ao processar notificação: {e}")
            self._handle_retry(ch, method)

    def _handle_retry(self, ch, method):
        self.retry_count += 1
        if self.retry_count < self.max_retries:
            print(f"→ Tentando novamente... ({self.retry_count}/{self.max_retries})")
            time.sleep(2)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        else:
            print(f"✗ Máximo de tentativas atingido. Descartando mensagem.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            self.retry_count = 0

    def iniciar(self):
        print("\n" + "="*60)
        print("CONSUMIDOR DE NOTIFICAÇÕES")
        print("="*60)
        print("→ Fila: notificacoes")
        print("→ Padrão de rota: evento.aluno.criado")
        print("→ Responsabilidade: Enviar notificações por email")
        print("→ Status: Aguardando mensagens...")
        print("="*60 + "\n")

        self.broker.consume_messages(
            queue_name='notificacoes',
            callback=self.processar_evento,
            auto_ack=False
        )

if __name__ == '__main__':
    consumidor = ConsumidorNotificacoes()
    consumidor.iniciar()
