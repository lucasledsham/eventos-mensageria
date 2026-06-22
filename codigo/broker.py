import pika
import json
import time
from datetime import datetime

class MessageBroker:
    def __init__(self, host='localhost', port=5672):
        self.host = host
        self.port = port
        self.connection = None
        self.channel = None
        self.setup_connection()

    def setup_connection(self):
        try:
            credentials = pika.PlainCredentials('guest', 'guest')
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            print(f"✓ Conectado ao RabbitMQ em {self.host}:{self.port}")
        except Exception as e:
            print(f"✗ Erro ao conectar ao RabbitMQ: {e}")
            raise

    def declare_exchange_and_queues(self):
        try:
            self.channel.exchange_declare(
                exchange='eventos_academicos',
                exchange_type='topic',
                durable=True
            )
            print("✓ Exchange 'eventos_academicos' declarado")

            queues = {
                'notificacoes': 'evento.aluno.criado',
                'auditoria': 'evento.*',
                'relatorios': 'evento.aluno.*'
            }

            for queue_name, routing_key in queues.items():
                self.channel.queue_declare(
                    queue=queue_name,
                    durable=True
                )
                self.channel.queue_bind(
                    exchange='eventos_academicos',
                    queue=queue_name,
                    routing_key=routing_key
                )
                print(f"✓ Fila '{queue_name}' declarada e ligada ao padrão '{routing_key}'")
        except Exception as e:
            print(f"✗ Erro ao declarar exchange/filas: {e}")
            raise

    def publish_message(self, routing_key, message_data):
        try:
            message = {
                'timestamp': datetime.now().isoformat(),
                'routing_key': routing_key,
                **message_data
            }

            self.channel.basic_publish(
                exchange='eventos_academicos',
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            print(f"\n→ MENSAGEM PUBLICADA")
            print(f"  Tipo: {routing_key}")
            print(f"  Dados: {json.dumps(message_data, ensure_ascii=False, indent=2)}")
            print(f"  Timestamp: {message['timestamp']}")
            return message
        except Exception as e:
            print(f"✗ Erro ao publicar mensagem: {e}")
            raise

    def consume_messages(self, queue_name, callback, auto_ack=False):
        try:
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=auto_ack
            )
            print(f"→ Consumidor iniciado para fila '{queue_name}'")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("\n✓ Consumidor encerrado")
            self.channel.stop_consuming()
            self.connection.close()
        except Exception as e:
            print(f"✗ Erro ao consumir mensagens: {e}")
            raise

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("✓ Conexão com RabbitMQ fechada")
