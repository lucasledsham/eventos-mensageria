# Exemplos de Requisições HTTP

## Requisição 1: Health Check

Verificar se a API está respondendo.

```bash
# Linux/Mac
curl http://localhost:5000/health

# Windows PowerShell
Invoke-WebRequest -Uri "http://localhost:5000/health" -Method GET
```

**Resposta esperada:**
```json
{
  "status": "ok",
  "servico": "Produtor de Eventos Acadêmicos"
}
```

---

## Requisição 2: Listar Eventos Disponíveis

Ver todos os tipos de eventos suportados.

```bash
# Linux/Mac
curl http://localhost:5000/eventos

# Windows PowerShell
Invoke-WebRequest -Uri "http://localhost:5000/eventos" -Method GET | ConvertFrom-Json | ConvertTo-Json
```

**Resposta esperada:**
```json
{
  "eventos_disponiveis": [
    {
      "tipo": "evento.aluno.criado",
      "descricao": "Disparado quando um novo aluno é cadastrado",
      "consumidores": ["notificacoes", "auditoria", "relatorios"]
    },
    {
      "tipo": "evento.aluno.matriculado",
      "descricao": "Disparado quando um aluno realiza matrícula",
      "consumidores": ["auditoria", "relatorios"]
    }
  ]
}
```

---

## Requisição 3: Criar Novo Aluno

Endpoint principal que publica evento `evento.aluno.criado`.

### Linux/Mac com curl
```bash
curl -X POST http://localhost:5000/alunos \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "email": "joao@example.com",
    "matricula": "2024001",
    "curso": "Engenharia de Software"
  }'
```

### Windows PowerShell
```powershell
$body = @{
    nome = "João Silva"
    email = "joao@example.com"
    matricula = "2024001"
    curso = "Engenharia de Software"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/alunos" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

### Windows cmd.exe
```cmd
powershell -NoProfile -Command ^
  $body = @{nome='João Silva'; email='joao@example.com'; matricula='2024001'; curso='Engenharia de Software'} | ConvertTo-Json; ^
  Invoke-WebRequest -Uri 'http://localhost:5000/alunos' -Method POST -Body $body -ContentType 'application/json'
```

**Resposta esperada (201 Created):**
```json
{
  "mensagem": "Aluno cadastrado com sucesso",
  "aluno_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-06-21T10:15:30.123456"
}
```

---

## Requisição 4: Registrar Matrícula

Endpoint que publica evento `evento.aluno.matriculado`.

**⚠️ Substitua `<ALUNO_ID>` pelo ID retornado na Requisição 3!**

### Linux/Mac
```bash
curl -X POST http://localhost:5000/matriculas \
  -H "Content-Type: application/json" \
  -d '{
    "aluno_id": "550e8400-e29b-41d4-a716-446655440000",
    "disciplina": "Arquitetura de Software",
    "semestre": "2024.1"
  }'
```

### Windows PowerShell
```powershell
$body = @{
    aluno_id = "550e8400-e29b-41d4-a716-446655440000"
    disciplina = "Arquitetura de Software"
    semestre = "2024.1"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/matriculas" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

**Resposta esperada (201 Created):**
```json
{
  "mensagem": "Matrícula registrada com sucesso",
  "timestamp": "2024-06-21T10:15:35.567890"
}
```

---

## Requisição 5: Criar Múltiplos Alunos (Para Teste de Carga)

### Linux/Mac com loop
```bash
#!/bin/bash

for i in {1..5}; do
  curl -X POST http://localhost:5000/alunos \
    -H "Content-Type: application/json" \
    -d "{
      \"nome\": \"Aluno $i\",
      \"email\": \"aluno$i@example.com\",
      \"matricula\": \"2024$(printf "%03d" $i)\",
      \"curso\": \"Engenharia de Software\"
    }"
  echo "\n---\n"
done
```

### Windows PowerShell
```powershell
1..5 | ForEach-Object {
    $body = @{
        nome = "Aluno $_"
        email = "aluno$_@example.com"
        matricula = "2024$('{0:D3}' -f $_)"
        curso = "Engenharia de Software"
    } | ConvertTo-Json
    
    Invoke-WebRequest -Uri "http://localhost:5000/alunos" `
        -Method POST `
        -Body $body `
        -ContentType "application/json"
    
    Start-Sleep -Seconds 1
}
```

---

## Requisição 6: Erro - Falta Campo Obrigatório

Testar validação de entrada.

### Linux/Mac
```bash
curl -X POST http://localhost:5000/alunos \
  -H "Content-Type: application/json" \
  -d '{"nome": "João Silva"}'
```

### Windows PowerShell
```powershell
$body = @{
    nome = "João Silva"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/alunos" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

**Resposta esperada (400 Bad Request):**
```json
{
  "erro": "Nome e email são obrigatórios"
}
```

---

## Requisição 7: Teste com Variáveis de Ambiente

Reutilizar IDs entre requisições.

### Linux/Mac
```bash
# Criar aluno e salvar ID
ALUNO_ID=$(curl -s -X POST http://localhost:5000/alunos \
  -H "Content-Type: application/json" \
  -d '{"nome":"Maria","email":"maria@example.com"}' | grep -o '"aluno_id":"[^"]*"' | cut -d'"' -f4)

echo "ID do aluno criado: $ALUNO_ID"

# Usar ID em próxima requisição
curl -X POST http://localhost:5000/matriculas \
  -H "Content-Type: application/json" \
  -d "{\"aluno_id\":\"$ALUNO_ID\",\"disciplina\":\"Cálculo\"}"
```

### Windows PowerShell
```powershell
# Criar aluno e extrair ID
$response = Invoke-WebRequest -Uri "http://localhost:5000/alunos" `
    -Method POST `
    -Body (@{
        nome = "Maria"
        email = "maria@example.com"
    } | ConvertTo-Json) `
    -ContentType "application/json"

$aluno_id = ($response.Content | ConvertFrom-Json).aluno_id
Write-Host "ID do aluno criado: $aluno_id"

# Usar ID em próxima requisição
$matricula_body = @{
    aluno_id = $aluno_id
    disciplina = "Cálculo"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/matriculas" `
    -Method POST `
    -Body $matricula_body `
    -ContentType "application/json"
```

---

## Requisição 8: Teste com jq (Formatação JSON)

Linux/Mac com jq instalado.

```bash
# Instalação (se necessário)
# sudo apt-get install jq  # Debian/Ubuntu
# brew install jq          # macOS

# Criar aluno e formatar resposta
curl -s -X POST http://localhost:5000/alunos \
  -H "Content-Type: application/json" \
  -d '{"nome":"Pedro","email":"pedro@example.com"}' | jq '.'

# Extrair apenas o ID
curl -s -X POST http://localhost:5000/alunos \
  -H "Content-Type: application/json" \
  -d '{"nome":"Ana","email":"ana@example.com"}' | jq -r '.aluno_id'

# Listar eventos e filtrar por tipo
curl -s http://localhost:5000/eventos | jq '.eventos_disponiveis[] | select(.tipo | contains("aluno"))'
```

---

## Requisição 9: Teste com Postman

Importar coleção de requisições.

```json
{
  "info": {
    "name": "Plataforma Acadêmica",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "http://localhost:5000/health"
      }
    },
    {
      "name": "Listar Eventos",
      "request": {
        "method": "GET",
        "url": "http://localhost:5000/eventos"
      }
    },
    {
      "name": "Criar Aluno",
      "request": {
        "method": "POST",
        "url": "http://localhost:5000/alunos",
        "header": [
          {"key": "Content-Type", "value": "application/json"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"nome\": \"Lucas Silva\",\n  \"email\": \"lucas@example.com\",\n  \"matricula\": \"2024001\",\n  \"curso\": \"Engenharia de Software\"\n}"
        }
      }
    },
    {
      "name": "Registrar Matrícula",
      "request": {
        "method": "POST",
        "url": "http://localhost:5000/matriculas",
        "header": [
          {"key": "Content-Type", "value": "application/json"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"aluno_id\": \"{{aluno_id}}\",\n  \"disciplina\": \"Arquitetura de Software\",\n  \"semestre\": \"2024.1\"\n}"
        }
      }
    }
  ]
}
```

---

## Teste de Carga com Apache Bench

Simular múltiplas requisições simultâneas.

```bash
# Instalar (se necessário)
# sudo apt-get install apache2-utils  # Linux
# brew install httpd                  # macOS

# Teste simples: 100 requisições, 10 simultâneas
ab -n 100 -c 10 http://localhost:5000/health

# Teste POST: criar 50 alunos
# Crie um arquivo data.txt:
# {"nome":"Aluno1","email":"aluno1@ex.com"}
# {"nome":"Aluno2","email":"aluno2@ex.com"}
# ...

# Depois:
while IFS= read -r line; do
  curl -X POST http://localhost:5000/alunos \
    -H "Content-Type: application/json" \
    -d "$line"
done < data.txt
```

---

## Teste com GNU parallel

Processo paralelo de requisições.

```bash
# Instalar (se necessário)
# sudo apt-get install parallel

# Criar 100 alunos em paralelo (10 por vez)
seq 1 100 | parallel --jobs 10 \
  'curl -s -X POST http://localhost:5000/alunos \
    -H "Content-Type: application/json" \
    -d "{\"nome\":\"Aluno {}\",\"email\":\"aluno{}@example.com\"}" \
  | grep -o "aluno_id"'
```

---

## Verificar RabbitMQ Management Console

Acessar a console web para visualizar filas e mensagens.

```bash
# URL
http://localhost:15672

# Credenciais padrão
Username: guest
Password: guest

# Navegação:
# 1. Clique em "Queues and Streams"
# 2. Escolha uma fila (notificacoes, auditoria, relatorios)
# 3. Veja as mensagens sendo publicadas/consumidas em tempo real
```

---

## Dicas de Debugging

### Ver headers da resposta
```bash
# Linux/Mac
curl -i -X POST http://localhost:5000/alunos ...

# Windows PowerShell
$response = Invoke-WebRequest -Uri "..." -Method POST
$response.Headers | Format-Table
```

### Ver tempo de resposta
```bash
# Linux/Mac
curl -w "Tempo total: %{time_total}s\n" \
  -X POST http://localhost:5000/alunos ...

# Windows PowerShell
$start = Get-Date
Invoke-WebRequest -Uri "..." -Method POST
$elapsed = (Get-Date) - $start
Write-Host "Tempo: $elapsed"
```

### Ver logs completos
```bash
# Linux/Mac
curl -v http://localhost:5000/health

# Windows PowerShell
$ErrorActionPreference = "SilentlyContinue"
Invoke-WebRequest -Uri "http://localhost:5000/health" -Verbose
```

---

Bom teste! 🧪
