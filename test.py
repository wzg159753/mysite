import random
import string
from urllib import parse

# print(string.digits)
# a = ''.join([random.choice(string.digits) for _ in range(6)])

# class Test(object):
#
#     def __init__(self, test):
#         self.test = test
#
#     def get(self):
#         print(f'hello_{self.test}')
#         return self.test
#
# t1 = Test('world')
# # res = t1.get()
# # print(res)
#
# class Test2(Test):
#
#     def __init__(self, name):
#         super().__init__(name)
#
#     def get(self):
#         aa = super().get()
#         print(aa+'111')
#
# t2 = Test2('xiaowang')
# t2.get()

# a = 1
# b = 2
# c = 4
# d = 6
# e = 20
#
# result = (a if a == 2 else None) or (b if b == 3 else None)
# print(result)

s = '%257B%2522claimEditPoint%2522%253A%25220%2522%252C%2522explainPoint%2522%253A%25220%2522%252C%2522integrity%2522%253A%252214%2525%2522%252C%2522state%2522%253A%25223%2522%252C%2522surday%2522%253A%2522188%2522%252C%2522announcementPoint%2522%253A%25220%2522%252C%2522vipManager%2522%253A%25220%2522%252C%2522onum%2522%253A%25225%2522%252C%2522monitorUnreadCount%2522%253A%252256%2522%252C%2522discussCommendCount%2522%253A%25221%2522%252C%2522claimPoint%2522%253A%25220%2522%252C%2522token%2522%253A%2522eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxMzM3NTM1ODU4MSIsImlhdCI6MTU2MjU2ODg1OSwiZXhwIjoxNTk0MTA0ODU5fQ.cu2VYzz93n4hz8i1d6IOXhj5BBx5S44QTRk9JzZ0mLEY_X0vy23LlCPClzy4CvNbU1McGGlOgyhyev7YKbOkKw%2522%252C%2522vipToTime%2522%253A%25221578728208870%2522%252C%2522redPoint%2522%253A%25220%2522%252C%2522myAnswerCount%2522%253A%25220%2522%252C%2522myQuestionCount%2522%253A%25220%2522%252C%2522signUp%2522%253A%25220%2522%252C%2522nickname%2522%253A%2522%25E8%2596%2587%25E8%25AF%25BA%25E5%25A8%259C%25C2%25B7%25E7%2591%259E%25E5%25BE%25B7%2522%252C%2522privateMessagePointWeb%2522%253A%25220%2522%252C%2522privateMessagePoint%2522%253A%25220%2522%252C%2522isClaim%2522%253A%25220%2522%252C%2522companyName%2522%253A%2522%25E4%25BF%25A1%25E8%2581%2594%25E8%25B5%2584%25E4%25BF%25A1%25E6%259C%258D%25E5%258A%25A1%25E6%259C%2589%25E9%2599%2590%25E5%2585%25AC%25E5%258F%25B8%25E5%258C%2597%25E4%25BA%25AC%25E5%2588%2586%25E5%2585%25AC%25E5%258F%25B8%2522%252C%2522isExpired%2522%253A%25220%2522%252C%2522pleaseAnswerCount%2522%253A%25221%2522%252C%2522vnum%2522%253A%25220%2522%252C%2522bizCardUnread%2522%253A%25220%2522%252C%2522mobile%2522%253A%252213375358581%2522%257D'

# r = parse.unquote(s)
# # print(r)
# print(parse.unquote(r))


a = '{"claimEditPoint":"0","explainPoint":"0","integrity":"14%","state":"3","surday":"188","announcementPoint":"0","vipManager":"0","onum":"5","monitorUnreadCount":"56","discussCommendCount":"1","claimPoint":"0","token":"eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxMzM3NTM1ODU4MSIsImlhdCI6MTU2MjU2ODg1OSwiZXhwIjoxNTk0MTA0ODU5fQ.cu2VYzz93n4hz8i1d6IOXhj5BBx5S44QTRk9JzZ0mLEY_X0vy23LlCPClzy4CvNbU1McGGlOgyhyev7YKbOkKw","vipToTime":"1578728208870","redPoint":"0","myAnswerCount":"0","myQuestionCount":"0","signUp":"0","nickname":"薇诺娜·瑞德","privateMessagePointWeb":"0","privateMessagePoint":"0","isClaim":"0","companyName":"信联资信服务有限公司北京分公司","isExpired":"0","pleaseAnswerCount":"1","vnum":"0","bizCardUnread":"0","mobile":"13375358581"}'

b = parse.quote(a)
print(parse.quote(b))





