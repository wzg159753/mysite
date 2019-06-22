from django.middleware.csrf import get_token
from django.utils.deprecation import MiddlewareMixin


class GetMiddleware(MiddlewareMixin):
    """
    自定义中间件获取csrf_token
    """
    # 记住就是每一次请求来的时候，调用这个方法，获取一个token，然后返回给浏览器，设置在cookie中
    # 浏览器下次请求的时候从cookie获取这个csrf_token，传给服务器验证,验证成功才能登陆
    # 需要注意 这里的逻辑有点不同
    def process_request(self, request):
        get_token(request) # 验证csrf_token

