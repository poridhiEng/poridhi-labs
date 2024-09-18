// config/database.js
const { Sequelize } = require('sequelize');

const sequelize = new Sequelize('my_db', 'my_user', 'my_password', {
  host: 'localhost',
  dialect: 'mysql',
});

module.exports = sequelize;
