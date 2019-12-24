# ask for password
# hash sha512 it

import hashlib # for hashing main password
from getpass import getpass # for hidden input
import base64
from cryptography.fernet import Fernet
filename = 'safepasswords'
def hash_it(mainpassword): # mainpassword= str
    return hashlib.sha512(mainpassword.encode('utf-8')).hexdigest()#.encode('utf-8')
#           hashlib makes _hashlib.HASH , requires bytes ( str (encode) => bytes)
#                       .hexdigest = > str
#                       .encode  = > bytes

def readfileraw():
    try:
        with open(filename,'r') as f:
            a = f.read()
    except FileNotFoundError:
        return False
#        with open(filename,'w') as f:
#            f.write('\n')
#        a = readfileraw()
    except IsADirectoryError:
        print(f'{filename} is a directory!')
        raise SystemExit
    return a # string


def readfile(hashed,full=False): # hashed = str
    if not full:
        filelines = readfileraw().split('\n')
     
        key = base64.urlsafe_b64encode(hashed[:32].encode('utf-8'))
        token = filelines[0].encode('utf-8')
        check = decrypt(key,token)
#        print(check)
#        print(token)
#        print(key)
        if not check:
            return False
        return True

    filelines = readfileraw()
    if not filelines:
        print('empty list of passwords')
        return False
#    print(type(filelines))
#    print(type(filelines[0]))
    uncode(hashed,filelines) # str , [str,str,str,..]

def uncode(hashed,lines): # str , [str,str,str,...]
    if type(hashed) == str:
        hashed = hashed.encode('utf-8')
    keys= []
    for i in range(4):
        key = base64.urlsafe_b64encode(hashed[:32])
        hashed = hashed[32:]
#        print(len(key))
#        if len(key) == 44:
#            keys.append(key)
        keys.append(key)
#    for key in keys:
#        print(key)
    if not lines:
        return
#    print(hashed)
#    hashed= base64.urlsafe_b64encode(hashed)
#    print(lines) 
#    print(type(lines))
    if type(lines) == str:
        lines = lines.split('\n')
#        key = keys[0]
#        raw = decrypt(key,lines.encode('utf-8'))
#        print(f'raw = {raw}')
#        print(f'lines now {type(lines)}')
    for l in lines:
        if len(l) < 4:
            lines.pop(lines.index(l))
#    for i in range(0,len(lines),-1):
#        if len(lines[i]) < 4:
#            lines.remove(lines[i])
#    print(f'len lines = {len(lines)}')
#    print(f'lines = {lines}')
#    print(lines) 
#    print(type(lines))
    if type(lines) == list:
        print('site\t\tpassword')
        for line in lines:
            k = lines.index(line) % 4
            key = keys[k]
#            print(lines[i])
#            print(len(lines[i]))
            raw = decrypt(key,line.encode('utf-8'))
#            print('raw')
            raw = raw.decode('utf-8')
            print(f'{raw}')
    else:
        print(type(lines))

def decrypt(key,token):
#    token = base64.decode(token,'utf-8')
#    if type(token) != bytes:
#        token = bytes(token,'utf-8')
    f = Fernet(key)
#    print(f'token {token}')
#    print(f'len token = {len(token)}')
#    print(f'key {key}')
#    print(f'len key = {len(key)}')
    try:
        a = f.decrypt(token)
    except:
        return False
    return f.decrypt(token)

def newpass(hashed): # hashed = str
#    hashed = base64.urlsafe_b64encode(hashed)
    if type(hashed) == str:
        hashed = hashed.encode('utf-8')
    keys= []
    for i in range(4):
        key = base64.urlsafe_b64encode(hashed[:32])
        hashed = hashed[32:]
        keys.append(key)
#    print('keys:')
    for i in keys:
        print(i)
    site = input('password to site (ex: facebook.com):\n') # str
    ps = getpass(prompt='password there:\n') # str
    newline = site + '\t\t' + ps # str
    newline = newline.encode('utf-8') # bytes
    already = readfileraw()
    if not already:
        l = 0
    else:
        already = already.split('\n')
        for line in already:
            if len(line) < 4:
                already.pop(already.index(line))
        l = len(already) % 4
#    key = base64.urlsafe_b64encode(hashed[:32].encode('utf-8'))
#    l +=1
#    if l ==4:
#        l = 0
    F = Fernet(keys[l])
    newline = F.encrypt(newline)
#    print(newline)
#    print(len(newline))
#    print(len(newline.decode('utf-8')))
#    newline = base64(newline)
    with open(filename,'a') as f:
        f.write(newline.decode('utf-8'))
        f.write('\n')

def main():
    passw = getpass(prompt='main password:\n') # str
    hashed = hash_it(passw)#.decode('utf-8') # bytes .decode => str
    c = 5
    passw2 = passw[::-1]
    hash2 = hash_it(passw2)#.decode('utf-8') # bytes .decode => str
    # check if passw is correct:
    check = readfile(hash2,False)
    if not check:
        print('wrong password!')
        raise SystemExit
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
if __name__ == '__main__':
    main()


