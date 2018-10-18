// pages/index/photo.js

//引入本地json数据
var dogs_json = require('../../utils/dogs_data.js');
var upng = require('../../utils/upng-js/UPNG.js');

// Convert from normal to web-safe, strip trailing "="s
function webSafe64(base64) {
  return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

// 获取图像RGB数据
var getImageBase64 = function (canvasId, imgUrl, callback, imgWidth, imgHeight) {
  console.log("entering getBase64Image");
  const ctx = wx.createCanvasContext(canvasId);
  ctx.drawImage(imgUrl, 0, 0, imgWidth || 299, imgHeight || 299);
  ctx.draw(false, () => {
    console.log("ctx.draw");
    // API 1.9.0 获取图像数据
    wx.canvasGetImageData({
      canvasId: canvasId,
      x: 0,
      y: 0,
      width: imgWidth || 299,
      height: imgHeight || 299,
      success(res) {
        var result = res;
        console.log("buf:" + [result.data.buffer]);

        // png编码
        var pngData = upng.encode([result.data.buffer], result.width, result.height);
        // base64编码
        var base64Data = wx.arrayBufferToBase64(pngData);
        // web safe
        var base64DataSafe = webSafe64(base64Data)

        callback(base64DataSafe);
      },
      fail: e => {
        console.error(e);
      },
    })
  })
};

Page({

  /**
   * 页面的初始数据
   */
  data: {
    imgUrl: '',
    dogList: {},
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    this.setData({
      //dogs_json.dog_list获取dogs_data.js里定义的json数据，并赋值给dogList
      dogList: dogs_json.dog_list,
      imgUrl: options.filePath,
      display: "none"
    });
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {
    wx.showLoading({
      title: '正在识别中...',
    });
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
    var filePath = this.data.imgUrl;
    var that = this;

    getImageBase64('dogCanvas', filePath, function (base64Data) {
      //  在此处得到的RGB数据
      console.log("getImageBase64");
      var json_data = {
        "model_name": "default", model_version: 2, "data": { "image": "" }
      }
      json_data["data"]["image"] = base64Data;
      console.log("json_data:" + json_data);

      wx.request({
        url: "https://ilego.club:8500",
        // header: {
        //   "Content-Type": "application/x-www-form-urlencoded"
        // },
        method: "POST",
        data: json_data,
        success: function (response) {
          console.log("wx.request success!")
          var prediction = response.data["prediction"];
          console.log("response:" + response)
          console.log(prediction);
          var max = 0;
          var index = 0;
          for (var i = 0; i < prediction[0].length; i++) {
            console.log(i + ":" + prediction[0][i])
            if (prediction[0][i] > max) {
              max = prediction[0][i];
              index = i;
            }
          }
          console.log("max:" + max + ", index:" + index);

          console.log("hideLoading");
          wx.hideLoading();

          if (max > 0.1) {
            var dogInfo = that.data.dogList[index];
            console.log(dogInfo);
            that.setData({
              display: "block",
              cname: dogInfo["cname"],
              ename: dogInfo["ename"],
              description: dogInfo["description"],
            });
          } else {
            that.setData({
              display: "none"
            });
            wx.showModal({
              title: '提示',
              content: '对不起，无法识别！',
              showCancel: false,
            });
          }
        },
        fail: e => {
          console.error(e);
          that.setData({
            display: "none"
          });
          console.log("hideLoading");
          wx.hideLoading();
          wx.showModal({
            title: '错误提示',
            content: '请求服务器出错：' + e.errMsg,
            showCancel: false,
          });
        },
        complete: function() {
          console.log("complete");
        }
      });
    });
  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {

  }
})