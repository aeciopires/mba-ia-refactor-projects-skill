================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js)
Framework:     Express 4.18.2
Dependencies:  sqlite3 5.1.6
Domain:        LMS API — cursos, matrículas, pagamentos, usuários, checkout
Architecture:  Monolítica — God Class (AppManager) centraliza DB, rotas e lógica de negócio
Source files:  3 files analyzed (src/app.js, src/AppManager.js, src/utils.js)
DB tables:     users, courses, enrollments, payments, audit_logs
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript + Express 4.18.2
Files:   3 analyzed | ~155 lines of code

Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 2 | LOW: 3

Findings

---

[CRITICAL] God Class
File: src/AppManager.js:1-141
Description: Classe única com 3 responsabilidades distintas:
             - initDb(): cria tabelas e seed de dados (responsabilidade de DB/config)
             - setupRoutes(): define rotas e lógica de checkout/pagamento (responsabilidade de routes + controller)
             - Lógica de negócio embutida em closures dentro de setupRoutes()
Impact: Impossível testar partes isoladas; qualquer mudança na estrutura do DB afeta o comportamento de pagamentos.
Recommendation: Aplicar T-03 — decompor em config/database.js, models/, controllers/, routes/.

[CRITICAL] Hardcoded Credentials — Database & Payment Key
File: src/utils.js:2-6
Description: Credenciais de produção hardcoded no código-fonte:
             dbPass: "senha_super_secreta_prod_123"
             paymentGatewayKey: "pk_live_1234567890abcdef"
             smtpUser: "no-reply@fullcycle.com.br"
Impact: Qualquer desenvolvedor com acesso ao repositório possui credenciais de produção; rotação de chaves exige commit.
Recommendation: Aplicar T-02 — mover para process.env.DB_PASS, process.env.PAYMENT_KEY etc.

[CRITICAL] Weak / Reversible Password Storage
File: src/utils.js:17-23 e src/AppManager.js:68-69
Description: Função badCrypto() usa base64 como "hash" de senha:
             return Buffer.from(pwd).toString('base64').substring(0, 10);
             Hash gravado: let hash = badCrypto(p || "123456");
Impact: Base64 é codificação reversível — qualquer atacante com o hash recupera a senha original instantaneamente.
Recommendation: Aplicar T-05 — usar bcrypt.hash(pwd, 10) e bcrypt.compare().

[CRITICAL] Hardcoded Seed Password
File: src/AppManager.js:18
Description: Senha de usuário seed gravada em texto plano no banco:
             INSERT INTO users VALUES ('Leonan', 'leonan@fullcycle.com.br', '123')
Impact: Senha de seed fica em texto plano no banco e no código-fonte.
Recommendation: Usar bcrypt.hash() ao inserir dados iniciais.

[HIGH] Deeply Nested Callback Hell
File: src/AppManager.js:28-78
Description: Rota POST /api/checkout possui 4 níveis de callbacks aninhados:
             db.get(course) → db.get(user) → db.run(enrollment) → db.run(payment) → db.run(audit)
Impact: Impossível ler, testar ou modificar o fluxo de checkout; qualquer erro no meio da cadeia é silenciado.
Recommendation: Aplicar T-03 — reescrever com async/await e Promises encadeadas lineares.

[HIGH] Unauthenticated Admin Endpoint
File: src/AppManager.js:80-129
Description: Rota GET /api/admin/financial-report não possui nenhum middleware de autenticação.
Impact: Qualquer cliente pode acessar dados financeiros completos de todos os cursos e alunos.
Recommendation: Aplicar T-09 — adicionar middleware requireAdmin verificando x-admin-key no header.

[HIGH] Mutable Global State
File: src/utils.js:9-10
Description: Variáveis mutáveis no escopo de módulo compartilhadas entre requests:
             let globalCache = {};
             let totalRevenue = 0;
Impact: Em ambiente concorrente, múltiplos requests modificam o mesmo objeto; dados de um usuário podem contaminar outro.
Recommendation: Aplicar T-08 — substituir por serviço de cache com escopo de request ou Map gerenciado.

[MEDIUM] Orphan Records on User Delete
File: src/AppManager.js:131-137
Description: DELETE de usuário não remove enrollments nem payments associados:
             this.db.run("DELETE FROM users WHERE id = ?", [id], ...)
             // enrollments e payments ficam órfãos
Impact: Integridade referencial quebrada; relatório financeiro pode contar pagamentos de usuários inexistentes.
Recommendation: Deletar cascade ou remover explicitamente payments → enrollments → users nessa ordem.

[MEDIUM] N+1 Query in Financial Report
File: src/AppManager.js:80-128
Description: Para cada curso, faz db.all(enrollments) e para cada enrollment faz 2 queries (user + payment):
             courses.forEach(c => db.all(enrollments, ... enrollments.forEach(enr => db.get(user) + db.get(payment))))
Impact: Para C cursos com E matrículas cada, executa C × E × 2 + C queries — degradação quadrática.
Recommendation: Aplicar T-06 — JOIN único: courses LEFT JOIN enrollments LEFT JOIN users LEFT JOIN payments.

[LOW] Non-semantic Variable Names
File: src/AppManager.js:29-33
Description: Variáveis sem semântica no handler de checkout:
             let u = req.body.usr; let e = req.body.eml; let p = req.body.pwd; let cid = req.body.c_id; let cc = req.body.card;
Impact: Leitura muito difícil; manutenção propensa a erros por confusão entre variáveis.
Recommendation: Usar nomes descritivos: const { usr: name, eml: email, c_id: courseId, card } = req.body;

[LOW] Test Stub Payment Logic in Production
File: src/AppManager.js:45-46
Description: Lógica de aprovação de pagamento baseada no dígito inicial do número do cartão:
             let status = cc.startsWith("4") ? "PAID" : "DENIED";
Impact: Código de teste deixado em produção; pagamentos reais não são processados por gateway.
Recommendation: Substituir por chamada real ao gateway de pagamento via variável de ambiente process.env.PAYMENT_KEY.

[LOW] console.log Exposing Sensitive Data
File: src/AppManager.js:45
Description: Log expõe o número do cartão e a chave do gateway de pagamento:
             console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
Impact: Dados de cartão e chave de API aparecem em logs, violando PCI-DSS.
Recommendation: Remover o log ou mascarar os dados (ex.: cartão terminado em ${cc.slice(-4)}).

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
│   ├── settings.js       ← todas as configs lidas de process.env
│   └── database.js       ← helpers run/get/all com Promises + initDb()
├── models/
│   ├── userModel.js      ← findByEmail, create (bcrypt), verifyPassword, remove
│   ├── courseModel.js    ← findById (only active courses), findAll
│   └── enrollmentModel.js ← create, createPayment, logAudit, findAllWithDetails (JOIN único)
├── controllers/
│   ├── checkoutController.js ← async/await, sem req/res, validação de negócio
│   ├── reportController.js   ← relatório financeiro via JOIN
│   └── userController.js     ← delete em cascata (payments → enrollments → users)
├── routes/
│   └── api.js            ← Express Router, try/catch → next(err), auth middleware aplicado
├── middlewares/
│   ├── auth.js           ← requireAdmin verifica x-admin-key header
│   └── errorHandler.js   ← handler centralizado (err, req, res, next)
└── app.js                ← composition root, sem lógica de negócio

Validation
  ✓ Estrutura MVC criada com separação total de responsabilidades
  ✓ Credenciais movidas para process.env (settings.js)
  ✓ God Class (AppManager.js) decomposta em 6 módulos
  ✓ bcrypt substitui badCrypto() para hash de senhas
  ✓ Callback hell reescrito com async/await
  ✓ N+1 query eliminada com JOIN único em findAllWithDetails()
  ✓ /api/admin/financial-report protegida com requireAdmin
  ✓ DELETE de usuário remove payments e enrollments em cascata
  ✓ console.log com dados de cartão removido
  ⚠ Validação de boot e endpoints requer Node.js instalado no ambiente
    Executar: npm install && node src/app.js
    Testar:   curl http://localhost:3000/health
================================
