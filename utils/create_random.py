import random
from string import ascii_lowercase, ascii_uppercase, digits

def create_password_random(k=None):
    char = ascii_lowercase + ascii_uppercase + digits

    if k is None:
        k = random.randint(6, 16)
    password = ''.join(random.sample(char, k))
    return password
