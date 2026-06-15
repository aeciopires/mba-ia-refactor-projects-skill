const express = require('express');
const settings = require('./config/settings');
const { initDb } = require('./config/database');
const apiRoutes = require('./routes/api');
const errorHandler = require('./middlewares/errorHandler');

const app = express();
app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'Frankenstein LMS' });
});

app.use('/api', apiRoutes);
app.use(errorHandler);

initDb()
  .then(() => {
    app.listen(settings.port, () => {
      console.log(`Frankenstein LMS rodando na porta ${settings.port}...`);
    });
  })
  .catch((err) => {
    console.error('Falha ao inicializar banco de dados:', err);
    process.exit(1);
  });

module.exports = app;
