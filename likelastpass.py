# ask for password
# hash sha512 it

import hashlib # for hashing main password
from getpass import getpass # for hidden input
import base64
from cryptography.fernet import Fernet
filename = 'safepasswords'
def hash_it(mainpassword):
    return hashlib.sha512(mainpassword.encode('utf-8')).hexdigest().encode('utf-8')

def readfileraw():
    try:
        with open(filename,'r') as f:
            a = f.read()
    except FileNotFoundError:
        with open(filename,'w') as f:
            f.write('\n')
        a = readfileraw()
    except IsADirectoryError:
        print(f'{filename} is a directory!')
        raise SystemExit
    return a

def writerawonce(what):
    try:
        with open(filename,'r') as f:
            a = f.read()
    except FileNotFoundError:
        with open(filename,'w') as f:
            f.write(what+'\n')
    return

def readfile(hashed,full=False):
    if not full:

        filelines = readfileraw().split('\n')
        if filelines[0] == hashed:
            return filelines
    
        return False
    filelines = readfileraw().split('\n')
    filelines = filelines[1:]
    print(type(filelines))
    print(type(filelines[0]))
    uncode(hashed,filelines)

def uncode(hashed,lines):
    if not lines:
        return
#    print(hashed)
    hashed= base64.urlsafe_b64encode(hashed)
    for line in lines:
        if len(line) > 5:
#            key = base64.urlsafe_b64encode(hashed[:32])

            line = line.encode('utf-8')
            key = base64.urlsafe_b64encode(hashed[:32])
            aa = hashed[:32]
            bb = hashed[32:]
            hashed = bb+aa
            f = Fernet(key)
            raw = decrypt(key,line)
            print(raw)

def decrypt(key,token):
#    token = base64.decode(token,'utf-8')
    if type(token) != bytes:
        token = bytes(token,'utf-8')
    f = Fernet(key)
    print(f'{key}\n{token}')
    return f.decrypt(token)


def newpass(hashed):
    hashed = base64.urlsafe_b64encode(hashed)
    site = input('password to site (ex: facebook.com):\n')
    ps = getpass(prompt='password there:\n')
    newline = site + '\t\t' + ps
    newline = newline.encode('utf-8')
    l = len(readfileraw().split('\n'))-1
    l = l % 4
    while l != 0:
        aa= hashed[:32]
        bb = hashed[32:]
        hashed = bb + aa

        l-=1
    key = base64.urlsafe_b64encode(hashed[:32])
    F = Fernet(key)
    newline = F.encrypt(newline)
#    newline = base64(newline)
    with open(filename,'a') as f:
        f.write(newline.decode('utf-8'))
        f.write('\n')

def main():
    passw = getpass(prompt='main password:\n')
#    passw = b'Maecenata28101105'
    hashed = hash_it(passw).decode('utf-8')
    writerawonce(hashed)
    filelines = readfile(hashed,False)

    if not filelines:
        print('wrong password')
        return
    c = 5

    passw2 = passw[::-1]
    hash2 = hash_it(passw2)
    while c != 0:
        try:
            c = int(input('\n(1) read passwd\n(2) add new passwd\n'+
                    '(0) exit\n'))
        except:
            raise SystemExit
        if c == 2:
            newpass(hash2)

        elif c == 1:
            readfile(hash2,True)
        else:
            raise SystemExit
    return

main()


