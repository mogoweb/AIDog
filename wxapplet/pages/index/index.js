//index.js

//获取应用实例
const app = getApp()

Page({
  data: {
  },
  onLoad: function () {
    console.log("onLoad");
  },

  // 从相册选择
  doChooseImage: function () {
    console.log("doChooseImage");

    // 选择图片
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album'],
      success: function (res) {
        console.log("wx.chooseImage album success")

        const filePath = res.tempFilePaths[0]
        console.log("filePath:" + filePath);

        // 跳转到photo页面
        wx.navigateTo({
          url: 'photo?filePath=' + filePath,
        })
      },
      fail: e => {
        console.error(e);
      },
      complete: function () {
      }
    })
  },
  // 拍照
  doTakePhoto: function () {
    // 选择图片
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['camera'],
      success: function (res) {
        console.log("wx.chooseImage camera success")

        const filePath = res.tempFilePaths[0]
        console.log("filePath:" + filePath);

        // 跳转到photo页面
        wx.navigateTo({
          url: 'photo?filePath=' + filePath,
        })
      },
      fail: e => {
        console.error(e);
      }
    })
  },
})
