from django.middleware.csrf import get_token
from django.utils.deprecation import MiddlewareMixin


class GetMiddleware(MiddlewareMixin):
    """
    自定义中间件获取csrf_token
    """
    # process_request是将前端获取的csrftoken验证，process_response是将处理完成的response返回给前端
    # 需要注意 这里的逻辑有点不同
    def process_request(self, request):
        get_token(request) # 验证csrf_token

