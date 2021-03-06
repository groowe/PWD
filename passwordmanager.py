#!/usr/bin/env python
"""
Terminal based password manager.

needs pwtools in same directory
"""
# ask for password
# hash sha512 it

# import hashlib  # for hashing main password # moved to pwtools
from getpass import getpass  # for hidden input
import base64
from string import punctuation
from string import digits, ascii_lowercase, ascii_uppercase
from cryptography.fernet import Fernet
# import random  # for random gen pass # .. imported from pwtools
from pwtools import extrachars, genpass, hash_it


def newrandompass():
    """ manages creating new password """
    low = ascii_lowercase
    high = ascii_uppercase
#    digits = digits
    specials = punctuation
    hebrew = extrachars()

    print('ok, generating password')
    print('what kind of password you want?')
    print(f"low = {low}\n"
          + f"high ={high}\n"
          + f"digits = {digits}\n"
          + f"specials = {specials}\n"
          + f"hebrew = {hebrew[:10]}")
    lowuse = True
    highuse = True
    digitsuse = True
    specialsuse = True
    hebrewuse = True
    print('default = use all')
    question = None
    while question is None:
        question = input('use all ? (Y/N):\n')
        if question.lower() == 'n':
            question2 = input("please specify what list NOT to use (by name)\n"
                              + "if more,separete by comma\n")
            if 'digits' in question2.lower():
                digitsuse = False
            if 'high' in question2.lower():
                highuse = False
            if 'low' in question2.lower():
                lowuse = False
            if 'special' in question2.lower():
                specialsuse = False
            if 'hebrew' in question2.lower():
                hebrewuse = False
            inuse = ''
            if lowuse:
                inuse += f'{low}\n'
            if highuse:
                inuse += f'{high}\n'
            if digitsuse:
                inuse += f'{digits}\n'
            if specialsuse:
                inuse += f'{specials}\n'
            if hebrewuse:
                inuse += f'{hebrew}\n'
            if len(inuse) == 0:
                print('you have to use some characters :)\nplease try again\n')
                digitsuse = True
                highuse = True
                lowuse = True
                specialsuse = True
                hebrewuse = True
                q = None
                continue
        elif (q.lower() != 'y' and len(q) != 0):
            print('reaction not recognized\nplease try again\n')
            q = None
            continue
        usechars = ''
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
        if hebrewuse:
            usechars += hebrew
            lists.append(hebrew)
        if len(usechars) > 100:
            print(f'chars to use:\n{usechars[:100]}')
        else:

            print(f'chars to use:\n{usechars}')
        print(f'base {len(usechars)}')
        lenpass = 5
        while lenpass < 8:
            try:
                lenpass = input('minimal length of password?\n(8 minumum:\n')
                if len(lenpass) == 0:
                    lenpass = 8
                else:
                    lenpass = int(lenpass)
            except ValueError:
                print("only digits please")
                lenpass = 5
                continue
            if lenpass < 8:
                print('ok, setting to minimum (8)')
                lenpass = 8

        lenmax = 5
        while lenmax < lenpass:
            try:
                lenmax = input("maximal length of password?\n"
                               + f"{lenpass} minumum\n")
                if len(lenmax) == 0:
                    lenmax = lenpass
                else:
                    lenmax = int(lenmax)
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
        if len(usechars) > 100:
            print(f'password chars to choose from:\n{usechars[:100]}')
        else:
            print(f'password chars to choose from:\n{usechars}')
        qq = input('{Enter} to continue, anything else to start again\n')
        if len(qq) != 0:
            q = None
            continue
    passw = ""
    while len(passw) == 0:
        print('generating passwords:\n')
        passwords = genpass(lists, lenpass, lenmax)
        for i, x in zip(range(len(passwords)), passwords):
            print(f'({i})\t{x}')
        c = input("choose password you like (its number)\n"
                  + "or enter to generate again\n")
        if len(c) == 0:
            continue
        try:
            c = int(c)
        except ValueError:
            print('invalid choice')
            continue
        if c > (len(passwords) + 1) or c < 0:
            print('invalid choice')
            continue
        passw = passwords[c]
        print(f'you chose {passw}\n')
        a = input('enter or Y to accept\n')
        if len(a) != 0 and a.lower() != 'y':
            passw = ''
            continue
    return passw


FILENAME = 'safepasswords'


def readfileraw():
    """Read plain file with stored info."""
    try:
        with open(FILENAME, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        return False
#        with open(FILENAME,'w') as f:
#            f.write('\n')
#        a = readfileraw()
    except IsADirectoryError:
        print(f'{FILENAME} is a directory!')
        raise SystemExit
    return content  # string


def readfile(hashed, full=False, modify=False):  # hashed = str
    """

    hashed = hashed password
    full : True = read whole file
           False = just check if password matches
    modify : False = read
             True = write
    """
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
        check = decrypt(key, token)
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
        uncode(hashed, filelines)  # str , [str,str,str,..]
    else:
        a = uncode(hashed, filelines, True)
        return a


def uncode(hashed, lines, returnlines=False):  # str , [str,str,str,...]
    """decode lines with hashed."""
    if type(hashed) == str:
        hashed = hashed.encode('utf-8')
    keys = []
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
    if type(lines) == str:
        lines = lines.split('\n')
    for line in lines:
        if len(line) < 4:
            lines.pop(lines.index(line))
    if type(lines) == list:
        print('site / username / password')
        if returnlines:
            ll = []
        # count = 0
        # rrrr = []
        for line in lines:
            k = lines.index(line) % 4
            key = keys[k]
            raw = decrypt(key, line.encode('utf-8'))
            try:
                raw = raw.decode('utf-8')
            except AttributeError as exception:  # should never happen
                # if this happens, file has been modified
                print(f'error in logic (uncode function)\n{exception}')
                raise SystemExit
            if not returnlines:
                # rrrr.append(raw)
                #    if raw.startswith('https://www.humblebundle.com/'):
                #        print(count,raw.split('\t')[0])
                #   else:
                #       print(count,raw)
                print(raw)
                #   count+=1
                # input()
            else:
                ll.append(raw)
        if returnlines:
            return ll
        # with open('rrrr','w') as f:
        #    for item in rrrr:
        #        f.write(item + '\n\n')
    else:
        print(type(lines))


def decrypt(key, token):
    """just decrypt token with Fernet key"""
    f = Fernet(key)
    try:
        data = f.decrypt(token)
    except:
        return False
    return data.decrypt(token)


def newpass(hashed, siteusps=None, startover=False):
    """
    hashed = str
    siteusps =  [site , us , ps ]
    startover = wipe first
    """
#    hashed = base64.urlsafe_b64encode(hashed)
    if type(hashed) == str:
        hashed = hashed.encode('utf-8')
    keys = []
    for i in range(4):
        key = base64.urlsafe_b64encode(hashed[:32])
        hashed = hashed[32:]
        keys.append(key)
    ps = 0
    if siteusps is not None:
        try:
            if type(siteusps) != list or len(siteusps) != 3:
                siteusps = None
        except:
            siteusps = None
    if siteusps is not None:
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
        site = input('name of site (ex: facebook.com):\n')  # str
        us = input('username ?:\n')
    if ps == 0:
        ps = 0
        ps2 = 1
    else:
        ps2 = ps
    while ps != ps2:
        ps = getpass(prompt='password \n(empty to generate):\n')  # str
        if len(ps) == 0:
            ps = newrandompass()
            if not ps:
                return False
            ps2 = ps
        else:
            ps2 = getpass(prompt='once again the same please:\n')
        if ps != ps2:
            print('new password doesn\'t match\ntry again')

    newline = site + '\t\t' + us + '\t\t' + ps  # str
    newline = newline.encode('utf-8')  # bytes
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
    if startover:
        mode = 'w'
    else:
        mode = 'a'
#    print(f'{startover},{mode}')
#    input()
    with open(FILENAME, mode) as f:
        f.write(newline.decode('utf-8'))
        f.write('\n')


def modify(hashed, delete=False):
    # get all data from file
    alldata = readfile(hashed, full=True, modify=True)

    sorteddata = []
    sortedpasses = []
    for i in alldata:
        a = i.split('\t\t')
        sorteddata.append([a[0], a[1]])
        sortedpasses.append(a[2])
    for x, y in zip(range(len(sorteddata)), sorteddata):
        print(f'({x}) =  {y}')

    if len(sorteddata) == 1 and delete:
        last = input("only last site/user/password saved,delete it?\n"
                     + "enter or y:\n")
        if len(last) == 0 or last.lower() == 'y':
            newpass(hashed, startover=True)
        return
    c = None
    if delete:
        dd = "delete"
    else:
        dd = 'change'
    while c is None:

        c = input(f'which password you want to {dd}? (number):\n')
        try:
            c = int(c)
            if c > (len(sorteddata) + 1) or c < 0:
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
#    start = True  # tell newpass to start over on first line
#
#    for n,x,y in zip(range(len(sorteddata)),sorteddata,sortedpasses):
#        if n != c:
#            a = x[0]
#            b = x[1]
#            newpass(hashed,[a,b,y],start)
#            start = False

#    password = 0 # newpass takes 'password = 0' as not generated yet
    start = True
    if not delete:
        a = sorteddata[c][0]
        b = sorteddata[c][1]
        newpass(hashed, [a, b, 0], True)
        start = False
    for n, x, y in zip(range(len(sorteddata)), sorteddata, sortedpasses):
        if n != c:
            a = x[0]
            b = x[1]
            newpass(hashed, [a, b, y], start)
            if start:
                start = False


def main():
    # read password
    passw = getpass(prompt='main password:\n')  # str
    # reverse
    passw2 = passw[::-1]
    # hash
    hash2 = hash_it(passw2)  #.decode('utf-8') # bytes .decode => str
    # check if correct:
    check = readfile(hash2, False)
    if not check:
        print('wrong password!')
        raise SystemExit

    c = 5
    while c != 0:
        try:
            c = int(input('\n(1) read passwd\n(2) add new passwd\n'
                    + '(3) modify\n(4) delete\n(0) exit\n'))
        except:
            raise SystemExit
        if c == 2:
            newpass(hash2)
        elif c == 1:
            readfile(hash2, True)
        elif c == 3:
            modify(hash2)
        elif c == 4:
            modify(hash2, True)
        else:
            raise SystemExit

    print('exiting..')
    return


def main_():
    # read password
    passw = getpass(prompt='main password:\n')  # str
    # reverse
    passw2 = passw[::-1]
    # hash
    hash2 = hash_it(passw2)  #.decode('utf-8') # bytes .decode => str
    # check if correct:
    check = readfile(hash2, False)
    if not check:
        print('wrong password!')
        raise SystemExit

    c = 5
    while c != 0:
        try:
            c = int(input('\n(1) read passwd\n(2) add new passwd\n'
                    + '(3) modify\n(4) delete\n(0) exit\n'))
        except:
            raise SystemExit
        if c == 2:
            newpass(hash2)
        elif c == 1:
            readfile(hash2, True)
        elif c == 3:
            modify(hash2)
        elif c == 4:
            modify(hash2, True)
        else:
            raise SystemExit

    print('exiting..')
    return


if __name__ == '__main__':
    main_()
