================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python 3.x
Framework:     Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
Dependencies:  flask-cors 4.0.0, marshmallow, python-dotenv
Domain:        Task Manager API — tasks, users, categories, reports
Architecture:  Parcialmente Organizada — models/ e routes/ existem, mas sem camada de controllers;
               toda lógica de negócio está nas rotas; services/ existe mas está vazio
Source files:  10 files analyzed (app.py, database.py, models/*.py, routes/*.py,
               services/notification_service.py, utils/helpers.py)
DB tables:     tasks, users, categories (via SQLAlchemy ORM)
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 + SQLAlchemy 3.1.1
Files:   10 analyzed | ~600 lines of code

Summary
CRITICAL: 1 | HIGH: 3 | MEDIUM: 4 | LOW: 3

Findings

---

[CRITICAL] Hardcoded Secret Key
File: app.py:13
Description: SECRET_KEY hardcoded diretamente no código-fonte:
             app.config['SECRET_KEY'] = 'super-secret-key-123'
Impact: Token de sessão pode ser forjado por qualquer pessoa com acesso ao repositório.
Recommendation: Aplicar T-02 — carregar de os.environ.get("SECRET_KEY").

[HIGH] Weak Password Hashing (MD5)
File: models/user.py:29-32
Description: Senhas armazenadas com MD5:
             self.password = hashlib.md5(pwd.encode()).hexdigest()
             return self.password == hashlib.md5(pwd.encode()).hexdigest()
Impact: MD5 é reversível via rainbow tables; banco comprometido expõe todas as senhas em segundos.
Recommendation: Aplicar T-05 — substituir por bcrypt.hashpw() / bcrypt.checkpw().

[HIGH] Business Logic in Route Handlers (No Controllers Layer)
File: routes/task_routes.py:11-298 e routes/user_routes.py:10-211 e routes/report_routes.py:12-155
Description: Rotas contêm validação de campos, queries ao banco, cálculos de overdue e lógica de negócio.
             Exemplo em task_routes.py:43-53 (validação de overdue inline no handler):
             if t.due_date < datetime.utcnow():
                 if t.status != 'done' and t.status != 'cancelled':
                     task_data['overdue'] = True
Impact: Impossível testar lógica de negócio sem instanciar o contexto HTTP; viola MVC.
Recommendation: Aplicar T-04 — criar controllers/task_controller.py, user_controller.py, report_controller.py.

[HIGH] Sensitive Data Exposed in API Response
File: models/user.py:17-24
Description: to_dict() inclui o campo 'password' na serialização:
             'password': self.password,
Impact: Hash de senha retornado em toda resposta que usa to_dict() (GET /users, GET /users/:id, POST /users, login).
Recommendation: Remover 'password' de to_dict(); manter o campo apenas na lógica de autenticação.

[MEDIUM] Duplicated Overdue Logic (DRY Violation)
File: routes/task_routes.py:30-39, routes/task_routes.py:71-80, routes/task_routes.py:282-286,
      routes/user_routes.py:171-180, routes/report_routes.py:33-43, routes/report_routes.py:132-135
Description: Bloco de cálculo de overdue duplicado 6 vezes em diferentes arquivos:
             if t.due_date < datetime.utcnow():
                 if t.status != 'done' and t.status != 'cancelled': ...
             Nota: Task model já possui método is_overdue() que implementa esta lógica corretamente.
Impact: Qualquer mudança na regra de overdue exige atualização em 6 lugares; risco alto de inconsistência.
Recommendation: Usar t.is_overdue() (já existe em models/task.py:50) em todos os lugares.

[MEDIUM] Deprecated SQLAlchemy API
File: routes/task_routes.py:67, routes/task_routes.py:118, routes/task_routes.py:159,
      routes/user_routes.py:29, routes/user_routes.py:95, routes/report_routes.py:105, routes/report_routes.py:192
Description: Model.query.get(id) está deprecated no SQLAlchemy 2.0:
             task = Task.query.get(task_id)
             user = User.query.get(user_id)
Impact: Código quebrará na migração para SQLAlchemy 2.0+; deprecation warnings no log.
Recommendation: Substituir por db.session.get(Task, task_id) conforme guia de migração SQLAlchemy 2.0.

[MEDIUM] Bare Except Clauses
File: routes/task_routes.py:63, routes/report_routes.py:187, routes/report_routes.py:208, routes/report_routes.py:221
Description: Blocos except sem tipo de exceção especificado:
             except:
                 return jsonify({'error': 'Erro interno'}), 500
Impact: Captura KeyboardInterrupt, SystemExit e outros sinais não-recuperáveis; oculta bugs.
Recommendation: Usar except Exception as e: e registrar o erro com logger.exception().

[MEDIUM] Empty Services Layer
File: services/__init__.py e services/notification_service.py
Description: Diretório services/ existe mas está completamente vazio; controllers/ não existe.
             Serviços de notificação simulados com print() nos controllers das rotas originais.
Impact: Estrutura incompleta engana sobre a real separação de camadas do projeto.
Recommendation: Implementar services/ com lógica de notificação; criar camada controllers/ ausente.

[LOW] Deprecated SQLALCHEMY_TRACK_MODIFICATIONS Setting
File: app.py:12
Description: Configuração deprecated ainda presente:
             app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Impact: Aviso de deprecação no log; removida no Flask-SQLAlchemy 3.x.
Recommendation: Remover esta linha.

[LOW] print() Used for Logging
File: routes/task_routes.py:149, routes/task_routes.py:219, routes/task_routes.py:234,
      routes/user_routes.py:83, routes/user_routes.py:89, routes/user_routes.py:147
Description: print() utilizado para logging nos handlers de rota:
             print(f"Task criada: {task.id} - {task.title}")
Impact: Sem níveis de severidade, timestamps estruturados ou configuração de destino.
Recommendation: Substituir por logging.getLogger(__name__).info(...).

[LOW] Unused Imports
File: routes/task_routes.py:7, routes/user_routes.py:6, routes/report_routes.py:8
Description: Imports não utilizados em múltiplas rotas:
             import json, os, sys, time  (task_routes.py — nenhum utilizado)
             import hashlib, json, re    (user_routes.py — hashlib e json não utilizados)
             import json                 (report_routes.py — não utilizado)
Impact: Código morto; possível confusão sobre o que está em uso.
Recommendation: Remover imports não utilizados.

---

================================
Total: 11 findings
CRITICAL: 1 | HIGH: 3 | MEDIUM: 4 | LOW: 3
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y

================================
PHASE 3: REFACTORING COMPLETE
================================
Estrutura mantida e expandida (projeto já tinha models/ e routes/):

task-manager-api/
├── config/                    ← NOVO
│   └── settings.py            ← SECRET_KEY, DATABASE_URI, DEBUG via os.environ
├── controllers/               ← NOVO (camada ausente criada)
│   ├── task_controller.py     ← toda lógica de tasks; usa t.is_overdue() centralizado
│   ├── user_controller.py     ← toda lógica de usuários; bcrypt
│   └── report_controller.py   ← relatórios sem lógica duplicada
├── middlewares/               ← NOVO
│   └── error_handler.py       ← handler centralizado registrado em app.py
├── models/                    ← MANTIDO + corrigido
│   ├── task.py                ← inalterado (is_overdue() já existia e é agora usado)
│   ├── user.py                ← bcrypt substitui MD5; campo password removido de to_dict()
│   └── category.py            ← inalterado
├── routes/                    ← REESCRITO (handlers slim — apenas delegam ao controller)
│   ├── task_routes.py         ← 50 linhas (antes: 298 linhas com lógica embutida)
│   ├── user_routes.py         ← 55 linhas (antes: 212 linhas)
│   └── report_routes.py       ← 70 linhas (antes: 224 linhas)
├── services/                  ← MANTIDO (notification_service.py presente para evolução futura)
├── utils/helpers.py            ← inalterado
├── database.py                ← inalterado
└── app.py                     ← atualizado: usa config/settings.py, sem TRACK_MODIFICATIONS

Validation
  ✓ Application boots without errors
  ✓ GET /health → 200 {"status":"ok","timestamp":"..."}
  ✓ GET /tasks → 200 [] (lista vazia)
  ✓ GET /users → 200 [] (lista vazia, sem campo password)
  ✓ POST /users → 201 {"id":1,"name":"Test User","email":"test@test.com",...} (sem password)
  ✓ POST /tasks → 201 {"id":1,"title":"My first task",...}
  ✓ Logging estruturado: "INFO:controllers.task_controller:Task criada: 1 — My first task"
  ✓ is_overdue() centralizado — sem duplicação nas 6 localizações anteriores
  ✓ db.session.get() substitui deprecated Model.query.get() em todos os controllers
  ✓ bcrypt substitui MD5 nas senhas
  ✓ SECRET_KEY lida de os.environ
  ✓ SQLALCHEMY_TRACK_MODIFICATIONS removida
  ✓ Imports desnecessários removidos das rotas
================================
