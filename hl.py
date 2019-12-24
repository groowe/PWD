import hashlib

s = hashlib.sha512("This will be hashed".encode('utf-8'))
t = s.hexdigest().encode('utf-8')
print(t)

# t = 
# 1bb0f189d98515897224af9de9a495095bbee873eae59f277f6618688cd6ba05472a45e4e25620787effff9d1499979ddb474b89576c47a3b688b5ebc7154696

import base64

print(len(t)/32)
key = base64.urlsafe_b64encode(t[:32])
from getpass import getpass
passw = getpass(prompt='main password:\n')

from cryptography.fernet import Fernet
passw = passw.encode()
f = Fernet(key)
print(f'passw = {passw}')
encrypted = f.encrypt(passw)
print(f'encrypted = {encrypted}')
decrypted = f.decrypt(encrypted).decode('utf-8')
print(f'decrypted = {decrypted}')
##############
