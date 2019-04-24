from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as _UserManager

# Create your models here.


class UserManager(_UserManager):
    """
    自定义UserManager类 继承父类
    """
    def create_superuser(self, username, password, email=None, **extra_fields):
        """
        重写create_superuser方法，这个方法是用来创建用户的 将email改为默认参数
        这样就可以不写email
        :param username: 用户名 必填
        :param email: email 自己重写了 可以不填
        :param password: 密码 必填
        :param extra_fields:
        :return:
        """
        # 用super继续使用父类方法，将自定义的参数传给父类继续使用
        super(UserManager, self).create_superuser(username=username, password=password, email=email, **extra_fields)


class Users(AbstractUser):
    """
    自定义的一个用户模型类， 使用了django 的admin中的一些功能
    """
    # 覆盖原来的管理器，用自定义的管理器      Users.objects.filter(id=2)
    objects = UserManager()
    REQUIRED_FIELDS = ['mobile'] # 指定需要填入的字段

    # 自定义mobile字段
    mobile = models.CharField(verbose_name='电话号码', max_length=11, unique=True, help_text='手机号', error_messages={'unique': '电话号码已存在'})

    email_active = models.BooleanField(default=False, verbose_name='验证邮箱状态')

    class Meta:
        db_table = 'db_users' # 自定义表名  默认表名为app名 + 类名小写
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username