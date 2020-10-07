#!/usr/bin/env python3

import hashlib # for hashing main password
#from getpass import getpass # for hidden input
import base64
from cryptography.fernet import Fernet,InvalidToken
import random # for random gen pass
from string import punctuation,digits
from string import ascii_lowercase,ascii_uppercase
from os import remove # for ability to delete file in newpasss
passhash = '' #
filename = 'safepasswords' # name of file where data are stored
filelines = [] # raw data from file

def hash_it(mainpassword:str) -> str: # mainpassword= str
    return hashlib.sha512(mainpassword.encode('utf-8')).hexdigest()

def newpass(hashed,siteusps=None,add=True,delete=False):
    """
    writes down
    hashed = hashed password
    siteusps = [site,user,password]
    if delete == True,delete file
    # delete was added for ability to remove all passwords
    """
    if type(hashed) == str:
        hashed = hashed.encode('utf-8')
    keys = []
    for i in range(4):
        key = base64.urlsafe_b64encode(hashed[:32])
        hashed = hashed[32:]
        keys.append(key)
    if delete:
        remove(filename)
        open(filename,'w')
        return
    if siteusps != None:
        if type(siteusps) != bytes:
            if type(siteusps) != str:
                siteusps = '\t\t'.join(siteusps)
            siteusps = siteusps.encode('utf-8')
        # get number of lines already written
        already = readfileraw(return_file=True)
        if not already or not add:
            l = 0
        else:
            for line in already:
                if len(line) < 4:
                    already.pop(already.index(line))
            l = len(already) % 4
        F = Fernet(keys[l])
        newline = F.encrypt(siteusps)

        mode = 'a'if add else 'w'
        with open(filename,mode) as f:
            f.write(f"{newline.decode('utf-8')}\n")

def readfileraw(return_file=False):
    """reading plain file with stored info"""
    global filelines
    #if return_file or not filelines :
    try:
        #print(f"{filelines=}")
        with open(filename,"r") as f:
            a = f.read()
        filelines = a.split('\n')
        if filelines == ['']:# empty file
            filelines = []
            return False
    except FileNotFoundError:
        # file doesn't exists
        return False
    if not filelines:
        # if
        return False
    return filelines if return_file else True

def validatepass(password,lists):
    """
    check if password has characters from all lists
    """
    # not needed because string.whitespace are not in use
    #if '\t\t' in password:
        # this is used as splitter when reading file
        # it would make problems ...
        # if it will be improved,then this can be removed
    #    return False
    for list in lists:
        used = False
        for character in password:
            if character in list:
                used = True
                break
        if not used:
            return False
    return True

def genpass(lists,minlen,maxlen):
    """
    generates random password
    lists with chars needed to be used
    lists = ['adad','ASDASD','13213']
    """
    passwords = []

    while len(passwords) < 10:
        passw = ""
        if minlen < maxlen:
            passlen = random.randint(minlen,maxlen)
        else:
            passlen = minlen
        choice = ''
        for l in lists:
            # for equal chance of chosing char from list regardless
            # if some are significantly larger (like extrachars here)
            choice += ''.join(random.choices(l,k=passlen))
        if len(lists) == 1:
            passw = choice
        else:
            passw = ''.join(random.choices(choice,k=passlen))

        if validatepass(passw,lists):
            passwords.append(passw)
    return passwords

def extrachars():
    """
    unicodes of seriously special chars
    upside: this makes passwords basically
            immune for brute-force
    downside: majority of those chars are
            on some sites (like google)
            invalid... so unusable
    """
    b = range(0x2801,0x2900)
    c = range(0x11044,0x110a8)
    d = range(0x10cc0, 0x10d24)
    e = range(0x10b30, 0x10b94)
    f = range(0x1093c, 0x109a0 )
    g = range(0x10a68 ,0x10f18)
    h = range(0x10360 ,0x10a04)
    i = range(0xfb2c,0x102fc)
    j = range(0xa7f8 ,0xfa64)
    k = range(0x2e7c ,0xa794)
    l = range(0x2c24 , 0x2e18)
    m = range(0x2aea ,0x2bc0)
    n = range(0x283c , 0x2968)
    o = range(0x2328 ,0x26ac)
    p = range(0x5d0,0x5eb)
    r = [b,c,d,e,f,g,h,i,j,k,l,m,n,o,p]
    allch= []
    for ia in r:
        allch.extend([chr(i) for i in ia
            if chr(i).isprintable() # only printable chars
            if not chr(i).isascii() # ascii is in another list
            if not chr(i).isspace()]) # spaces are usually not permitted
    allch=list(set(allch))
    return ''.join(allch)

def newrandompass(low=True,high=True,
                use_digits=True,specials=True,
                extra=True,
                min_length=10,max_length=20):
    """
    builds
    """
    use_chars = []
    if low:
        use_chars.append(ascii_lowercase)
    if high:
        use_chars.append(ascii_uppercase)
    if use_digits:
        use_chars.append(digits)
    if specials:
        use_chars.append(punctuation)
    # up to here 94 characters
    # 94**8 = 6095689385410816 = 6.095689e+15
    if extra:
        use_chars.append(extrachars())
    # if used all, it is 48741 characters
    # that would be for password with length 8 characters
    # 48741**8 = 31853376985417679534107315657041386721 ==  3.185338e+37
    return genpass(use_chars,min_length,max_length)

def decrypt(key,token):
    """decrypt token with Fernet key"""
    f = Fernet(key)
    #print(f"{type(key)=}")
    #print(key)
    #print(token)
    #print(f"{type(token)=}")
    try:
        a = f.decrypt(token)
    except InvalidToken:
        # wrong key
        return False
    except Exception as Ex:
        print(f'{Ex=} {type(Ex)=}in decrypt function at {__file__}')
        return False
    #print(f"{a=}")
    return a

def uncode(hashed):
    """
    decode stored passwords
    """
    #print(f"{thashed=}")
    if not hashed:
        return
    if type(hashed) == str:
        hashed = hashed.encode('utf-8')
    keys = []
    readfileraw()
    for i in range(4):
        key = base64.urlsafe_b64encode(hashed[:32])
        hashed = hashed[32:]

        keys.append(key)
        #print(len(keys),key)

    result = []
    for l in filelines:
        # if there are some shorter lines than 4
        # remove them
        if len(l) < 4:
            filelines.pop(filelines.index(l))
            continue
        k = filelines.index(l) % 4
        key = keys[k]
        #print(f"{l=}")
        raw = decrypt(key,l.encode('utf-8'))
        try:
            raw = raw.decode('utf-8')
        except AttributeError as exception:
            # this should NEVER happen
            print(f"error in logic (uncode function)\n{exception}")
            raise SystemExit
        result.append(raw)
    return result

def readfile(hashed,full=False):
    """
    hashed = hashed password
    full : True = read whole file
           False = just check if password matches
    modify : False = read
             True = write
    """
    # temporary stored hash
    global passhash
    if not full:
        # checking if password works
        fileexists = readfileraw()
        if not fileexists:
            # file doesn't exists
            # it is first use
            # password needs to be written twice
            if hashed != passhash:
                passhash = hashed
                return None
            return True
        #filelines = filelines.split('\n')
        key = base64.urlsafe_b64encode(hashed[:32].encode('utf-8'))
        token = filelines[0].encode('utf-8')
        check = decrypt(key,token)

        return bool(check)
    return uncode()

def validate_password(password:str):
    """
    solely for checking if main password is ok
    """
    password = password[::-1]
    hash2 = hash_it(password)
    check = readfile(hash2,False)
    if check == None:
        return None
    if not check:
        return False
    return hash2
