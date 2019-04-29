import random
import string

print(string.digits)
a = ''.join([random.choice(string.digits()) for _ in range(6)])

