const userModel = require('../models/userModel');
const enrollmentModel = require('../models/enrollmentModel');

async function deleteUser(userId) {
  await enrollmentModel.removePaymentsByUserId(userId);
  await enrollmentModel.removeByUserId(userId);
  await userModel.remove(userId);
  return { message: 'Usuário e registros relacionados removidos com sucesso.' };
}

module.exports = { deleteUser };
