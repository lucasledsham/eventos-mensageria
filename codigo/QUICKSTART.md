# Guia Rápido - Arquitetura Orientada a Eventos

## 5 Minutos para Começar

### Passo 1: Preparação
```bash
# Windows PowerShell
cd codigo
pip install -r requirements.txt
docker-compose up -d
```

### Passo 2: Iniciar em 4 Terminais
```bash
# Terminal 1 - Produtor (API)
python producer.py

# Terminal 2 - Consumidor de Notificações
python consumer_notificacoes.py

# Terminal 3 - Consumidor de Auditoria
python consumer_auditoria.py

# Terminal 4 - Consumidor de Relatórios
python consumer_relatorios.py
```

### Passo 3: Teste Automático
```bash
# Terminal 5
python teste_api.py
```

---

## Demonstração Manual

### Criar um Aluno
```powershell
$body = @{
    nome = "Lucas Silva"
    email = "lucas@exemplo.com"
    matricula = "2024001"
    curso = "Engenharia de Software"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/alunos" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

### Registrar Matrícula
```powershell
$body = @{
    aluno_id = "<COPIE_O_ID_DO_ALUNO_ANTERIOR>"
    disciplina = "Arquitetura de Software"
    semestre = "2024.1"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/matriculas" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

---

## O Que Observar

✅ **No Terminal do Produtor:**
- Mensagem publicada com timestamp
- "Evento publicado com sucesso"

✅ **Nos Terminais dos Consumidores:**
- Cada um processa a mensagem
- Tempo de processamento diferente
- Demonstra processamento paralelo e assíncrono

✅ **Na Console RabbitMQ** (http://localhost:15672)
- Vá em "Queues"
- Veja as mensagens sendo processadas
- Observe o desacoplamento

---

## Demonstrações Obrigatórias

| # | Demonstração | Como Testar |
|---|---|---|
| 1 | **Publicação de mensagens** | Terminal do Produtor: veja "MENSAGEM PUBLICADA" |
| 2 | **Consumo assíncrono** | Consumidores processam APÓS API retornar |
| 3 | **Fila recebendo mensagens** | Console RabbitMQ: Queues → escolha uma fila |
| 4 | **Comportador com consumidor indisponível** | Ctrl+C em um consumidor → enviar novo aluno → fila acumula → reiniciar consumidor |
| 5 | **Reprocessamento/retry** | Use `demo_disponibilidade.py` |
| 6 | **Tempo de publicação/processamento** | Veja timestamps nos logs: "timestamp:" |
| 7 | **Consistência eventual** | API retorna imediato, consumidores processam depois |

---

## Troubleshooting

### ❌ Erro: "Connection refused"
```bash
# Verifique se RabbitMQ está rodando
docker ps
# Se não: docker-compose up -d
```

### ❌ Erro: "No module named pika"
```bash
pip install pika
```

### ❌ Porta 5000 já em uso
```bash
# Modificar producer.py, última linha:
app.run(debug=True, port=5001)  # mudou de 5000 para 5001
```

### ❌ RabbitMQ Management não abre
```bash
# Aguarde 10 segundos após docker-compose up
docker logs rabbitmq_eventos
```

---

## Próximas Explorações

1. **Adicione um novo consumidor** (ex: SMS)
2. **Implemente dead-letter queue** para mensagens que falham
3. **Monitore performance** com Prometheus + Grafana
4. **Teste failover** com múltiplas instâncias do RabbitMQ
5. **Implemente correlationId** para rastrear mensagens end-to-end

---

## Arquivos Principais

```
codigo/
├── producer.py              # API REST (ação principal)
├── broker.py                # Configuração do RabbitMQ
├── consumer_notificacoes.py # Consumidor 1
├── consumer_auditoria.py    # Consumidor 2
├── consumer_relatorios.py   # Consumidor 3
├── demo_disponibilidade.py  # Demo de indisponibilidade
├── teste_api.py             # Testes automatizados
├── docker-compose.yml       # RabbitMQ em container
├── requirements.txt         # Dependências Python
├── README.md                # Documentação completa
└── QUICKSTART.md            # Este arquivo
```

---

## Conceitos-Chave Demonstrados

### 🎯 Desacoplamento
API não conhece consumidores. Mensagens são o "contrato".

### 🚀 Escalabilidade
Adicione 10 consumidores sem modificar API.

### 🛡️ Confiabilidade
Se consumidor falha, mensagem fica na fila até ser processada.

### ⚡ Performance
API responde em <100ms, processamento acontece em background.

### 📊 Rastreabilidade
Cada mensagem tem timestamp, routing_key, e ID único.

---

Divirta-se explorando arquitetura orientada a eventos! 🚀
