module.exports = {
  port: process.env.PORT || 3000,
  dbPath: process.env.DB_PATH || ':memory:',
  paymentKey: process.env.PAYMENT_KEY || '',
  adminKey: process.env.ADMIN_KEY || 'admin-key-change-me',
  smtpUser: process.env.SMTP_USER || '',
};
