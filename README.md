# Skill de Auditoria e Refatoração Arquitetural

<!-- TOC -->

- [Skill de Auditoria e Refatoração Arquitetural](#skill-de-auditoria-e-refatoração-arquitetural)
  - [A) Análise Manual](#a-análise-manual)
    - [Projeto 1 — code-smells-project (Python/Flask — E-commerce API)](#projeto-1--code-smells-project-pythonflask--e-commerce-api)
    - [Projeto 2 — ecommerce-api-legacy (Node.js/Express — LMS API)](#projeto-2--ecommerce-api-legacy-nodejsexpress--lms-api)
    - [Projeto 3 — task-manager-api (Python/Flask — Task Manager)](#projeto-3--task-manager-api-pythonflask--task-manager)
  - [B) Construção da Skill](#b-construção-da-skill)
    - [Arquivos da Skill](#arquivos-da-skill)
    - [Decisões de Design](#decisões-de-design)
  - [C) Resultados](#c-resultados)
    - [Resumo dos Relatórios](#resumo-dos-relatórios)
    - [Comparação Antes/Depois](#comparação-antesdepois)
    - [Checklist de Validação](#checklist-de-validação)
      - [Fase 1](#fase-1)
      - [Fase 2](#fase-2)
      - [Fase 3](#fase-3)
    - [Logs de Validação](#logs-de-validação)
  - [D) Como Executar](#d-como-executar)
    - [Pré-requisitos](#pré-requisitos)
    - [Instalando dependências](#instalando-dependências)
    - [Executando a Skill em cada projeto](#executando-a-skill-em-cada-projeto)
    - [Rodando a aplicação refatorada](#rodando-a-aplicação-refatorada)
    - [Validando que a refatoração funcionou](#validando-que-a-refatoração-funcionou)
  - [Developer](#developer)
  - [License](#license)

<!-- TOC -->

Skill para Claude Code que analisa codebases, gera relatórios de auditoria de anti-patterns e refatora automaticamente para o padrão MVC — agnóstica de tecnologia (Python/Flask e Node.js/Express).

---

## A) Análise Manual

### Projeto 1 — code-smells-project (Python/Flask — E-commerce API)

| Severidade | Arquivo | Linha | Problema |
|-----------|---------|-------|---------|
| CRITICAL | models.py | 28, 48, 68, 93, 110, 127 | SQL Injection — concatenação de strings em todas as queries SQL |
| CRITICAL | app.py | 59–78 | Endpoint `/admin/query` executa SQL arbitrário sem autenticação |
| CRITICAL | app.py | 7 | `SECRET_KEY = "minha-chave-super-secreta-123"` hardcoded |
| CRITICAL | app.py | 47–57 | `/admin/reset-db` deleta todo o banco sem autenticação |
| HIGH | models.py | 79–86 | Campo `senha` retornado em texto plano nas respostas da API |
| HIGH | models.py | 105–120 | Login compara senha em texto plano (sem hash) |
| HIGH | models.py | 235–273 | Regras de desconto embutidas na camada de models |
| MEDIUM | models.py | 171–201 | N+1 queries: loop aninhado para buscar itens e produtos de cada pedido |
| MEDIUM | database.py | 76–83 | Senhas seed inseridas em texto plano |
| LOW | app.py | 8 | `DEBUG=True` hardcoded |
| LOW | controllers.py | 288–289 | Health endpoint expõe secret_key na resposta |
| LOW | controllers.py | múltiplos | `print()` para logging em vez de biblioteca de log estruturado |

**Justificativa:** SQL Injection em todas as queries permite exfiltração completa do banco. O endpoint `/admin/query` sem autenticação é uma porta aberta para qualquer atacante. Senhas em texto plano violam os princípios básicos de segurança.

---

### Projeto 2 — ecommerce-api-legacy (Node.js/Express — LMS API)

| Severidade | Arquivo | Linha | Problema |
|-----------|---------|-------|---------|
| CRITICAL | src/utils.js | 2–6 | Credenciais hardcoded: `dbPass`, `paymentGatewayKey` (`pk_live_...`), SMTP |
| CRITICAL | src/AppManager.js | 1–141 | God Class — DB init + routes + pagamento na mesma classe |
| CRITICAL | src/utils.js | 17–23 | `badCrypto()` usa base64 reversível como "hash" de senha |
| CRITICAL | src/AppManager.js | 18, 69 | Senhas gravadas como base64 reversível no banco |
| HIGH | src/AppManager.js | 28–78 | Callback hell 4 níveis — checkout inteiro em closures aninhados |
| HIGH | src/utils.js | 9–10 | Estado global mutável: `globalCache` e `totalRevenue` |
| HIGH | src/AppManager.js | 80–129 | `/api/admin/financial-report` sem autenticação |
| MEDIUM | src/AppManager.js | 80–128 | N+1 queries em cascata no relatório financeiro |
| MEDIUM | src/AppManager.js | 131–137 | DELETE de usuário deixa enrollments e payments órfãos |
| LOW | src/AppManager.js | 29–33 | Variáveis sem semântica: `u`, `e`, `p`, `cid`, `cc` |
| LOW | src/AppManager.js | 45–46 | Lógica de pagamento por dígito inicial do cartão (stub de teste em produção) |
| LOW | src/AppManager.js | 45 | `console.log` com número do cartão e chave do gateway (violação PCI-DSS) |

**Justificativa:** Chave `pk_live_...` hardcoded no código-fonte equivale a publicar as credenciais de produção. `badCrypto()` com base64 é reversível instantaneamente — não é criptografia. God Class impede qualquer tentativa de teste ou manutenção isolada.

---

### Projeto 3 — task-manager-api (Python/Flask — Task Manager)

| Severidade | Arquivo | Linha | Problema |
|-----------|---------|-------|---------|
| CRITICAL | app.py | 13 | `SECRET_KEY = 'super-secret-key-123'` hardcoded |
| HIGH | models/user.py | 29–32 | MD5 para hash de senhas — quebrado por rainbow tables |
| HIGH | routes/task_routes.py | 11–298 | Toda lógica de negócio nas rotas — sem camada de controllers |
| HIGH | models/user.py | 17–24 | `to_dict()` inclui campo `password` em todas as respostas |
| MEDIUM | 6 arquivos | múltiplos | Lógica de overdue duplicada 6 vezes (mesmo `Task.is_overdue()` existindo) |
| MEDIUM | routes/task_routes.py | 67, 118, 159 | API deprecated: `Model.query.get()` removida no SQLAlchemy 2.0 |
| MEDIUM | routes/task_routes.py | 63 e outros | `except:` bare — captura todo tipo de exceção |
| MEDIUM | services/ | todo | Camada services/ existe mas está vazia; controllers/ não existe |
| LOW | app.py | 12 | `SQLALCHEMY_TRACK_MODIFICATIONS` deprecated |
| LOW | routes/*.py | múltiplos | `print()` em vez de `logging` estruturado |
| LOW | routes/task_routes.py | 7 | Imports não utilizados: `json, os, sys, time` |

**Justificativa:** MD5 como hash de senha é inseguro desde os anos 90. A duplicação do bloco de overdue em 6 locais é uma bomba-relógio de manutenção. API deprecated vai quebrar na próxima versão do SQLAlchemy.

---

## B) Construção da Skill

### Arquivos da Skill

```
.claude/skills/refactor-arch/
├── SKILL.md                      ← prompt principal com fluxo das 3 fases
├── 01-project-analysis.md        ← heurísticas de detecção de stack
├── 02-antipatterns-catalog.md    ← 14 anti-patterns classificados (CRITICAL → LOW)
├── 03-audit-report-template.md   ← template exato do relatório de auditoria
├── 04-architecture-guidelines.md ← regras do padrão MVC alvo e invariantes de camada
└── 05-refactoring-playbook.md    ← 10 padrões de transformação com exemplos antes/depois
```

### Decisões de Design

**Por que 14 anti-patterns (mais que o mínimo de 8)?**
Os anti-patterns foram derivados dos problemas reais encontrados nos 3 projetos. Cada um tem sinais de detecção específicos por linguagem (Python e Node.js), não descrições genéricas.

**Como a skill é agnóstica de tecnologia:**
- `01-project-analysis.md` tem heurísticas separadas para Python/Flask, Django, Express, FastAPI
- `02-antipatterns-catalog.md` tem sinais de detecção em Python e Node.js para cada entry
- `04-architecture-guidelines.md` define a estrutura MVC para Python (`src/views/`) e Node.js (`src/routes/`)
- `05-refactoring-playbook.md` tem exemplos antes/depois em ambas as linguagens
- `SKILL.md` usa condicionais por linguagem nas instruções de migração da Fase 3

**Anti-patterns incluídos — razão de inclusão:**

| Anti-pattern | Razão |
|-------------|-------|
| AP-01 SQL Injection | Encontrado em 100% das queries do projeto 1 |
| AP-02 Hardcoded Credentials | Nos 3 projetos; chave `pk_live_` no projeto 2 |
| AP-03 God Class | AppManager.js — caso clássico e grave |
| AP-04 Unauthenticated Admin | `/admin/query` sem auth é CRITICAL |
| AP-05 Weak Password | MD5 / base64 / plaintext nos 3 projetos |
| AP-06 Business Logic in Routes | Problema mais frequente nos 3 projetos |
| AP-07 Mutable Global State | `globalCache` no projeto 2 |
| AP-08 Sensitive Data Exposure | Password em respostas nos projetos 2 e 3 |
| AP-09 N+1 Query | Loops aninhados nos projetos 1 e 2 |
| AP-10 Missing Input Validation | Checkout sem validação no projeto 2 |
| AP-11 Bare Except | Múltiplas rotas nos projetos 1 e 3 |
| AP-12 Deprecated API | `Model.query.get()` no projeto 3 — importante para SQLAlchemy 2.0 |
| AP-13 Magic Numbers | Thresholds de desconto no projeto 1 |
| AP-14 print() for Logging | Nos 3 projetos |

**Desafios encontrados:**
- Projeto 3 já tinha estrutura parcial — a Fase 3 foi escrita para detectar isso e "construir sobre" ao invés de recriar toda a estrutura
- Projeto 2 usa callbacks assíncronos — o playbook inclui transformação callback hell → async/await
- Detecção de deprecated APIs requer conhecimento de versão — adicionado no catálogo com sinais específicos de versão

---

## C) Resultados

### Resumo dos Relatórios

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---------|---------|------|--------|-----|-------|
| code-smells-project | 4 | 3 | 2 | 3 | **12** |
| ecommerce-api-legacy | 4 | 3 | 2 | 3 | **12** |
| task-manager-api | 1 | 3 | 4 | 3 | **11** |

### Comparação Antes/Depois

**code-smells-project:**
- Antes: 4 arquivos na raiz, SQL Injection em 12+ queries, secrets hardcoded, N+1 queries, senhas em plaintext
- Depois: `src/` com 5 camadas MVC, queries parametrizadas, bcrypt, JOIN único, secrets via `os.environ`

**ecommerce-api-legacy:**
- Antes: 1 God Class (141 linhas), callbacks 4 níveis, `badCrypto()` (base64), credentials hardcoded, admin sem auth
- Depois: 10 módulos MVC, async/await, bcrypt, `process.env`, `requireAdmin` middleware

**task-manager-api:**
- Antes: routes/ com 700+ linhas de lógica mista, overdue duplicado 6×, MD5, sem controllers, API deprecated
- Depois: routes/ com ~175 linhas de delegação pura, controllers/ centraliza lógica, bcrypt, `is_overdue()` usado 1× no controller, `db.session.get()` substitui deprecated

### Checklist de Validação

#### Fase 1

| Critério | Projeto 1 | Projeto 2 | Projeto 3 |
|---------|-----------|-----------|-----------|
| Linguagem detectada | ✓ Python | ✓ JavaScript | ✓ Python |
| Framework detectado | ✓ Flask 3.1.1 | ✓ Express 4.18.2 | ✓ Flask 3.0.0 + SQLAlchemy |
| Domínio descrito | ✓ E-commerce | ✓ LMS | ✓ Task Manager |
| Nº arquivos condiz | ✓ 4 | ✓ 3 | ✓ 10 |

#### Fase 2

| Critério | Projeto 1 | Projeto 2 | Projeto 3 |
|---------|-----------|-----------|-----------|
| Relatório segue template | ✓ | ✓ | ✓ |
| Arquivo e linhas exatos | ✓ | ✓ | ✓ |
| Ordenado por severidade | ✓ | ✓ | ✓ |
| ≥ 5 findings | ✓ 12 | ✓ 12 | ✓ 11 |
| ≥ 1 CRITICAL ou HIGH | ✓ 4 CRITICAL | ✓ 4 CRITICAL | ✓ 1C + 3H |
| APIs deprecated detectadas | — | — | ✓ |
| Pausa antes da Fase 3 | ✓ | ✓ | ✓ |

#### Fase 3

| Critério | Projeto 1 | Projeto 2 | Projeto 3 |
|---------|-----------|-----------|-----------|
| Estrutura MVC criada | ✓ | ✓ | ✓ |
| Config sem hardcoded | ✓ `os.environ` | ✓ `process.env` | ✓ `os.environ` |
| Models sem lógica de negócio | ✓ | ✓ | ✓ |
| Controllers orquestram | ✓ | ✓ | ✓ |
| Routes só delegam | ✓ | ✓ | ✓ |
| Error handler centralizado | ✓ | ✓ | ✓ |
| Aplicação inicia sem erros | ✓ | ⚠ Node.js ausente no env | ✓ |
| Endpoints respondem | ✓ | ⚠ Node.js ausente no env | ✓ |

### Logs de Validação

**Projeto 1:**
```
$ SECRET_KEY=segura python src/app.py
 * Running on http://0.0.0.0:5000

GET /health  → 200 {"counts":{"pedidos":0,"produtos":10,"usuarios":3},...}
GET /produtos → 200 sucesso: True, 10 produtos
GET /usuarios → 200 sucesso: True, 3 usuários (sem campo 'senha')
POST /login  → 200 sucesso: True
```

**Projeto 3:**
```
$ python app.py
 * Running on http://0.0.0.0:5000

GET /health  → 200 {"status":"ok","timestamp":"2026-06-15 00:19:02"}
POST /users  → 201 {"id":1,"name":"Test User","email":"test@test.com",...}
             (campo 'password' ausente — vulnerabilidade corrigida)
INFO:controllers.task_controller:Task criada: 1 — My first task
             (logging estruturado com nível, módulo e mensagem)
```

---

## D) Como Executar

### Pré-requisitos

- Python 3.9+ com pip (projetos 1 e 3)
- Node.js 18+ com npm (projeto 2)
- Claude Code instalado e autenticado

### Instalando dependências

```bash
# Projeto 1
cd code-smells-project
pip install -r requirements.txt

# Projeto 2
cd ../ecommerce-api-legacy
npm install

# Projeto 3
cd ../task-manager-api
pip install -r requirements.txt
```

### Executando a Skill em cada projeto

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

A skill executa as 3 fases interativamente:
1. **Fase 1** — Detecta stack e imprime resumo (sem modificar arquivos)
2. **Fase 2** — Gera relatório de auditoria e **aguarda confirmação** `[y/n]`
3. **Fase 3** — Refatora para MVC e valida que a aplicação funciona

### Rodando a aplicação refatorada

**Projeto 1:**
```bash
cd code-smells-project
SECRET_KEY=minha-chave-segura python src/app.py
curl http://localhost:5000/health
curl http://localhost:5000/produtos
```

**Projeto 2:**
```bash
cd ecommerce-api-legacy
PAYMENT_KEY=pk_test_... ADMIN_KEY=minha-chave npm start
curl http://localhost:3000/health
curl -H 'x-admin-key: minha-chave' http://localhost:3000/api/admin/financial-report
```

**Projeto 3:**
```bash
cd task-manager-api
SECRET_KEY=minha-chave-segura python app.py
curl http://localhost:5000/health
curl http://localhost:5000/tasks
```

### Validando que a refatoração funcionou

```bash
# Sem secrets hardcoded no código
grep -rn "SECRET_KEY\s*=\s*['\"]" src/    # deve retornar vazio

# Sem SQL por concatenação
grep -rn '+ str(' src/models/              # deve retornar vazio (projeto 1)

# Sem campo senha na resposta
curl http://localhost:5000/usuarios | grep senha  # deve retornar vazio

# Relatórios de auditoria gerados
ls reports/
# audit-project-1.md  audit-project-2.md  audit-project-3.md
```

## Developer

Aecio dos Santos Pires
- Linkedin: https://www.linkedin.com/in/aeciopires/
- Site: http://aeciopires.com/

## License

MIT License
