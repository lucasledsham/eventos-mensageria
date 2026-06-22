from broker import MessageBroker
import json
import time
from datetime import datetime

class ConsumidorAuditoria:
    def __init__(self):
        self.broker = MessageBroker(host='localhost', port=5672)
        self.broker.declare_exchange_and_queues()
        self.eventos_processados = []

    def processar_evento(self, ch, method, properties, body):
        try:
            mensagem = json.loads(body)
            tempo_inicio = time.time()

            print(f"\n{'─'*60}")
            print(f"[CONSUMIDOR: AUDITORIA]")
            print(f"{'─'*60}")
            print(f"→ Evento recebido: {method.routing_key}")
            print(f"→ Queue: auditoria")
            print(f"→ Timestamp: {datetime.now().isoformat()}")
            print(f"\nDados da mensagem:")
            print(json.dumps(mensagem, ensure_ascii=False, indent=2))

            print(f"\n→ Registrando em log de auditoria...")
            time.sleep(0.5)

            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'evento': method.routing_key,
                'id_entidade': mensagem.get('aluno_id'),
                'usuario': 'SISTEMA',
                'operacao': 'CREATE' if 'criado' in method.routing_key else 'UPDATE'
            }

            self.eventos_processados.append(log_entry)
            print(f"  ✓ Log armazenado")
            print(f"  ✓ ID da auditoria: {len(self.eventos_processados)}")
            print(f"  ✓ Operação: {log_entry['operacao']}")

            tempo_fim = time.time()
            tempo_processamento = tempo_fim - tempo_inicio

            print(f"\n✓ Evento de auditoria registrado com sucesso")
            print(f"  Tempo de processamento: {tempo_processamento:.2f}s")
            print(f"  Total de eventos auditados: {len(self.eventos_processados)}")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"✗ Erro ao processar auditoria: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def iniciar(self):
        print("\n" + "="*60)
        print("CONSUMIDOR DE AUDITORIA")
        print("="*60)
        print("→ Fila: auditoria")
        print("→ Padrão de rota: evento.*")
        print("→ Responsabilidade: Registrar todos os eventos em log de auditoria")
        print("→ Status: Aguardando mensagens...")
        print("="*60 + "\n")

        self.broker.consume_messages(
            queue_name='auditoria',
            callback=self.processar_evento,
            auto_ack=False
        )

if __name__ == '__main__':
    consumidor = ConsumidorAuditoria()
    consumidor.iniciar()
