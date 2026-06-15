const router = require('express').Router();
const checkoutController = require('../controllers/checkoutController');
const reportController = require('../controllers/reportController');
const userController = require('../controllers/userController');
const requireAdmin = require('../middlewares/auth');

router.post('/checkout', async (req, res, next) => {
  try {
    const { usr: name, eml: email, pwd: password, c_id: courseId, card } = req.body;
    const result = await checkoutController.processCheckout({ name, email, password, courseId, card });
    res.status(200).json(result);
  } catch (err) {
    next(err);
  }
});

router.get('/admin/financial-report', requireAdmin, async (req, res, next) => {
  try {
    const report = await reportController.financialReport();
    res.json(report);
  } catch (err) {
    next(err);
  }
});

router.delete('/users/:id', requireAdmin, async (req, res, next) => {
  try {
    const result = await userController.deleteUser(parseInt(req.params.id, 10));
    res.json(result);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
