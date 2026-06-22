# Índice do Projeto - Arquitetura Orientada a Eventos e Mensageria

## 📚 Documentação

### Para Começar Rapidamente
- **[QUICKSTART.md](QUICKSTART.md)** — Guia de 5 minutos para executar tudo
  - Setup rápido
  - 4 comandos para rodar
  - Demonstrações obrigatórias checklist

### Documentação Principal
- **[README.md](README.md)** — Documentação completa do projeto
  - Visão geral da arquitetura
  - Componentes e responsabilidades
  - Conceitos arquiteturais demonstrados
  - Passo-a-passo de instalação
  - Trade-offs de processamento assíncrono

### Detalhes Arquiteturais
- **[ARQUITETURA.md](ARQUITETURA.md)** — Aprofundamento técnico
  - Fluxo completo de uma requisição
  - Padrão de roteamento (Topic Exchange)
  - Garantias de entrega (durabilidade, ACK, requeue)
  - Trade-offs implementados
  - Casos de uso reais
  - Monitoramento e observabilidade
  - Escalabilidade horizontal
  - Segurança
  - Testabilidade

### Exemplos de Requisições
- **[exemplos_requisicoes.md](exemplos_requisicoes.md)** — Todos os testes HTTP
  - Requisições com curl (Linux/Mac)
  - Requisições com PowerShell (Windows)
  - Teste de carga
  - Dicas de debugging
  - Exemplos com jq, Postman, Apache Bench

---

## 💻 Código Python

### Componentes Principais

#### Broker (Message Broker)
- **[broker.py](broker.py)** — Classe MessageBroker
  - Configuração do RabbitMQ
  - Declaração de exchange e filas
  - Publicação e consumo de mensagens
  - Gerenciamento de conexão

#### Produtor (API REST)
- **[producer.py](producer.py)** — API Flask
  - `POST /alunos` — Criar novo aluno (publica evento)
  - `POST /matriculas` — Registrar matrícula (publica evento)
  - `GET /eventos` — Listar eventos disponíveis
  - `GET /health` — Health check

#### Consumidores

- **[consumer_notificacoes.py](consumer_notificacoes.py)**
  - Fila: `notificacoes`
  - Padrão: `evento.aluno.criado`
  - Responsabilidade: Enviar emails
  - Tempo: ~1s por mensagem

- **[consumer_auditoria.py](consumer_auditoria.py)**
  - Fila: `auditoria`
  - Padrão: `evento.*` (todos os eventos)
  - Responsabilidade: Registrar logs
  - Tempo: ~0.5s por mensagem

- **[consumer_relatorios.py](consumer_relatorios.py)**
  - Fila: `relatorios`
  - Padrão: `evento.aluno.*`
  - Responsabilidade: Gerar relatórios
  - Tempo: ~1.5s por mensagem

#### Utilidades

- **[teste_api.py](teste_api.py)** — Script de testes automatizados
  - Health check
  - Listar eventos
  - Criar aluno
  - Registrar matrícula
  - Guia interativo

- **[demo_disponibilidade.py](demo_disponibilidade.py)** — Demo especial
  - Simula consumidor indisponível
  - Demonstra comportamento com requeue
  - Mostra persistência de mensagens

---

## 🐳 Infraestrutura

### Docker
- **[docker-compose.yml](docker-compose.yml)** — Configuração do RabbitMQ
  - RabbitMQ 3.12 com management plugin
  - Porta 5672 (AMQP)
  - Porta 15672 (Management Console)
  - Volume persistente para dados

### Dependências Python
- **[requirements.txt](requirements.txt)**
  - Flask==2.3.3
  - pika==1.3.1
  - python-dotenv==1.0.0
  - requests==2.31.0

### Configuração
- **[.env.example](.env.example)** — Variáveis de ambiente
  - Credenciais RabbitMQ
  - Configurações API
  - Configurações consumidores
  - Níveis de log

---

## 🚀 Quick Reference

### Iniciar o Projeto
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Iniciar RabbitMQ
docker-compose up -d

# 3. Iniciar produtor (Terminal 1)
python producer.py

# 4. Iniciar consumidores (Terminais 2-4)
python consumer_notificacoes.py
python consumer_auditoria.py
python consumer_relatorios.py

# 5. Rodar testes (Terminal 5)
python teste_api.py
```

### RabbitMQ Management
```
URL: http://localhost:15672
User: guest
Password: guest
```

### Endpoints da API
```
GET  /health              # Verificar saúde
GET  /eventos             # Listar eventos
POST /alunos              # Criar aluno (publica evento)
POST /matriculas          # Criar matrícula (publica evento)
```

---

## 📋 Demonstrações Obrigatórias

Checklist do que está demonstrado:

- ✅ **Publicação de mensagens** 
  - Ver em: Terminal do Produtor após POST /alunos

- ✅ **Consumo assíncrono**
  - Ver em: Terminais dos consumidores processando após API retornar

- ✅ **Fila recebendo mensagens**
  - Ver em: http://localhost:15672 → Queues → observe crescimento/decréscimo

- ✅ **Comportamento com consumidor indisponível**
  - Ver em: demo_disponibilidade.py ou parar consumidor manualmente

- ✅ **Reprocessamento/retry de mensagens**
  - Ver em: Quando consumer falha, basic_nack recoloca na fila

- ✅ **Tempo entre publicação e processamento**
  - Ver em: Timestamps em cada log (publicação → processamento)

- ✅ **Discussão sobre consistência eventual e falhas**
  - Ver em: ARQUITETURA.md → Casos de Uso Reais

---

## 📊 Estrutura de Diretórios

```
codigo/
├── INDICE.md                      ← Você está aqui
├── README.md                      ← Documentação principal
├── QUICKSTART.md                  ← Guia de 5 minutos
├── ARQUITETURA.md                 ← Detalhes técnicos
├── exemplos_requisicoes.md        ← Testes HTTP
│
├── broker.py                      ← Message Broker (RabbitMQ)
├── producer.py                    ← API REST (Produtor)
├── consumer_notificacoes.py       ← Consumidor 1
├── consumer_auditoria.py          ← Consumidor 2
├── consumer_relatorios.py         ← Consumidor 3
│
├── teste_api.py                   ← Testes automatizados
├── demo_disponibilidade.py        ← Demo especial
│
├── docker-compose.yml             ← Infraestrutura
├── requirements.txt               ← Dependências Python
└── .env.example                   ← Variáveis de ambiente
```

---

## 🎯 Fluxo de Leitura Recomendado

### Primeira Vez
1. [QUICKSTART.md](QUICKSTART.md) - Entender o básico (5 min)
2. [README.md](README.md) - Visão geral e componentes (15 min)
3. Executar `python teste_api.py` - Ver funcionando (5 min)

### Aprofundamento
4. [ARQUITETURA.md](ARQUITETURA.md) - Entender decisões (20 min)
5. [exemplos_requisicoes.md](exemplos_requisicoes.md) - Testar manualmente (10 min)
6. Ler código: `broker.py` → `producer.py` → `consumer_*.py` (30 min)

### Apresentação para Professor
- Preparar slides com diagramas
- Demonstrar ao vivo: `teste_api.py`
- Mostrar RabbitMQ Management Console
- Explicar conceitos usando [ARQUITETURA.md](ARQUITETURA.md)

---

## 🔍 Conceitos Demonstrados

| Conceito | Arquivo | Linha |
|----------|---------|-------|
| **Desacoplamento** | README.md | Sessão "Desacoplamento" |
| **Escalabilidade** | README.md | Sessão "Escalabilidade" |
| **Confiabilidade** | broker.py | `basic_ack()`, `basic_nack()` |
| **Consistência Eventual** | ARQUITETURA.md | Caso de Uso 1 |
| **Rastreabilidade** | broker.py | `message['timestamp']` |
| **Topic Exchange** | ARQUITETURA.md | Sessão "Padrão de Roteamento" |
| **ACK Manual** | consumer_*.py | `ch.basic_ack()` |
| **Requeue** | demo_disponibilidade.py | `basic_nack(requeue=True)` |

---

## 🛠️ Troubleshooting

### Problema: "Connection refused"
**Solução:** Verifique se RabbitMQ está rodando
```bash
docker ps
# Se não vê rabbitmq_eventos: docker-compose up -d
```

### Problema: "No module named pika"
**Solução:** Instale dependências
```bash
pip install -r requirements.txt
```

### Problema: Porta 5000 em uso
**Solução:** Modifique producer.py, última linha
```python
app.run(debug=True, port=5001)  # mudou para 5001
```

Mais troubleshooting em: [QUICKSTART.md](QUICKSTART.md#troubleshooting)

---

## 📞 Suporte

Para dúvidas sobre:
- **Setup inicial:** [QUICKSTART.md](QUICKSTART.md)
- **Como funciona:** [README.md](README.md)
- **Por que essas decisões:** [ARQUITETURA.md](ARQUITETURA.md)
- **Como testar:** [exemplos_requisicoes.md](exemplos_requisicoes.md)

---

## ✨ Diferenciais do Projeto

✅ Código limpo e bem documentado  
✅ Todos os requisitos funcionais cobertos  
✅ Todas as demonstrações obrigatórias implementadas  
✅ Múltiplas formas de testar (script, manual, carga)  
✅ Documentação em português  
✅ Pronto para apresentação acadêmica  
✅ Escalável para produção  
✅ Exemplos de Windows, Linux e Mac  

---

**Última atualização:** 2024-06-21  
**Status:** ✅ Completo e testado  
**Nível de dificuldade:** Intermediário  
**Tempo de aprendizado:** 1-2 horas  

Bom trabalho! 🚀
