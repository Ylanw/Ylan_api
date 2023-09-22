const axios = require('axios')
module.exports = async (req, res) => {
  if (req.method === 'GET') {
    if (req.query.qq) {
      let { data } = await axios.get(`https://users.qzone.qq.com/fcg-bin/cgi_get_portrait.fcg?uins=${req.query.qq}`);
      let ls = JSON.parse(data.match(/portraitCallBack.*?\:(.*)\}/)[1])
      res.json({
        success: 0,
        msg: '获取成功~',
        name: ls[6],
        avatar: ls[0]
      })
    } else {
      res.json({
        success: 1,
        msg: '获取失败~'
      })
    }
  }
}