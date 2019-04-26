from django.http import JsonResponse

from .res_code import Code


def get_json_data(error=Code.OK, errmsg='', data=None, **kwargs):
    """
    构造json数据
    :param error: 错误码
    :param errmsg:  错误信息
    :param data:  数据
    :param kwargs:  其他数据
    :return:
    """

    json_dict = {'error': error, 'errmsg': errmsg, 'data': data}
    # 判断kwargs有没有值 或者是不是一个字典
    if kwargs and isinstance(kwargs, dict) and kwargs.keys():
        # 如果验证成功，就更新到json_dict
        json_dict.update(kwargs)

    return JsonResponse(json_dict)
