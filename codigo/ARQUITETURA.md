# Detalhes Arquiteturais

## Fluxo Completo de uma Requisição

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Cliente envia: POST /alunos {nome, email, matricula, curso}                │
└──────────────────────────┬──────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ ETAPA 1: PROCESSAMENTO SÍNCRONO (< 100ms)                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ 1. API valida entrada (obrigatório: nome, email)                           │
│ 2. Gera UUID para aluno_id                                                 │
│ 3. Conecta ao RabbitMQ                                                      │
│ 4. Publica evento na exchange 'eventos_academicos'                         │
│ 5. Retorna 201 CRIADO ao cliente ← IMEDIATO                                │
│                                                                              │
│ ⏱️  Tempo total: 50-100ms                                                    │
│                                                                              │
└──────────────────────────┬──────────────────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────────┐
        │    RabbitMQ (Message Broker)             │
        │                                          │
        │ Exchange: eventos_academicos             │
        │ Type: topic                              │
        │ Durable: true                            │
        │                                          │
        │ Routing key: evento.aluno.criado         │
        │ Mensagem: {id, nome, email, ...}         │
        │ Timestamp: ISO8601                       │
        └──────────┬────────────────────────────────┘
                   │
        ┌──────────┴──────────┬─────────────┐
        │                     │             │
        ▼                     ▼             ▼
    ┌─────────┐         ┌──────────┐   ┌──────────┐
    │ Fila    │         │ Fila     │   │ Fila     │
    │notif    │         │auditoria │   │relatorios│
    │(durable)│         │(durable) │   │(durable) │
    └────┬────┘         └────┬─────┘   └────┬─────┘
         │                   │              │
         ▼                   ▼              ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ ETAPA 2: PROCESSAMENTO ASSÍNCRONO (paralelo, 0.5-1.5s)                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Consumidor 1: NOTIFICAÇÕES          Consumidor 2: AUDITORIA                │
│ ├─ Recebe mensagem                  ├─ Recebe mensagem                    │
│ ├─ Decodifica JSON                  ├─ Decodifica JSON                    │
│ ├─ Simula envio de email (~1s)      ├─ Registra log (~0.5s)              │
│ ├─ Envia ACK (acknowledge)          ├─ Envia ACK                          │
│ └─ Mensagem removida da fila        └─ Mensagem removida da fila          │
│                                                                              │
│ Consumidor 3: RELATÓRIOS                                                   │
│ ├─ Recebe mensagem                                                         │
│ ├─ Decodifica JSON                                                         │
│ ├─ Gera relatório PDF (~1.5s)                                              │
│ ├─ Envia ACK                                                               │
│ └─ Mensagem removida da fila                                               │
│                                                                              │
│ ⏱️  Tempo total: até 1.5s (paralelo, não sequencial)                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Padrão de Roteamento (Topic Exchange)

```
Routing Keys:
├── evento.aluno.criado
├── evento.aluno.matriculado
├── evento.aluno.atualizado
└── evento.aluno.deletado

Binding Patterns:
├── Fila "notificacoes"    ← evento.aluno.criado
├── Fila "auditoria"       ← evento.*           (todos)
└── Fila "relatorios"      ← evento.aluno.*    (qualquer aluno)

Resultado:
┌─────────────────────────────────────────────────────┐
│ Se evento.aluno.criado é publicado:                │
│ ├─ notificacoes recebe ✓                          │
│ ├─ auditoria recebe ✓                             │
│ ├─ relatorios recebe ✓                            │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Se evento.aluno.matriculado é publicado:           │
│ ├─ notificacoes recebe ✗                          │
│ ├─ auditoria recebe ✓                             │
│ ├─ relatorios recebe ✓                            │
└─────────────────────────────────────────────────────┘
```

---

## Garantias de Entrega

### Durabilidade (Persistence)
```python
# Mensagem é armazenada em disco
properties=pika.BasicProperties(
    delivery_mode=2  # PERSISTENT (1=transient)
)

# Resultado: Se RabbitMQ reinicia, mensagem ainda existe
```

### Acknowledgment (ACK)
```
SEM ACK (auto_ack=True):
├─ Mensagem removida da fila ANTES de processar
├─ Se consumidor falha: mensagem é perdida ✗
└─ Rápido mas arriscado

COM ACK Manual (auto_ack=False):
├─ Mensagem só sai da fila APÓS processar
├─ Se consumidor falha: mensagem fica na fila ✓
└─ Lento mas seguro (NOSSO MODELO)
```

### Requeue
```python
# Se erro durante processamento:
ch.basic_nack(requeue=True)  # Recoloca no final da fila

# Workflow:
1. Mensagem entregue ao consumidor
2. Consumidor falha no processamento
3. Chamada basic_nack(requeue=True)
4. Mensagem volta para o final da fila
5. Consumidor a recebe novamente
6. ... repete até sucesso
```

---

## Trade-offs Implementados

### ✅ Vantagens Escolhidas

| Aspecto | Decisão | Benefício |
|--------|---------|-----------|
| **Durabilidade** | Filas duráveis | Mensagens sobrevivem a falhas |
| **Confiabilidade** | ACK Manual | Garantia de processamento |
| **Flexibilidade** | Topic Exchange | Fácil adicionar novos consumidores |
| **Escalabilidade** | Processamento paralelo | Múltiplos consumidores simultâneos |
| **Rastreabilidade** | Timestamp + Routing Key | Auditoria completa |

### ⚠️ Desafios Mitigados

| Desafio | Solução |
|---------|---------|
| **Latência** | Aceitável para tarefas em background |
| **Complexidade** | Código bem documentado |
| **Consistência eventual** | Aplicável ao domínio (acadêmico) |
| **Debugging** | Logs detalhados em cada etapa |

---

## Casos de Uso Reais

### Caso 1: Email Falha Temporariamente
```
1. API publica: evento.aluno.criado
2. Consumer notificacoes tenta enviar email
3. Serviço de email indisponível → exceção
4. Consumer: ch.basic_nack(requeue=True)
5. Mensagem volta para fila
6. Após 5 segundos: Consumer tenta novamente
7. Email agora disponível → sucesso → ACK
8. Mensagem removida da fila

Resultado: Email sempre é enviado (eventualmente)
```

### Caso 2: Novo Requisito: Enviar SMS
```
Antes (acoplado):
├─ Modificar API
├─ Testar tudo
├─ Deploy em produção
└─ Risco alto

Depois (desacoplado):
├─ Criar consumer_sms.py
├─ Adicionar binding: evento.aluno.criado → fila_sms
├─ Iniciar consumer
└─ Pronto! Sem modificar API ou outro código

Resultado: Zero downtime, baixo risco
```

### Caso 3: Pico de Tráfego
```
Cenário: 1000 novos alunos em 1 minuto

Sem mensageria:
├─ API tenta processar tudo
├─ Timeout após 30s
├─ Emails não são enviados
└─ Sistema falha

Com mensageria:
├─ API publica 1000 eventos em 5s
├─ RabbitMQ armazena tudo em disco
├─ Consumidores processam no seu próprio ritmo
├─ Após 2 horas: tudo processado
└─ Sistema nunca fica sobrecarregado
```

---

## Monitoramento e Observabilidade

### Métricas Principais
```
1. Taxa de publicação: eventos/segundo
2. Taxa de consumo: eventos/segundo
3. Latência: tempo publicação → processamento
4. Taxa de retry: quantas tentativas falham
5. Queue depth: quantas mensagens aguardam
6. Consumer concurrency: quantos consumidores rodando
```

### Logs Estruturados
```json
{
  "timestamp": "2024-06-21T10:15:30.123456",
  "component": "producer",
  "action": "publish",
  "routing_key": "evento.aluno.criado",
  "aluno_id": "550e8400-e29b-41d4-a716-446655440000",
  "duration_ms": 45
}

{
  "timestamp": "2024-06-21T10:15:31.234567",
  "component": "consumer_notificacoes",
  "action": "process",
  "routing_key": "evento.aluno.criado",
  "status": "success",
  "duration_ms": 1050
}
```

---

## Escalabilidade Horizontal

### Cenário: Muitos Eventos de Email
```
Problema: 1 consumidor não consegue processar 1000 emails/min

Solução:
1. Iniciar 10 instâncias do consumer_notificacoes
2. RabbitMQ distribui as mensagens entre elas
3. Cada instância processa ~100 emails/min
4. Total: 1000 emails/min processados

Código (pseudo):
for i in range(10):
    subprocess.start("python consumer_notificacoes.py")
```

### Cenário: Múltiplos Data Centers
```
RabbitMQ Cluster:
├─ Node 1 (Datacenter A): primary
├─ Node 2 (Datacenter B): replica
└─ Node 3 (Datacenter C): replica

Benefícios:
├─ Alta disponibilidade (tolerância a 1 falha)
├─ Distribuição geográfica
└─ Fallback automático se data center cai
```

---

## Segurança

### Implementado
```python
# Credenciais
credentials = pika.PlainCredentials('guest', 'guest')

# Pode ser melhorado para:
credentials = pika.PlainCredentials(
    username=os.getenv('RABBITMQ_USER'),
    password=os.getenv('RABBITMQ_PASSWORD')
)

# Ou usar SSL/TLS:
context = pika.SSLContext()
parameters = pika.ConnectionParameters(
    host='rabbitmq.prod.com',
    port=5671,
    ssl_options=pika.SSLOptions(context)
)
```

### Recomendações para Produção
1. Usar secrets management (AWS Secrets, HashiCorp Vault)
2. Habilitar SSL/TLS entre cliente e RabbitMQ
3. Usar RabbitMQ com autenticação forte
4. Implementar rate limiting
5. Validar/sanitizar payloads
6. Criptografar dados sensíveis em mensagens

---

## Testabilidade

### Teste Unitário
```python
def test_message_published():
    broker = MessageBroker()
    msg = broker.publish_message('evento.test', {'data': 'test'})
    assert msg['timestamp'] is not None
```

### Teste de Integração
```python
def test_consumer_processes_message():
    # 1. Publish mensagem
    broker.publish_message('evento.test', {...})
    
    # 2. Consumidor processa
    consumer = ConsumidorTest()
    consumer.process()
    
    # 3. Verificar resultado
    assert consumer.processed == True
```

### Teste de Carga
```bash
# Simular 1000 eventos/segundo
wrk -t4 -c100 -d30s --script=post.lua http://localhost:5000/alunos
```

---

Fim da documentação arquitetural! 🏗️
