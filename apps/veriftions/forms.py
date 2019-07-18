from django import forms
from django.core.validators import RegexValidator # 导入校验器
from django_redis import get_redis_connection # 导入redis连接工具


from users.models import Users

# 正则表达式验证 手机号
mobile_validator = RegexValidator(r"^1[3-9]\d{9}$", "手机号码格式不正确")


class SmsCodeForm(forms.Form):
    """
    验证发送短信的三个字段
    # 需要手机号来发送短信
    # 图片uuid来获取验证码，用来比对
    # 用户输入的验证码用来跟数据库中的验证码比对一致性
    """
    # 手机号
    mobile = forms.CharField(max_length=11, min_length=11, validators=[mobile_validator], error_messages={
        'max_length': '密码超出最大长度',
        'min_length': '密码小于最小长度',
        'required': '手机号已存在'
    })
    # 验证码uuid
    image_code_id = forms.UUIDField(error_messages={'required': '图片id不能为空'})
    # 用户输入的验证码
    text = forms.CharField(max_length=4, min_length=4, error_messages={
        'max_length': '验证码超过最大长度',
        'min_length': '验证码小于最小长度',
        'required': '验证码不能为空'
    })

    def clean(self):
        """
        自定义多个验证  可以单个验证 def clean_字段名():
        :return:
        """
        clean_data = super().clean()
        # 获取字段
        mobile = clean_data.get('mobile')
        image_code_id = clean_data.get('image_code_id')
        text = clean_data.get('text')

        # 判断手机号存不存在
        if Users.objects.filter(mobile=mobile).exists():
            raise forms.ValidationError('手机号码已经存在')

        # 连接到指定redis数据库
        con = get_redis_connection(alias='verify_codes')
        # 拼接uuid
        img_key = f'img_{image_code_id}'

        # 获取对应uuid的图片验证码文本信息
        real_image_code_origin = con.get(img_key)
        # # 从redis中取出来的数据是二进制数据，将二进制解码成字符串
        # real_image_code = real_image_code_origin.decode('utf8')

        # 用一个三目运算解决验证问题
        real_image_code = real_image_code_origin.decode('utf8') if real_image_code_origin else None
        # 将图片验证码取出来后存放在内存中 所以redis中就不需要了，释放内存，删除验证码
        # con.delete(img_key)

        if (not real_image_code) or (text != real_image_code):
            raise forms.ValidationError('图片验证失败')

        # 验证60秒 如果60s之内 不能发送
        sms_flag_key = f'sms_flag_{mobile}'
        # 获取验证码状态标签
        sms_fmt = con.get(sms_flag_key)
        # 如果有这个标签，则代表在60s之内，就把异常返回给后端
        if sms_fmt:
            raise forms.ValidationError('操作过于频繁，请60秒后发送')

