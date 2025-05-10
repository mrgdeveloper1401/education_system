import random
from string import digits

def create_password_random(phone,k=None):
    char = phone + digits

    if k is None:
        k = random.randint(6, 10)
    password = ''.join(random.sample(char, k))
    return password
