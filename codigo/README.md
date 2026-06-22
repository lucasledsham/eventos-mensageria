# Arquitetura Orientada a Eventos e Mensageria

## Visão Geral

Este projeto implementa uma solução completa de mensageria e processamento assíncrono para uma plataforma acadêmica, demonstrando os conceitos fundamentais de **Arquitetura Orientada a Eventos (EOA)**.

### Objetivo

Demonstrar como a troca assíncrona de eventos pode:
- ✅ Reduzir **acoplamento** entre componentes
- ✅ Melhorar **escalabilidade** do sistema
- ✅ Permitir **flexibilidade** na adição de novos consumidores
- ✅ Garantir **confiabilidade** e processamento resiliente
- ✅ Implementar **consistência eventual**

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    API REST (PRODUTOR)                   │
│                   Flask + Python 3.11                    │
│                                                          │
│  POST /alunos               → evento.aluno.criado       │
│  POST /matriculas           → evento.aluno.matriculado  │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ Publica evento
                   ▼
┌──────────────────────────────────────────────────────────┐
│              MESSAGE BROKER (RABBITMQ)                   │
│                                                          │
│  Exchange: eventos_academicos (tipo: topic)             │
│                                                          │
│  Routing patterns:                                       │
│  ├── evento.aluno.criado                               │
│  ├── evento.aluno.matriculado                          │
│  └── evento.*                                           │
└──────────────────────────────────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
    ┌───────┐  ┌────────┐  ┌──────────┐
    │ FILA  │  │ FILA   │  │ FILA     │
    │notif. │  │auditoria│  │relatórios│
    └───┬───┘  └────┬───┘  └──────┬───┘
        │           │             │
        ▼           ▼             ▼
    ┌──────────────────────────────────────────┐
    │           CONSUMIDORES                   │
    │                                          │
    │ • Notificações   (envia emails)         │
    │ • Auditoria      (registra logs)        │
    │ • Relatórios     (gera estatísticas)    │
    └──────────────────────────────────────────┘
```

---

## Componentes

### 1. **Produtor (API REST)**
**Arquivo:** `producer.py`

Responsável pela ação principal do sistema.

```python
POST /alunos
{
  "nome": "João Silva",
  "email": "joao@exemplo.com",
  "matricula": "2024001",
  "curso": "Engenharia de Software"
}
```

**Resultado:** Evento publicado `evento.aluno.criado`

### 2. **Message Broker**
**Arquivo:** `broker.py`

Intermediário que desacopla produtores e consumidores.

**Características:**
- Exchange do tipo `topic` para roteamento flexível
- Filas duráveis (persistem entre reinicializações)
- Acknowledgment de mensagens para garantia de entrega

### 3. **Consumidores**

#### a) Notificações (`consumer_notificacoes.py`)
- **Fila:** `notificacoes`
- **Padrão:** `evento.aluno.criado`
- **Função:** Enviar email ao aluno
- **Tempo de processamento:** ~1s

#### b) Auditoria (`consumer_auditoria.py`)
- **Fila:** `auditoria`
- **Padrão:** `evento.*` (todos os eventos)
- **Função:** Registrar log para compliance
- **Tempo de processamento:** ~0.5s

#### c) Relatórios (`consumer_relatorios.py`)
- **Fila:** `relatorios`
- **Padrão:** `evento.aluno.*`
- **Função:** Gerar relatórios estatísticos
- **Tempo de processamento:** ~1.5s

---

## Conceitos Arquiteturais Demonstrados

### 1. **Desacoplamento**
```
❌ SEM mensageria (acoplado):
  API → Email → Auditoria → Relatórios
  (Se um falhar, tudo falha)

✅ COM mensageria (desacoplado):
  API → [Message Broker] → {Email, Auditoria, Relatórios}
  (Cada componente é independente)
```

### 2. **Escalabilidade**
Adicione novos consumidores **sem modificar o produtor**:
```python
# Novo consumidor de notificação via SMS
queue_bind(exchange='eventos_academicos', 
           queue='sms',
           routing_key='evento.aluno.criado')
```

### 3. **Confiabilidade e Retry**
Mensagens são reprocessadas automaticamente se o consumidor falhar:
```python
if erro:
    ch.basic_nack(requeue=True)  # Recoloca na fila
    # Será tentada novamente automaticamente
```

### 4. **Consistência Eventual**
Sistema eventualmente consistente:
- Ação principal (API): síncrone e imediata
- Ações secundárias (email, auditoria): assíncronas
- Garante que todos os consumidores processem a mensagem

### 5. **Rastreabilidade**
Cada mensagem carrega:
- `timestamp`: quando foi publicada
- `routing_key`: tipo de evento
- `delivery_tag`: identificador único

---

## Instalação e Execução

### Pré-requisitos
- Docker e Docker Compose (para RabbitMQ)
- Python 3.11+
- pip

### Passo 1: Instalar Dependências

```bash
cd codigo
pip install -r requirements.txt
```

### Passo 2: Iniciar RabbitMQ

```bash
docker-compose up -d
```

Verifique se está rodando:
```bash
docker ps
# deve listar: rabbitmq_eventos
```

Acesse a management console: http://localhost:15672 (usuário: guest, senha: guest)

### Passo 3: Iniciar o Produtor

```bash
python producer.py
```

**Saída esperada:**
```
✓ Conectado ao RabbitMQ em localhost:5672
✓ Exchange 'eventos_academicos' declarado
✓ Fila 'notificacoes' declarada e ligada ao padrão 'evento.aluno.criado'
✓ Fila 'auditoria' declarada e ligada ao padrão 'evento.*'
✓ Fila 'relatorios' declarada e ligada ao padrão 'evento.aluno.*'

PRODUTOR DE EVENTOS - PLATAFORMA ACADÊMICA
============================================================
API iniciada em http://localhost:5000
```

### Passo 4: Iniciar os Consumidores (em terminais separados)

```bash
# Terminal 1
python consumer_notificacoes.py

# Terminal 2
python consumer_auditoria.py

# Terminal 3
python consumer_relatorios.py
```

### Passo 5: Executar os Testes

```bash
python teste_api.py
```

---

## Demonstrações Obrigatórias

### ✅ 1. Publicação de Mensagens
```bash
curl -X POST http://localhost:5000/alunos \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Santos",
    "email": "maria@exemplo.com",
    "matricula": "2024002"
  }'
```

**Resultado:** Mensagem publicada com timestamp

### ✅ 2. Consumo Assíncrono
Os consumidores processam a mensagem **após** a API retornar a resposta.

Terminal do Produtor:
```
→ MENSAGEM PUBLICADA
  Tipo: evento.aluno.criado
  Timestamp: 2024-06-21T10:15:30.123456
```

Terminal dos Consumidores (após ~100ms):
```
[CONSUMIDOR: NOTIFICAÇÕES]
→ Evento recebido: evento.aluno.criado
✓ Notificação processada com sucesso
  Tempo de processamento: 1.05s
```

### ✅ 3. Fila Recebendo Mensagens
Na RabbitMQ Management Console (http://localhost:15672):
- Vá em "Queues and Streams"
- Observe mensagens sendo acumuladas/processadas nas filas

### ✅ 4. Comportamento com Consumidor Indisponível
```bash
# 1. Parar um consumidor (Ctrl+C)
# 2. Enviar uma nova requisição POST /alunos
# 3. Verificar fila na console - mensagem fica pendente
# 4. Reiniciar o consumidor
# 5. Mensagem é processada automaticamente
```

Ou use o script de demo:
```bash
python demo_disponibilidade.py
```

### ✅ 5. Reprocessamento e Retry
Quando um consumidor falha:
```python
ch.basic_nack(requeue=True)  # Recoloca na fila
```

O RabbitMQ automaticamente tenta novamente.

### ✅ 6. Tempo entre Publicação e Processamento
Cada consumidor exibe:
```
→ Processamento iniciado em: 2024-06-21T10:15:30.500000
✓ Processado em: 2024-06-21T10:15:31.550000
  Tempo decorrido: 1.05s
```

### ✅ 7. Discussão sobre Consistência Eventual e Falhas

**Cenário 1: Falha do Consumidor**
```
Antes: API retorna 201 CRIADO
Depois: Email ainda será enviado (quando consumidor voltar)
Resultado: Sistema eventualmente consistente
```

**Cenário 2: Falha da API**
```
Antes: Produtor recebe erro
Depois: Nenhuma mensagem publicada
Resultado: Consistência garantida
```

**Cenário 3: RabbitMQ Indisponível**
```
Resultado: Mensagens persistem em disco
Quando broker voltar: Todas as mensagens são reprocessadas
```

---

## Fluxo de Execução Completo

```mermaid
1. Cliente → POST /alunos
   ↓
2. API valida dados (síncrono)
   ↓
3. API publica evento (síncrono)
   ↓
4. API retorna 201 CRIADO (IMEDIATO)
   ↓ (enquanto cliente recebe resposta...)
5. RabbitMQ armazena mensagem
   ↓
6. Consumidor 1 processa (≈1s)
7. Consumidor 2 processa (≈0.5s)
8. Consumidor 3 processa (≈1.5s)
   ↓ (todos em paralelo)
9. Todos os consumidores confirmam (ACK)
   ↓
10. Mensagem removida da fila
```

---

## Trade-offs de Processamento Assíncrono

### Vantagens ✅
- **Desacoplamento:** Componentes independentes
- **Escalabilidade:** Adicione consumidores sem modificar produtor
- **Confiabilidade:** Retry automático, persistência
- **Performance:** API responde imediatamente
- **Flexibilidade:** Novos consumidores em tempo de execução

### Desafios ⚠️
- **Latência:** Processamento não é imediato
- **Complexidade:** Debug é mais difícil
- **Consistência eventual:** Dados podem estar temporariamente inconsistentes
- **Monitoramento:** Precisa de logging e observabilidade

---

## Verificação da Arquitetura

### Health Check
```bash
curl http://localhost:5000/health
```

Resposta:
```json
{
  "status": "ok",
  "servico": "Produtor de Eventos Acadêmicos"
}
```

### RabbitMQ Status
```bash
docker exec rabbitmq_eventos rabbitmq-diagnostics ping
# Resultado: pong
```

### Listar Eventos
```bash
curl http://localhost:5000/eventos
```

---

## Parar o Sistema

```bash
# Parar consumidores (Ctrl+C em cada terminal)

# Parar produtor (Ctrl+C)

# Parar RabbitMQ
docker-compose down
```

---

## Tecnologias Utilizadas

| Componente | Tecnologia | Motivo |
|-----------|-----------|--------|
| **Produtor** | Flask + Python | Sintaxe clara, fácil prototipagem |
| **Message Broker** | RabbitMQ | Robusto, suporte a topic exchange, durabilidade |
| **Consumidores** | Python + pika | Biblioteca madura, bom suporte |
| **Infraestrutura** | Docker | Fácil execução, reprodutibilidade |

---

## Conclusão

Este projeto demonstra uma arquitetura moderna baseada em eventos que é:
- ✅ **Escalável:** Adicione componentes sem impacto
- ✅ **Resiliente:** Tolera falhas temporárias
- ✅ **Flexível:** Fácil de evoluir
- ✅ **Rastreável:** Logs e auditoria integrados
- ✅ **Educacional:** Código limpo e bem documentado

Perfeito para entender os conceitos de EOA em um contexto acadêmico realista!
