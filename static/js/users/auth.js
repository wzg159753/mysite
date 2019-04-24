$(function () {
  let $username = $('#user_name');
  let $img = $(".form-item .captcha-graph-img img");
  let sImageCodeId = "";

  // 1、图像验证码逻辑
  generateImageCode();  // 生成图像验证码图片
  $img.click(generateImageCode);  // 点击图片验证码生成新的图片验证码图片

  // 2、用户名验证逻辑
  $username.blur(function () {
    fn_check_usrname();
  });

  // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
  function generateImageCode() {
    // 1、生成一个图片验证码随机编号
    sImageCodeId = generateUUID();
    // 2、拼接请求url /image_codes/<uuid:image_code_id>/
    let imageCodeUrl = "/image_codes/" + sImageCodeId + "/";
    // 3、修改验证码图片src地址
    $img.attr('src', imageCodeUrl)

  }

  // 生成图片UUID验证码
  function generateUUID() {
    let d = new Date().getTime();
    if (window.performance && typeof window.performance.now === "function") {
      d += performance.now(); //use high-precision timer if available
    }
    let uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
      let r = (d + Math.random() * 16) % 16 | 0;
      d = Math.floor(d / 16);
      return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    return uuid;
  }


  // 判断用户名是否已经注册
  function fn_check_usrname() {
    let sUsername = $username.val();  // 获取用户名字符串
    let sReturnValue = "";

    if (sUsername === "") {
      message.showError('用户名不能为空！');
      return
    }
    if (!(/^\w{5,20}$/).test(sUsername)) {
      message.showError('请输入5-20个字符的用户名');
      return
    }

    // 发送ajax请求，去后端查询用户名是否存在
    $.ajax({
      url: '/usernames/' + sUsername + '/',
      type: 'GET',
      dataType: 'json',
      async: false
    })
      .done(function (res) {
        if (res.data.count !== 0) {
          message.showError(res.data.username + '已注册，请重新输入！');
          sReturnValue = ""
        } else {
          message.showInfo(res.data.username + '能正常使用！');
          sReturnValue = "success"
        }
      })
      .fail(function () {
        message.showError('服务器超时，请重试！');
        sReturnValue = ""
      });
    return sReturnValue
  }

});