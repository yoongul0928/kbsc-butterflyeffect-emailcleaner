const Sequelize = require("sequelize");

const env = process.env.NODE_ENV || "development";
const config = require("../config/config2")[env];
const db = {};

const sequelize = new Sequelize(
  config.database,
  config.username,
  config.password,
  config
);

//데이터베이스 모델 정의
db.User = require("./users")(sequelize, Sequelize);
db.Email = require("./email")(sequelize, Sequelize);
db.Delete = require("./delete")(sequelize, Sequelize);
/*db.User = require('./usermanage')(sequelize, Sequelize);
db.User = require('./restore')(sequelize, Sequelize);
db.User = require('./reward')(sequelize, Sequelize);
*/

//데이터베이스 관계 정의
// db.User.hasMany(db.Email, { foreignKey: "personal_no", sourceKey: "no" });
// db.Email.belongsTo(db.User, {
//   foreignKey: "personal_no",
//   sourceKey: "user_no",
// });

db.User.hasMany(db.Email, {foreignKey:'no'});
db.Email.belongsTo(db.User, {foreignKey:'user_no'});

db.Email.hasMany(db.Delete, { foreignKey: "delete_no" });
db.Delete.belongsTo(db.Email, { foreignKey: "delete_no" });

db.sequelize = sequelize;
db.Sequelize = Sequelize;

module.exports = db;
