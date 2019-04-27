

# 在verifications目录下的constants.py文件中定义如下常数：
# 图片验证码redis有效期，单位秒
IMAGE_CODE_REDIS_EXPIRSE = 5 * 60

# 短信验证码有效期，单位秒
SMS_CODE_REDIS_EXPIRES = 5 * 60

# 发送间隔
SEND_SMS_CODE_INTERVAL = 60

# 短信发送模板
SMS_CODE_TEMP_ID = 1

# 短信验证码位数
SMS_CODE_NUMS = 6