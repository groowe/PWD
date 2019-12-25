# ask for password
# hash sha512 it

import hashlib # for hashing main password
from getpass import getpass # for hidden input
import base64
from cryptography.fernet import Fernet
import random # for random gen pass


def newrandompass():
    low = "abcdefghijklmnopqrstuvwxyz"
    high = low.upper()
    digits = "0123456789"
    specials ="!@#$%^&*()?"
    print('ok, generating password')
    print('what kind of password you want?')
    print(f'low = {low}\nhigh ={high}\ndigits = {digits}\nspecials = {specials}')
    lowuse = True
    highuse = True
    digitsuse = True
    specialsuse = True
    print('default = use all')
    q = None
    while q == None:
        q = input('use all ? (Y/N):\n')
        if q.lower() == 'n':
            q2 = input('please specify what list NOT to use (by name)\nif more,separete by comma\n')
            if 'digits' in q2.lower():
                digitsuse = False
            if 'high' in q2.lower():
                highuse = False
            if 'low' in q2.lower():
                lowuse = False
            if 'special' in q2.lower():
                specialsuse = False
            inuse = ''
            if lowuse:
                inuse += f'{low}\n'
            if highuse:
                inuse += f'{high}\n'
            if digitsuse:
                inuse += f'{digits}\n'
            if specialsuse:
                inuse += f'{specials}\n'
            if len(inuse) == 0:
                print('you have to use some characters :)\nplease try again\n')
                digitsuse = True
                highuse = True
                lowuse = True
                specialsuse = True
                q = None
                continue
        elif (q.lower() != 'y' and len(q) != 0):
            print('reaction not recognized\nplease try again\n')
            q = None
            continue
        usechars =''
        lists = []
        if lowuse:
            usechars += low
            lists.append(low)
        if highuse:
            usechars += high
            lists.append(high)
        if digitsuse:
            usechars += digits
            lists.append(digits)
        if specialsuse:
            usechars += specials
            lists.append(specials)
        print(f'chars to use:\n{usechars}')
        lenpass = 5
        while lenpass < 8:
            try:
                lenpass = int(input('minimal length of password?\n(8 minumum:\n'))
            except ValueError:
                print("only digits please")
                lenpass= 5
                continue
            if lenpass < 8:
                print('ok, setting to minimum (8)')
                lenpass = 8

        lenmax = 5
        while lenmax < lenpass:
            try:
                lenmax = int(input(f'maximal length of password?\n{lenpass} minumum\n'))
            except ValueError:

                print("only digits please\n")
                lenmax = 5
                continue
            if lenmax < lenpass:
                print(f'setting fixed length {lenpass}\n')
                lenmax = lenpass

        print('recap')
        print(f'minimal length of password = {lenpass}')
        print(f'maximal length of password = {lenmax}')
        print(f'password chars to choose from:\n{usechars}')
        qq = input('{Enter} to continue, anything else to start again\n')
        if len(qq) != 0:
            q = None
            continue
    passw = ""
    while len(passw) == 0:
        print('generating passwords:\n')
        passwords  = genpass(usechars,lists,lenpass,lenmax)
        for i,x in zip(range(len(passwords)),passwords):
            print(f'({i})\t{x}')
        c = input('choose password you like (its number)\n or enter to generate again\n')
        if len(c) == 0:
            continue
        try:
            c = int(c)
        except ValueError:
            print('invalid choice')
            continue
        if c > (len(passwords) +1) or c < 0:
            print('invalid choice')
            continue
        passw = passwords[c]
        print(f'you chose {passw}\n')
        a = input('enter or Y to accept\n')
        if len(a) != 0 and a.lower() != 'y':
            passw= ''
            continue
    return passw

def validatepass(passw,lists):
    for i in lists:
        init = False
        for a in i:
            if a in passw:
                init = True
        if not init:
            return False
    return True

def genpass(chars,lists,minlen,maxlen):
    # chars to choose from
    # lists needed to be used from

    # generate 10 passwords:
    passwords = []
    while len(passwords) < 10:
        passw = ""
        if minlen < maxlen:
            passlen = random.randint(minlen,maxlen)
        else:
            passlen = minlen
        while len(passw) < passlen:
            passw+= chars[random.randint(0,len(chars)-1)]
        if validatepass(passw,lists):
            passwords.append(passw)
    return passwords

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

def readfile(hashed,full=False,modify=False): # hashed = str
    if not full:
        filelines = readfileraw()
        if not filelines:
            print('first run')
            p = getpass('write your password again:\n')
            p2 = p[::-1]
            hash2 = hash_it(p2)
            if hashed == hash2:
                print('your master password stored')
                return True
            print('passwords doesn\'t match')
            return False
        filelines = filelines.split('\n')
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
    if not modify:
        uncode(hashed,filelines) # str , [str,str,str,..]
    else:
        a = uncode(hashed,filelines,True)
        return a


def uncode(hashed,lines,returnlines = False): # str , [str,str,str,...]
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
        print('site / username / password')
        if returnlines:
            ll = []
        for line in lines:
            k = lines.index(line) % 4
            key = keys[k]
#            print(lines[i])
#            print(len(lines[i]))
            raw = decrypt(key,line.encode('utf-8'))
#            print('raw')
            try:

                raw = raw.decode('utf-8')
            except AttributeError as exception: # should never happen
                print(f'error in logic (uncode function)\n{exception}')
                raise SystemExit

            if not returnlines:
                print(f'{raw}')
            else:
                ll.append(raw)
        if returnlines:
            return ll

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

def newpass(hashed,siteusps=None,startover= False): # hashed = str , siteusps =  [site , us , ps ] , startover = wipe first
#    hashed = base64.urlsafe_b64encode(hashed)
    if type(hashed) == str:
        hashed = hashed.encode('utf-8')
    keys= []
    for i in range(4):
        key = base64.urlsafe_b64encode(hashed[:32])
        hashed = hashed[32:]
        keys.append(key)
#    print('keys:')
##### for debug :
#    for i in keys:
#        print(i)
################
    ps = 0
    if siteusps != None:
        try:
            if type(siteusps) != list or len(siteusps) != 3:
                siteusps = None
        except:
            siteusps = None
    if siteusps != None:
        site = siteusps[0]
        us = siteusps[1]
        ps = siteusps[2]
########### for debug :  ######################
#        print(f'site = {site}\ntype site = {type(site)}')
#        print(f'us = {us}\n type us = {type(us)}')
#        print(f'ps = {ps}\ntypeps = {type(ps)}')
#        print(f'siteusps = {siteusps}\ntype siteusps = {type(siteusps)}')
###############################################
    else:
        site = input('name of site (ex: facebook.com):\n') # str
        us = input('username ?:\n')
    if ps == 0:
        ps = 0
        ps2 = 1
    else:
        ps2 = ps
    while ps != ps2:
        ps = getpass(prompt='password \n(empty to generate):\n') # str
        if len(ps) == 0:
            ps = newrandompass()
            if not ps:
                return False
            ps2 = ps
        else:
            ps2 = getpass(prompt='once again the same please:\n')
        if ps != ps2:
            print('new password doesn\'t match\ntry again')

    newline = site + '\t\t' + us + '\t\t' +ps # str
    newline = newline.encode('utf-8') # bytes
    already = readfileraw()
    if not already or startover:
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
    if startover:
        mode = 'w'
    else:
        mode = 'a'
#    print(f'{startover},{mode}')
#    input()
    with open(filename,mode) as f:
        f.write(newline.decode('utf-8'))
        f.write('\n')

def modify(hashed,delete=False):
    # get all data from file
    alldata = readfile(hashed,full=True,modify=True)
    
    sorteddata = []
    sortedpasses = []
    for i in alldata:
        a = i.split('\t\t')
        sorteddata.append([a[0],a[1]])
        sortedpasses.append(a[2])
    for x,y in zip(range(len(sorteddata)),sorteddata):
        print(f'({x}) =  {y}')

    if len(sorteddata) == 1 and delete:
        last = input('only last site/user/password saved,delete it?\nenter or y:\n')
        if len(last) == 0 or last.lower() == 'y':
            newpass(hashed,startover=True)
        return
    c = None
    if delete:
        dd = "delete"
    else:
        dd = 'change'
    while c == None:

        c = input(f'which password you want to {dd}? (number):\n')
        try:
            c = int(c)
            if c > ( len(sorteddata) +1) or c < 0:
                print('only numbers 0 - {len(sorteddata) -1}!')
                c = None
                continue
        except ValueError:
            print('only numbers please')
            c = None
            continue
        print(f'{sorteddata[c]}')
        a = input('correct?  (enter or y)\nexit to abort\n')
        if not (len(a) == 0 or a.lower() == 'y'):
            if a.lower() == 'exit':
                return
            c = None
    # c == index of password to change
#    print(f'{sorteddata[c]}')
#    c = int(c)
#    print(f'{c} {type(c)}')
#    input()
#    return
    start = True  # tell newpass to start over on first line

    for n,x,y in zip(range(len(sorteddata)),sorteddata,sortedpasses):
        if n != c:
            a = x[0]
            b = x[1]
            newpass(hashed,[a,b,y],start)
            start = False
    if delete:
        return
    a = sorteddata[c][0]
    b = sorteddata[c][1]
#    password = 0 # newpass takes 'password = 0' as not generated yet
    newpass(hashed,[a,b,0])


def main():
    passw = getpass(prompt='main password:\n') # str
#    hashed = hash_it(passw)#.decode('utf-8') # bytes .decode => str
    passw2 = passw[::-1]
    hash2 = hash_it(passw2)#.decode('utf-8') # bytes .decode => str
    # check if passw is correct:
    check = readfile(hash2,False)
    if not check:
        print('wrong password!')
        raise SystemExit

    c = 5
    while c != 0:
        try:
            c = int(input('\n(1) read passwd\n(2) add new passwd\n'+
                    '(3) modify\n(4) delete\n(0) exit\n'))
        except:
            raise SystemExit
        if c == 2:
            newpass(hash2)
        elif c == 1:
            readfile(hash2,True)
        elif c == 3:
            modify(hash2)
        elif c == 4:
            modify(hash2,True)
        else:
            raise SystemExit

    print('exiting..')
    return
if __name__ == '__main__':
    main()


