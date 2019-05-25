$(document).ready(function() {

  var animating = false,
      submitPhase1 = 1100,
      submitPhase2 = 400,
      logoutPhase1 = 800,
      $login = $(".login"),
      $app = $(".app");

  function ripple(elem, e) {
    $(".ripple").remove();
    var elTop = elem.offset().top,
        elLeft = elem.offset().left,
        x = e.pageX - elLeft,
        y = e.pageY - elTop;
    var $ripple = $("<div class='ripple'></div>");
    $ripple.css({top: y, left: x});
    elem.append($ripple);
  };

  $(document).on("click", ".login__submit", function(e) {
      var register_user=$('#register_user').val();
      var register_nick=$('#register_nick').val();
      var register_pwd=$('#register_pwd').val();
      var register_repwd=$('#register_repwd').val();
    if(register_user !=''&& register_nick!='' && register_pwd!=''&&register_repwd!=''){
       if (register_pwd==register_repwd){
 if (animating) return;
    animating = true;
    var that = this;
    ripple($(that), e);
    $(that).addClass("processing");
    setTimeout(function() {
      $(that).addClass("success");
      // setTimeout(function() {
      //   $app.show();
      //   $app.css("top");
      //   $app.addClass("active");
      // }, submitPhase2 - 70);
       register(register_user,register_pwd,register_nick);
      setTimeout(function() {
        $login.hide();
        $login.addClass("inactive");
        animating = false;
        $(that).removeClass("success processing");
      }, submitPhase2);
    }, submitPhase1);
       } else {
         alert('两次密码输入不一样，请重新输入！')
           $('#register_pwd').val('');
           $('#register_repwd').val('');
       }

    }else{
        alert('有未填项！')
      }

  });

function register(user,pwd,nickname){
    $.ajax({
                    url:'/register',
                    type:'POST',
                    data:{
                        'user':user,
                        'password':pwd,
                        'nickname':nickname
                    },
                    dataType:'json',
                    success:function(data){
                        if (data['success']==true){
                            alert('注册成功')
                            window.location.href='/login'
                        } else {
                             alert('用户名已存在')
                        }
                    },error: function (jqXHR) {
                    console.log('error2:', jqXHR)
                }
                })
}





  $(document).on("click", ".app__logout", function(e) {
    if (animating) return;
    $(".ripple").remove();
    animating = true;
    var that = this;
    $(that).addClass("clicked");
    setTimeout(function() {
      $app.removeClass("active");
      $login.show();
      $login.css("top");
      $login.removeClass("inactive");
    }, logoutPhase1 - 120);
    setTimeout(function() {
      $app.hide();
      animating = false;
      $(that).removeClass("clicked");
    }, logoutPhase1);
  });

});