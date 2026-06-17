# Plano de Implementação — Skill de Auditoria e Refatoração Arquitetural

## Visão Geral

Criar uma Claude Code Skill (`/refactor-arch`) que executa 3 fases sequenciais — Análise, Auditoria e Refatoração — de forma agnóstica de tecnologia, validada nos 3 projetos fornecidos.

---

## Fase 0 — Análise Manual dos Projetos

Antes de criar a skill, documentar os problemas de cada projeto para embasar o catálogo de anti-patterns.

### Projeto 1 — code-smells-project (Python/Flask)

| # | Severidade | Arquivo | Linha | Problema |
|---|-----------|---------|-------|---------|
| 1 | CRITICAL | models.py | 28, 48, 68, 93, 110, 127, 140, 150, 174, 280, 289 | SQL Injection — concatenação de strings em todas as queries |
| 2 | CRITICAL | app.py | 59–78 | Endpoint `/admin/query` executa SQL arbitrário sem autenticação |
| 3 | CRITICAL | app.py | 7 | Credencial hardcoded: `SECRET_KEY = "minha-chave-super-secreta-123"` |
| 4 | CRITICAL | app.py | 47–57 | Endpoint `/admin/reset-db` sem autenticação deleta todo o banco |
| 5 | HIGH | models.py | 79–86 | Senha retornada em texto plano nas respostas da API |
| 6 | HIGH | models.py | 105–120 | Login compara senha em texto plano (sem hashing) |
| 7 | HIGH | models.py | 171–233 | N+1 queries: para cada pedido abre 2 loops de queries aninhados |
| 8 | HIGH | models.py | 235–273 | Lógica de negócio (cálculo de desconto) no arquivo de models |
| 9 | MEDIUM | controllers.py | todo | Ausência de validação de entrada nas rotas POST/PUT |
| 10 | MEDIUM | models.py | todo | Nenhum tratamento de erro nas operações de banco de dados |
| 11 | LOW | models.py | 257–260 | Magic numbers (10000, 5000, 1000, 0.1, 0.05, 0.02) sem constantes |
| 12 | LOW | app.py | 8 | `DEBUG=True` hardcoded — expõe stack traces em produção |

### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

| # | Severidade | Arquivo | Linha | Problema |
|---|-----------|---------|-------|---------|
| 1 | CRITICAL | utils.js | 1–7 | Credenciais hardcoded: senha do DB, chave de pagamento, SMTP |
| 2 | CRITICAL | AppManager.js | 1–141 | God Class — inicializa banco, define rotas e processa pagamentos |
| 3 | CRITICAL | utils.js | 17–23 | `badCrypto()` usa base64 reversível como hash de senha |
| 4 | CRITICAL | AppManager.js | 18, 69 | Senhas gravadas como base64 reversível no banco |
| 5 | HIGH | AppManager.js | 28–78 | Callback hell 4 níveis — lógica de negócio embutida em closures |
| 6 | HIGH | utils.js | 9–10 | Estado global mutável: `globalCache` e `totalRevenue` sem proteção |
| 7 | HIGH | AppManager.js | 80–129 | `/api/admin/financial-report` sem nenhuma autenticação |
| 8 | HIGH | AppManager.js | 80–128 | N+1 queries em cascata no relatório financeiro |
| 9 | MEDIUM | AppManager.js | 131–137 | DELETE de usuário deixa enrollments e payments órfãos |
| 10 | MEDIUM | AppManager.js | 45–46 | Lógica de pagamento baseada em dígito inicial do cartão (stub de teste em produção) |
| 11 | LOW | AppManager.js | 29–33 | Nomes de variáveis sem semântica: `u`, `e`, `p`, `cid`, `cc` |
| 12 | LOW | AppManager.js | todo | Nenhuma validação de formato dos campos no checkout |

### Projeto 3 — task-manager-api (Python/Flask)

| # | Severidade | Arquivo | Linha | Problema |
|---|-----------|---------|-------|---------|
| 1 | HIGH | app.py | 13 | Credencial hardcoded: `SECRET_KEY = 'super-secret-key-123'` |
| 2 | HIGH | routes/task_routes.py | 11–298 | Toda lógica de negócio na camada de rotas — sem controllers |
| 3 | HIGH | routes/task_routes.py | 30–39, 71–80, 282–286 | Lógica de "overdue" duplicada em 3 lugares diferentes |
| 4 | MEDIUM | routes/task_routes.py | 7 | Imports não utilizados: `json`, `os`, `sys`, `time` |
| 5 | MEDIUM | routes/task_routes.py | 63 | `except:` bare — captura todo tipo de exceção incluindo KeyboardInterrupt |
| 6 | MEDIUM | services/ | todo | Camada de services existe mas está vazia — não é usada nas rotas |
| 7 | LOW | routes/task_routes.py | 67, 118, 159 | API deprecated: `Task.query.get()` removida no SQLAlchemy 2.0 |
| 8 | LOW | routes/task_routes.py | 149, 219, 234 | `print()` para logging — sem níveis de severidade ou destino configurável |
| 9 | LOW | app.py | 12 | `SQLALCHEMY_TRACK_MODIFICATIONS = False` é configuração deprecated |

---

## Fase 1 — Criação da Skill

### Estrutura de Arquivos a Criar

```
code-smells-project/
└── .claude/
    └── skills/
        └── refactor-arch/
            ├── SKILL.md                      ← prompt principal (instrução ao agente)
            ├── 01-project-analysis.md        ← heurísticas de detecção de stack
            ├── 02-antipatterns-catalog.md    ← catálogo com ≥8 anti-patterns
            ├── 03-audit-report-template.md   ← template do relatório de auditoria
            ├── 04-architecture-guidelines.md ← regras do padrão MVC alvo
            └── 05-refactoring-playbook.md    ← ≥8 padrões de transformação com antes/depois
```

### 1.1 — SKILL.md

Arquivo de instrução principal. Define o fluxo das 3 fases:

**Fase 1 — Análise (sem modificar arquivos)**
- Detectar linguagem, framework, versão, dependências
- Mapear arquivos fonte, contar linhas, identificar entidades de domínio
- Identificar banco de dados e tabelas
- Imprimir o resumo formatado (bloco `PROJECT ANALYSIS`)

**Fase 2 — Auditoria**
- Cruzar o código contra `02-antipatterns-catalog.md`
- Gerar relatório seguindo `03-audit-report-template.md`
- Cada finding deve ter arquivo + linha exata + severidade
- Ordenar findings por severidade: CRITICAL → HIGH → MEDIUM → LOW
- **PAUSAR e pedir confirmação do usuário antes de prosseguir**

**Fase 3 — Refatoração (somente após confirmação)**
- Reestruturar para MVC seguindo `04-architecture-guidelines.md`
- Aplicar transformações de `05-refactoring-playbook.md`
- Criar estrutura de diretórios: `src/config/`, `src/models/`, `src/views/`, `src/controllers/`, `src/middlewares/`
- Validar: iniciar a aplicação e testar endpoints originais

### 1.2 — 01-project-analysis.md

Heurísticas de detecção por linguagem/framework:

- **Python/Flask**: `app.py`, `requirements.txt` com `flask`, decoradores `@app.route`
- **Python/Django**: `manage.py`, `settings.py`, `INSTALLED_APPS`
- **Node.js/Express**: `package.json` com `express`, `app.use()`, `app.get/post`
- **Java/Spring**: `pom.xml` com `spring-boot`, `@SpringBootApplication`
- Detecção de banco: `sqlite3`, `psycopg2`, `mysql-connector`, `mongoose`
- Mapeamento de domínio: extrair nomes de tabelas/modelos, rotas principais
- Contagem de arquivos e linhas
- Identificação da arquitetura atual (monolítica, parcialmente organizada, MVC)

### 1.3 — 02-antipatterns-catalog.md

Catálogo com ≥8 anti-patterns (distribuição obrigatória: CRITICAL/HIGH/MEDIUM/LOW):

| # | Anti-pattern | Severidade | Sinal de detecção |
|---|-------------|-----------|------------------|
| 1 | SQL Injection | CRITICAL | `"SELECT " + var`, `f"WHERE id = {id}"`, concatenação de strings em queries |
| 2 | Hardcoded Credentials | CRITICAL | `SECRET_KEY = "..."`, `password = "..."`, `api_key = "pk_live_..."` no código fonte |
| 3 | God Class | CRITICAL | Arquivo único com >3 responsabilidades (DB, rotas, lógica, auth) |
| 4 | Unauthenticated Admin Endpoint | CRITICAL | Rota `/admin/...` sem middleware de autenticação |
| 5 | Plaintext/Weak Password Storage | HIGH | `senha = md5(pwd)`, base64 como hash, comparação direta de senha |
| 6 | Business Logic in Routes/Views | HIGH | Queries SQL ou cálculos complexos dentro de `@app.route` ou `app.get()` |
| 7 | Mutable Global State | HIGH | Variáveis globais modificadas em handlers de requisição |
| 8 | N+1 Query Problem | MEDIUM | Query dentro de loop `for`, callbacks aninhados para buscar dados relacionados |
| 9 | Missing Input Validation | MEDIUM | Ausência de checagem de tipos, limites ou formatos em entradas do usuário |
| 10 | Bare Except / Swallowed Errors | MEDIUM | `except:` sem tipo, ou `catch(err) {}` sem tratamento |
| 11 | Deprecated API Usage | MEDIUM | `Model.query.get()` (SQLAlchemy 2.0), `app.use(bodyParser)` (Express 4.16+) |
| 12 | Magic Numbers | LOW | Literais numéricos sem constantes nomeadas (ex: `0.1`, `10000`, `5000`) |
| 13 | Debug Mode in Production | LOW | `DEBUG=True`, `app.run(debug=True)` sem verificação de ambiente |
| 14 | print() for Logging | LOW | `print()` em handlers de rotas em vez de biblioteca de log estruturado |

### 1.4 — 03-audit-report-template.md

Template do relatório de auditoria a ser gerado na Fase 2:

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome>
Stack:   <Linguagem> + <Framework>
Files:   <N> analyzed | ~<LOC> lines of code

Summary
CRITICAL: N | HIGH: N | MEDIUM: N | LOW: N

Findings

[SEVERITY] Anti-pattern Name
File: path/to/file.py:line-range
Description: O que foi encontrado e por quê é um problema.
Impact: Consequência prática deste problema.
Recommendation: Como corrigir.

...

================================
Total: N findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

### 1.5 — 04-architecture-guidelines.md

Regras do padrão MVC alvo para Python/Flask e Node.js/Express:

**Estrutura de diretórios alvo:**
```
src/
├── config/
│   └── settings.py / settings.js     ← configurações via variáveis de ambiente
├── models/
│   └── <entity>_model.py / .js       ← apenas acesso a dados, sem lógica de negócio
├── controllers/
│   └── <entity>_controller.py / .js  ← orquestra models, valida, retorna resposta
├── views/ (ou routes/)
│   └── <entity>_routes.py / .js      ← apenas define rotas e delega ao controller
├── middlewares/
│   └── error_handler.py / .js        ← tratamento centralizado de erros
└── app.py / app.js                   ← composition root, sem lógica
```

**Invariantes de camada:**
- `models/`: nenhuma referência a `request` ou `response`
- `controllers/`: nenhuma query SQL direta — usa funções de model
- `views/routes/`: nenhuma lógica de negócio — apenas delega ao controller
- `config/`: todas as configs lidas de `os.environ` / `process.env`

### 1.6 — 05-refactoring-playbook.md

Playbook com ≥8 padrões de transformação (antes/depois):

| # | Transformação | Anti-pattern alvo |
|---|--------------|------------------|
| 1 | Parametrized Queries | SQL Injection |
| 2 | Environment Variables for Secrets | Hardcoded Credentials |
| 3 | God Class Decomposition | God Class |
| 4 | Extract Controller from Route | Business Logic in Routes |
| 5 | Password Hashing (bcrypt) | Plaintext Password Storage |
| 6 | Batch Query / JOIN | N+1 Query Problem |
| 7 | Centralized Error Handler | Bare Except / Swallowed Errors |
| 8 | Remove Mutable Global State | Mutable Global State |
| 9 | Authentication Middleware | Unauthenticated Admin Endpoint |
| 10 | Named Constants | Magic Numbers |

Cada entrada terá exemplo de código antes (Python ou JS) e depois da transformação.

---

## Fase 2 — Execução da Skill nos 3 Projetos

### 2.1 — Projeto 1: code-smells-project

```bash
cd code-smells-project
claude "/refactor-arch"
```

**Checklist de validação:**
- [ ] Fase 1 detecta: Python, Flask, SQLite, domínio E-commerce, 4 arquivos
- [ ] Fase 2 encontra ≥5 findings (esperado: ≥10), incluindo SQL Injection e Hardcoded Credentials
- [ ] Skill pausa antes da Fase 3
- [ ] Fase 3 cria estrutura MVC em `src/`
- [ ] `python src/app.py` inicia sem erros
- [ ] Endpoints `/produtos`, `/usuarios`, `/pedidos`, `/health` respondem
- [ ] Salvar relatório em `reports/audit-project-1.md`
- [ ] Commitar código refatorado

**Estrutura MVC esperada após refatoração:**
```
src/
├── config/settings.py          ← SECRET_KEY via env var
├── models/
│   ├── produto_model.py        ← queries parametrizadas
│   ├── usuario_model.py        ← senha hasheada com bcrypt
│   └── pedido_model.py
├── controllers/
│   ├── produto_controller.py
│   ├── usuario_controller.py
│   └── pedido_controller.py
├── views/
│   └── routes.py
├── middlewares/
│   └── error_handler.py
└── app.py
```

### 2.2 — Projeto 2: ecommerce-api-legacy

```bash
cd ../ecommerce-api-legacy
# Copiar skill do projeto 1
cp -r ../code-smells-project/.claude/skills/refactor-arch/ .claude/skills/refactor-arch/
claude "/refactor-arch"
```

**Checklist de validação:**
- [ ] Fase 1 detecta: JavaScript/Node.js, Express, SQLite in-memory, domínio LMS
- [ ] Fase 2 encontra ≥5 findings, incluindo God Class e Hardcoded Credentials
- [ ] Skill pausa antes da Fase 3
- [ ] Fase 3 decompõe `AppManager.js` em models/controllers/routes
- [ ] `node src/app.js` inicia sem erros
- [ ] Endpoints `/api/checkout`, `/api/admin/financial-report` respondem
- [ ] Salvar relatório em `reports/audit-project-2.md`
- [ ] Commitar código refatorado

**Estrutura MVC esperada após refatoração:**
```
src/
├── config/settings.js
├── models/
│   ├── userModel.js
│   ├── courseModel.js
│   └── enrollmentModel.js
├── controllers/
│   ├── checkoutController.js
│   └── reportController.js
├── routes/
│   └── api.js
├── middlewares/
│   └── errorHandler.js
└── app.js
```

### 2.3 — Projeto 3: task-manager-api

```bash
cd ../task-manager-api
cp -r ../code-smells-project/.claude/skills/refactor-arch/ .claude/skills/refactor-arch/
claude "/refactor-arch"
```

**Checklist de validação:**
- [ ] Fase 1 detecta: Python, Flask, SQLite/SQLAlchemy, domínio Task Manager
- [ ] Fase 1 detecta que projeto tem estrutura parcial (models/, routes/, services/ existem)
- [ ] Fase 2 encontra ≥5 findings, incluindo ausência de controllers e overdue duplicado
- [ ] Fase 2 detecta API deprecated (`Task.query.get()`)
- [ ] Skill pausa antes da Fase 3
- [ ] Fase 3 adiciona camada de controllers sem quebrar models existentes
- [ ] `python app.py` inicia sem erros
- [ ] Endpoints `/tasks`, `/users` respondem
- [ ] Salvar relatório em `reports/audit-project-3.md`
- [ ] Commitar código refatorado

**Estrutura MVC esperada após refatoração:**
```
src/
├── config/settings.py
├── models/                     ← mantém models existentes, migra para SQLAlchemy 2.0
│   ├── task.py
│   ├── user.py
│   └── category.py
├── controllers/                ← NOVO: extrai lógica das rotas
│   ├── task_controller.py      ← overdue centralizado aqui
│   └── user_controller.py
├── routes/                     ← só delega ao controller
│   ├── task_routes.py
│   └── user_routes.py
├── services/                   ← implementar serviços existentes vazios
│   └── notification_service.py
├── middlewares/
│   └── error_handler.py
└── app.py
```

---

## Fase 3 — Entregáveis

### Arquivos a criar

| Arquivo | Descrição |
|---------|-----------|
| `code-smells-project/.claude/skills/refactor-arch/SKILL.md` | Prompt principal da skill |
| `code-smells-project/.claude/skills/refactor-arch/01-project-analysis.md` | Heurísticas de detecção de stack |
| `code-smells-project/.claude/skills/refactor-arch/02-antipatterns-catalog.md` | Catálogo de anti-patterns (≥8) |
| `code-smells-project/.claude/skills/refactor-arch/03-audit-report-template.md` | Template do relatório |
| `code-smells-project/.claude/skills/refactor-arch/04-architecture-guidelines.md` | Regras do padrão MVC |
| `code-smells-project/.claude/skills/refactor-arch/05-refactoring-playbook.md` | Playbook de transformações (≥8) |
| `reports/audit-project-1.md` | Relatório de auditoria do projeto 1 |
| `reports/audit-project-2.md` | Relatório de auditoria do projeto 2 |
| `reports/audit-project-3.md` | Relatório de auditoria do projeto 3 |
| `README.md` | Documentação com seções A, B, C, D |

### Código refatorado (resultado da Fase 3)

- `code-smells-project/src/` — estrutura MVC completa
- `ecommerce-api-legacy/src/` — estrutura MVC completa (decomposta do AppManager.js)
- `task-manager-api/src/` (ou reorganizado) — controllers adicionados

---

## Ordem de Execução

```
1. [x] Ler TASK.md
2. [x] Analisar código dos 3 projetos (PLAN.md documenta os achados)
3. [x] Criar os 5 arquivos de referência da skill
4. [x] Criar SKILL.md
5. [x] Executar skill no projeto 1 (code-smells-project)
6. [x] Salvar relatório project-1, commitar
7. [x] Copiar skill para projeto 2, executar, salvar relatório, commitar
8. [x] Copiar skill para projeto 3, executar, salvar relatório, commitar
9. [x] Escrever README.md com seções A, B, C, D
10. [x] Commitar tudo
```

---

## Critérios de Aceite (checklist final)

### Skill
- [x] Catálogo tem ≥8 anti-patterns com distribuição de severidade (14 anti-patterns: 4 CRITICAL, 4 HIGH, 3 MEDIUM, 3 LOW)
- [x] Catálogo inclui detecção de APIs deprecated (Deprecated API — `Model.query.get()`, `bodyParser`)
- [x] Playbook tem ≥8 padrões com exemplos antes/depois (10 transformações T-01 a T-10)
- [x] Skill é agnóstica de tecnologia (Python e Node.js — exemplos em ambas as linguagens em cada arquivo)
- [x] Fase 2 pausa obrigatoriamente antes de qualquer modificação (imprime `[y/n]` e aguarda confirmação)

### Fase 1 (cada projeto)
- [x] Linguagem detectada corretamente (Python proj 1 e 3, Node.js proj 2)
- [x] Framework detectado corretamente (Flask proj 1 e 3, Express proj 2)
- [x] Domínio da aplicação descrito (E-commerce, LMS, Task Manager)
- [x] Número de arquivos condiz com a realidade (4, 3, 10 arquivos analisados respectivamente)

### Fase 2 (cada projeto)
- [x] Relatório segue o template definido (reports/audit-project-{1,2,3}.md)
- [x] Cada finding tem arquivo e linhas exatas
- [x] Findings ordenados por severidade (CRITICAL → HIGH → MEDIUM → LOW)
- [x] Mínimo de 5 findings por projeto (12, 12, 11 findings)
- [x] Pelo menos 1 CRITICAL ou HIGH por projeto (4, 4, 1 CRITICAL respectivamente)
- [x] APIs deprecated detectadas (projeto 3 — `Model.query.get()` marcado como MEDIUM)

### Fase 3 (cada projeto)
- [x] Estrutura MVC criada (src/config, src/models, src/controllers, src/views ou routes/, src/middlewares)
- [x] Config extraída para módulo (SECRET_KEY, DATABASE_PATH via os.environ / process.env)
- [x] Models sem lógica de negócio (queries parametrizadas, sem lógica de desconto ou cálculos)
- [x] Controllers orquestram o fluxo (pedido_controller, checkoutController, task_controller)
- [x] Views/Routes apenas delegam (handlers reduzidos para try/catch → next(err) ou 3 linhas)
- [x] Error handling centralizado (middlewares/error_handler.py e middlewares/auth.py em cada projeto)
- [x] Aplicação inicia sem erros (validado com `python src/app.py` e `python app.py`)
- [x] Endpoints originais respondem corretamente (GET /produtos, /checkout, /tasks validados)
