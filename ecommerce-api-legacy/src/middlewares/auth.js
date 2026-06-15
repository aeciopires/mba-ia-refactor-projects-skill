const settings = require('../config/settings');

module.exports = function requireAdmin(req, res, next) {
  const key = req.headers['x-admin-key'];
  if (key !== settings.adminKey) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
};
