const { OK, CREATED, BAD_REQUEST } =
  require("../../config/statusCode").statusCode;
const axios = require("axios");

const emailServices = require("../../services/email");

exports.deleteEmail = async (req, res, next) => {
  const { user_no, email_id, list } = req.body;

  const email_info = await emailServices.getEmailInfo({
    user_no,
    email_id,
  });

  //await emailServices.setDeleteEmail({ Emails, deleteDate, emailLen });

  try {
    const response = await axios.post("http://127.0.0.1:5000/delete", {
      Emails: {
        email_address: email_id,
        password: email_info.dataValues.email_Pw,
        list,
      },
    });
    await emailServices.updateTotalNum({
      email_no: email_info.dataValues.no,
      emailLen: response.data.emailLen,
    });

    res.status(CREATED).json({ result: response.data.emailLen });
  } catch (error) {
    res.status(BAD_REQUEST).json({
      message: "연동 실패!",
    });
  }
};
