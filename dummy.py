# try dummy working

import hashlib # hashing main password
from getpass import getpass # hidden input
import base64
from cryptography.fernet import Fernet

filename = 'dummysafe'
# read from file

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

def writefileraw(what):
    with open(filename,'w') as f:
        f.write(what)

def hashit(what):
    return hashlib.sha512(what.encode('utf-8')).hexdigest().encode('utf-8')

def main():
    passw =  getpass(prompt='mainpass:\n')
    ## get password : password
    hashedpassword = hashit(passw)
    ## hash it : hashedpassword
    key = base64.urlsafe_b64encode(hashedpassword[:32])
    ## use first 32 bytes as a key : key
    value = input('value to encode:\n')
    ## get string : inputvalue
    f = Fernet(key)
    crypted = f.encrypt(value.encode('utf-8'))
    ## crypt it : crypted 
    writefileraw(crypted.decode('utf-8'))
    ## write it : to file
    fromfile = readfileraw()
    ## read it : from file
    passw2 =  getpass(prompt='mainpass:\n')
    ## get password : password2
    hashedpassword2 = hashit(passw2)
    ## hash it : hashedpassword2
    key2 = base64.urlsafe_b64encode(hashedpassword2[:32])
    ## use first 32 bytes as a key : key2
#    print(key)
#    print(key2)
#    print(hashedpassword)
    f2 = Fernet(key2)
    try:
        decrypted = f2.decrypt(fromfile.encode('utf-8'))
    except Exception as exception:
        print('wrong pass')
        print(f'{exception}')
        raise SystemExit
    ## decrypt it : decrypted
    print(f'{value}\n{decrypted}')
    ## print decrypted value
#    if decrypted.decode('utf-8') == value:
#        print(True)
#    else:
#        print(False)
    ## if decrypted value == inputvalue:
    ##      success!
    #### not actually needed !
    ## if wrong key,
    ## fernet throws exception

main()
