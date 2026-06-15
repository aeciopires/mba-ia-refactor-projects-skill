================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python 3.x
Framework:     Flask 3.1.1
Dependencies:  flask-cors 5.0.1, sqlite3 (stdlib)
Domain:        E-commerce API — produtos, pedidos, usuários, relatórios de vendas
Architecture:  Monolítica — 4 arquivos na raiz sem separação de camadas real
Source files:  4 files analyzed (app.py, models.py, controllers.py, database.py)
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~550 lines of code

Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 2 | LOW: 3

Findings

---

[CRITICAL] SQL Injection
File: models.py:28
Description: Query construída por concatenação de string sem parâmetros:
             cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
Impact: Qualquer valor de id pode injetar SQL arbitrário, permitindo leitura ou deleção de todos os dados.
Recommendation: Aplicar T-01 — usar cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))

[CRITICAL] SQL Injection
File: models.py:47-50
Description: INSERT com concatenação de strings em 4 campos:
             "INSERT INTO produtos ... VALUES ('" + nome + "', '" + descricao + "', ..."
Impact: Um atacante pode encerrar o INSERT e executar queries adicionais (SQLi clássico).
Recommendation: Aplicar T-01 — substituir por cursor.execute com tuple de parâmetros.

[CRITICAL] Hardcoded Credentials
File: app.py:7
Description: Chave secreta hardcoded no código-fonte:
             app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
Impact: Qualquer pessoa com acesso ao repositório conhece a chave; tokens JWT/sessão tornam-se forjáveis.
Recommendation: Aplicar T-02 — carregar de os.environ.get("SECRET_KEY").

[CRITICAL] Unauthenticated Admin Endpoint
File: app.py:59-78
Description: Rota /admin/query executa SQL arbitrário enviado pelo cliente sem nenhuma autenticação:
             cursor.execute(query)  # query vem diretamente de request.get_json()["sql"]
Impact: Qualquer cliente pode ler, modificar ou destruir todos os dados do banco de dados.
Recommendation: Aplicar T-09 — adicionar decorator @require_admin verificando X-Admin-Key do header.

[HIGH] Sensitive Data Exposure in API Response
File: models.py:79-86 e controllers.py:130-133
Description: get_todos_usuarios() retorna o campo "senha" em texto claro em cada objeto.
             Chamada em listar_usuarios() expõe todas as senhas via GET /usuarios.
Impact: Qualquer cliente autenticado recebe as senhas de todos os usuários.
Recommendation: Remover o campo "senha" da serialização — criar função _row_to_public_dict().

[HIGH] Weak Password Storage (Plaintext Comparison)
File: models.py:108-120
Description: Login compara senha em texto plano:
             cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
Impact: Senhas armazenadas sem hash; vazamento do banco expõe todas as senhas.
Recommendation: Aplicar T-05 — usar bcrypt.hashpw() no cadastro e bcrypt.checkpw() no login.

[HIGH] Business Logic in Model Layer
File: models.py:235-273
Description: Função relatorio_vendas() contém regras de negócio complexas (cálculo de desconto com thresholds e taxas):
             if faturamento > 10000: desconto = faturamento * 0.1
Impact: Viola SRP — model mistura acesso a dados com regras de negócio; impossível testar isoladamente.
Recommendation: Mover lógica de desconto para um controller/service; model só retorna os totais brutos.

[MEDIUM] N+1 Query Problem
File: models.py:171-201
Description: Para cada pedido, executa 2 queries aninhadas dentro de loops for:
             for row in rows: cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = ...")
                 for item in itens: cursor3.execute("SELECT nome FROM produtos WHERE id = ...")
Impact: N pedidos × M itens = N×M+N+1 queries; degradação de performance linear.
Recommendation: Aplicar T-06 — usar JOIN único para buscar pedidos, itens e nomes de produtos.

[MEDIUM] Hardcoded Seed Passwords in Database Module
File: database.py:76-83
Description: Senhas dos usuários seed inseridas em texto plano:
             ("Admin", "admin@loja.com", "admin123", "admin")
Impact: Senhas de seed ficam expostas no código-fonte e no histórico git.
Recommendation: Aplicar T-05 — usar bcrypt.hashpw() ao inserir usuários iniciais.

[LOW] DEBUG=True Hardcoded
File: app.py:8
Description: Modo debug ativado incondicionalmente:
             app.config["DEBUG"] = True
Impact: Stack traces detalhadas expostas ao cliente em caso de erro; não deve ir para produção.
Recommendation: Aplicar T-02 — ler de os.environ.get("DEBUG", "false").lower() == "true".

[LOW] Secret Key Exposed in Health Endpoint
File: controllers.py:288-289
Description: O endpoint /health retorna o secret_key e debug flag na resposta JSON:
             "secret_key": "minha-chave-super-secreta-123"
Impact: Qualquer cliente que acesse /health recebe a chave secreta da aplicação.
Recommendation: Remover campos sensíveis da resposta do health check.

[LOW] print() Used for Logging
File: controllers.py:8, 57, 161, 208-210, 248-250 (múltiplas ocorrências)
Description: print() utilizado para logging em handlers de rota:
             print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + "...")
Impact: Sem níveis de severidade, timestamps ou destino configurável; incompatível com agregadores de log.
Recommendation: Substituir por logging.getLogger(__name__).info(...).

---

================================
Total: 12 findings
CRITICAL: 4 | HIGH: 3 | MEDIUM: 2 | LOW: 3
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y

================================
PHASE 3: REFACTORING COMPLETE
================================
New Project Structure:
src/
├── config/
│   ├── settings.py       ← SECRET_KEY, DEBUG, DATABASE_PATH via os.environ
│   └── database.py       ← get_db() com Flask app context (sem global mutável)
├── models/
│   ├── produto_model.py  ← queries parametrizadas, sem lógica de negócio
│   ├── usuario_model.py  ← bcrypt hash, sem campo senha na resposta
│   └── pedido_model.py   ← JOIN único elimina N+1, lógica de desconto removida
├── controllers/
│   ├── produto_controller.py ← validação + orquestração
│   ├── usuario_controller.py ← autenticação via bcrypt
│   └── pedido_controller.py  ← desconto calculado aqui com constantes nomeadas
├── views/
│   ├── produto_routes.py ← Blueprint, handlers ≤ 5 linhas
│   ├── usuario_routes.py
│   └── pedido_routes.py
├── middlewares/
│   ├── error_handler.py  ← handler centralizado registrado via register_error_handlers()
│   └── auth.py           ← decorator @require_admin verifica X-Admin-Key
└── app.py                ← composition root, sem lógica de negócio

Validation
  ✓ Application boots without errors
  ✓ GET /health → 200 {"status":"ok","database":"connected","counts":{"produtos":10,"usuarios":3,"pedidos":0}}
  ✓ GET /produtos → 200, 10 produtos retornados
  ✓ GET /usuarios → 200, 3 usuários retornados (sem campo senha)
  ✓ POST /login (admin@loja.com / admin123) → 200 sucesso: True
  ✓ GET / → 200, mensagem de boas-vindas
  ✓ Zero SQL Injection — todas as queries usam parâmetros (?)
  ✓ Zero hardcoded credentials — SECRET_KEY lida de os.environ
  ✓ Senhas protegidas com bcrypt
  ✓ N+1 query eliminado com JOIN
  ✓ Lógica de negócio extraída dos models para controllers
================================
