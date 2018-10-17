### AIDog

一款从图片识别狗的类别的应用，包括Android版和微信小程序版。

#### 源码说明

 * data
   
   包含狗的类别信息的数据及处理脚本，数据收集自百度百科和维基百科。
   
   - dogs.xls - Office Excel格式的数据
   - dogs.csv - CSV格式的数据
   - csv_to_json.py - CSV格式转换为JSON格式的脚本，在微信小程序和Android程序中都使用JSON格式的数据
 
 * serving
  
   包含重新训练狗类别识别模型的脚本，以及为了部署而对模型进行重建的脚本。
   
   * retrain.py - 从Inception V3模型重新训练狗类别识别模型的脚本
   * rebuild_model.py - 为了给微信小程序提供RESTful API，对retrain模型做了重建，使其接受base64字符串形式的图片数据。
   * test_rebuild_model.py - 测试rebuild的模型，直接inference模型
   * test_client.py - 用来测试服务器上所部署模型的简单测试客户端，适用于rebuild的模型
   * test_client_v1.py - 测试客户端的最初版本，适用于retrain出来的模型
   * dog_labels_inception_v3.txt - 狗类别标签列表，这个列表是在retrain过程中生成的
 
 * wxapplet
 
   包含微信小程序的源码。

 * tflite

   - android - 采用Tensorflow Lite的Android源码，在手机端实现狗狗识别。
   - scripts - 包含从mobilenet重新训练的脚本以及相关显示脚本
  
#### 相关文档

1. [当微信小程序遇上TensorFlow：Server端实现](https://mp.weixin.qq.com/s/_sKhfx1lIiIiWYKWkpGMcQ)
2. [当微信小程序遇上TensorFlow：Server端实现补充](https://mp.weixin.qq.com/s/Jl-4wfZ6Zl_bRnfdLvO2Fw)
3. [当微信小程序遇上TensorFlow：小程序实现](https://mp.weixin.qq.com/s/d2OR5Yn8hOneiTKhyUfWXg)
4. [当微信小程序遇上TensorFlow：接收base64编码图像数据](https://mp.weixin.qq.com/s/QBw4zcViFeKQQKoYKDQj6Q)

另外关于Tensorflow SavedModel模型，您还可以阅读：
1. [Tensorflow SavedModel模型的保存与加载](https://mp.weixin.qq.com/s/s-tJxJZS898RorCq4xV_Ug)
2. [如何查看Tensorflow SavedModel格式模型的信息](https://mp.weixin.qq.com/s/Mj97KSbAb6vaJDp0p5DI0A)
3. [如何合并两个TensorFlow模型](https://mp.weixin.qq.com/s/nJkhDwtmxzS-LN4g3hDoEw)

关于Android版本的Tensorflow Lite，您可以阅读：

1. [这个中秋，我开发了一个识别狗狗的app](https://mp.weixin.qq.com/s/JT1brb5QWgM8xFpJMdtK-w)
2. [TensorFlow在移动设备与嵌入式设备上的轻量级跨平台解决方案 | Google 开发者大会 2018](https://mp.weixin.qq.com/s/8v8zK492SxuJdWlt5qq5Zg)
3. [如何将自己开发的模型转换为TensorFlow Lite可用模型](https://mp.weixin.qq.com/s/AIQtlNNEb0lKyshGZcpZAw)
4. [Android上的TensorFlow Lite，了解一下？](https://mp.weixin.qq.com/s/9V4fd3iFCl5NaeH8iTRR8g)

您还可以关注我的微信公众号：云水木石，一个专注于机器学习的个人空间。

![image](https://user-gold-cdn.xitu.io/2018/9/30/166280e143423db2?imageView2/0/w/1280/h/960/format/webp/ignore-error/1&ynotemdtimestamp=1539762492678)
