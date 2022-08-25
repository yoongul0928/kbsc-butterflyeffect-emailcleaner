const { Email } = require("../../models");
//const { Delete } = require("../../models");
const { hashingPw } = require("../../utils/bcrypt");
const { Op, fn, col } = require("sequelize");

exports.insertEmail = async ({ no, email_id, email_Pw }) => {
  console.log(no);
  console.log(email_id);
  console.log(email_Pw);
  const emailData = {
    user_no: no,
    email_id,
    email_Pw,
  };
  console.log(emailData);
  const result = await Email.create(emailData);
  console.log(result);
  return result;
};

exports.getEmail = async ({ user_no }) => {
  const result = await Email.findAll({
    attributes: ["email_id", "email_Pw"],
    where: { user_no },
    raw: true,
  });
  return result;
};

exports.getEmailInfo = async ({ user_no, email_id }) => {
  const result = await Email.findOne({
    attributes: ["no", "email_Pw"],
    where: { user_no, email_id },
  });
  return result;
};

exports.updateTotalNum = async ({ email_no, emailLen }) => {
  const result = await Email.increment(
    { total_no: emailLen },
    { where: { no: email_no } }
  );
  return result;
};

exports.getTotalNum = async (user_no) => {
  const result = await Email.findAndCountAll({
    attributes: [
      [sequelize.fn("sum", sequelize.col("total_no")), "total_amount"],
    ],
    group: { user_no },
  });
  return result;
};
