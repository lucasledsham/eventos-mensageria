from broker import MessageBroker
import json
import time
from datetime import datetime

class DemoDisponibilidade:
    """
    Demonstra o comportamento quando consumidores estão indisponíveis.
    As mensagens permanecem na fila até que o consumidor volte a estar disponível.
    """

    def __init__(self):
        self.broker = MessageBroker(host='localhost', port=5672)
        self.broker.declare_exchange_and_queues()
        self.simular_indisponibilidade = False

    def processar_evento(self, ch, method, properties, body):
        try:
            mensagem = json.loads(body)

            print(f"\n{'─'*60}")
            print(f"[CONSUMIDOR: DEMO DISPONIBILIDADE]")
            print(f"{'─'*60}")
            print(f"→ Evento recebido: {method.routing_key}")
            print(f"→ Timestamp: {datetime.now().isoformat()}")

            if self.simular_indisponibilidade:
                print(f"\n⚠ SIMULANDO INDISPONIBILIDADE DO CONSUMIDOR")
                print(f"→ Rejeitando mensagem (requeue=True)")
                print(f"→ Mensagem será reprocessada quando o consumidor voltar")
                print(f"  Delivery Tag: {method.delivery_tag}")

                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                time.sleep(2)

                print(f"\n✓ Consumidor disponível novamente!")
                print(f"→ Reprocessando mensagem...")

                self.simular_indisponibilidade = False
                self.processar_evento(ch, method, properties, body)
            else:
                print(f"\nDados da mensagem:")
                print(json.dumps(mensagem, ensure_ascii=False, indent=2))

                print(f"\n→ Processando evento...")
                time.sleep(0.5)

                print(f"\n✓ Evento processado com sucesso")
                ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"✗ Erro: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def iniciar(self):
        print("\n" + "="*60)
        print("DEMO: COMPORTAMENTO COM CONSUMIDOR INDISPONÍVEL")
        print("="*60)
        print("\nEste consumidor demonstra:")
        print("  1. Comportamento quando consumidor está indisponível")
        print("  2. Persistência de mensagens na fila")
        print("  3. Reprocessamento quando consumidor volta")
        print("  4. Garantia de entrega (durabilidade)")
        print("\n→ Aguardando mensagens...")
        print("→ Ao receber mensagens, simulará indisponibilidade")
        print("→ Depois reprocessará a mensagem")
        print("="*60 + "\n")

        self.simular_indisponibilidade = True

        self.broker.consume_messages(
            queue_name='auditoria',
            callback=self.processar_evento,
            auto_ack=False
        )

if __name__ == '__main__':
    demo = DemoDisponibilidade()
    demo.iniciar()
