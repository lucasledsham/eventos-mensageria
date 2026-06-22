from broker import MessageBroker
import json
import time
from datetime import datetime

class ConsumidorRelatorios:
    def __init__(self):
        self.broker = MessageBroker(host='localhost', port=5672)
        self.broker.declare_exchange_and_queues()
        self.relatorios_gerados = 0

    def processar_evento(self, ch, method, properties, body):
        try:
            mensagem = json.loads(body)
            tempo_inicio = time.time()

            print(f"\n{'─'*60}")
            print(f"[CONSUMIDOR: RELATÓRIOS]")
            print(f"{'─'*60}")
            print(f"→ Evento recebido: {method.routing_key}")
            print(f"→ Queue: relatorios")
            print(f"→ Timestamp: {datetime.now().isoformat()}")
            print(f"\nDados da mensagem:")
            print(json.dumps(mensagem, ensure_ascii=False, indent=2))

            print(f"\n→ Gerando relatório...")
            time.sleep(1.5)

            self.relatorios_gerados += 1
            relatorio = {
                'id_relatorio': f"REL-{self.relatorios_gerados:04d}",
                'tipo': 'Estatísticas Acadêmicas',
                'data_geracao': datetime.now().isoformat(),
                'evento_origem': method.routing_key
            }

            print(f"  ✓ Relatório gerado: {relatorio['id_relatorio']}")
            print(f"  ✓ Tipo: {relatorio['tipo']}")
            print(f"  ✓ Dados inclusos: Nome, Email, Matrícula, Curso")

            tempo_fim = time.time()
            tempo_processamento = tempo_fim - tempo_inicio

            print(f"\n✓ Relatório processado com sucesso")
            print(f"  Tempo de processamento: {tempo_processamento:.2f}s")
            print(f"  Total de relatórios gerados: {self.relatorios_gerados}")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"✗ Erro ao processar relatório: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def iniciar(self):
        print("\n" + "="*60)
        print("CONSUMIDOR DE RELATÓRIOS")
        print("="*60)
        print("→ Fila: relatorios")
        print("→ Padrão de rota: evento.aluno.*")
        print("→ Responsabilidade: Gerar relatórios de estatísticas acadêmicas")
        print("→ Status: Aguardando mensagens...")
        print("="*60 + "\n")

        self.broker.consume_messages(
            queue_name='relatorios',
            callback=self.processar_evento,
            auto_ack=False
        )

if __name__ == '__main__':
    consumidor = ConsumidorRelatorios()
    consumidor.iniciar()
