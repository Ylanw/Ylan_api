const axios = require('axios')
module.exports = async (req, res) => {
  if (req.method === 'GET') {
    if (req.query.id) {
      let { data } = await axios.get('https://api.bilibili.com/x/web-interface/view?bvid=' + req.query.id)
      data = data.data
      let ls = {
        owner: data.owner.name,
        face: "https://images.weserv.nl/?url=" + data.owner.face,
        title: data.title,
        desc: data.desc,
        pic: "https://images.weserv.nl/?url=" + data.pic,
        coin: data.stat.coin,
        danmaku: data.stat.danmaku,
        favorite: data.stat.favorite,
        like: data.stat.like,
        reply: data.stat.reply,
        share: data.stat.share,
        view: data.stat.view,
      }
      if (req.query.t) { return res.send(ls[req.query.t]) } else return res.send(JSON.stringify(ls))
    } else { return res.send('Hello World!') }
  }
}