const axios = require('axios');

module.exports = async (req, res) => {
  if (req.method === 'GET') {
    if (req.query.qq) {
      try {
        const response = await axios.get(`https://users.qzone.qq.com/fcg-bin/cgi_get_portrait.fcg?uins=${req.query.qq}`);
        const data = response.data;
        const ls = JSON.parse(data.match(/portraitCallBack.*?\:(.*)\}/)[1]);

        res.json({
          success: 0,
          msg: '获取成功~',
          name: ls[6],
          avatar: ls[0]
        });
      } catch (error) {
        res.status(500).json({
          success: 1,
          msg: '获取失败~',
          error: error.message
        });
      }
    } else {
      res.status(400).json({
        success: 1,
        msg: '获取失败~，缺少qq参数'
      });
    }
  } else {
    res.status(405).json({
      success: 1,
      msg: '获取失败~，仅支持GET方法'
    });
  }
};
