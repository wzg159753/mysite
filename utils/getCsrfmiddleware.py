from django.middleware.csrf import get_token
from django.utils.deprecation import MiddlewareMixin


class GetMiddleware(MiddlewareMixin):
    """
    自定义中间件获取csrf_token
    """
    # process_request是请求预处理发送给前端的，process_response是获取将获取的数据进行预处理，然后给后端
    # 需要注意 这里的逻辑有点不同
    def process_request(self, request):
        get_token(request)
