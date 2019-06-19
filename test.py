import random
import string

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
result = '%06d' % random.randint(100000, 999999)
print(result)











