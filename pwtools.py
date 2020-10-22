#!/usr/bin/env python3
"""Common use functions for password management."""

import hashlib  # for hashing main password
# from getpass import getpass # for hidden input
import base64
from os import remove  # for ability to delete file in newpasss

import random  # for random gen pass
from string import punctuation, digits
from string import ascii_lowercase, ascii_uppercase
from cryptography.fernet import Fernet, InvalidToken

PASSHASH = ''  #
FILENAME = 'safepasswords'  # name of file where data are stored
FILELINES = []  # raw data from file


def hash_it(mainpassword: str) -> str:  # mainpassword= str
    """Simplified safe hashing."""
    return hashlib.sha512(mainpassword.encode('utf-8')).hexdigest()


def newpass(hashed, siteusps=None, add=True, delete=False, filename=FILENAME):
    """
    Write password(s) to file.

    hashed = hashed password
    siteusps = [site,user,password]
    delete was added for ability to remove all passwords.
    if delete == True,delete file
    """

    # checking if hashed password is ok
    check = readfile(hashed, False, filename=filename)
    if check is False:
        return
    if isinstance(hashed, str):
        hashed = hashed.encode('utf-8')
    keys = []
    for i in range(4):
        key = base64.urlsafe_b64encode(hashed[:32])
        hashed = hashed[32:]
        keys.append(key)
    if delete:
        remove(filename)
        with open(filename, 'w') as file:
            return
    if siteusps is not None:
        if not isinstance(siteusps, bytes):
            if not isinstance(siteusps, str):
                siteusps = '\t\t'.join(siteusps)
            siteusps = siteusps.encode('utf-8')
        # get number of lines already written
        already = readfileraw(return_file=True)
        if not already or not add:
            keyindex = 0
        else:
            for line in already:
                if len(line) < 4:
                    already.pop(already.index(line))
            keyindex = len(already) % 4
        fer = Fernet(keys[keyindex])
        newline = fer.encrypt(siteusps)

        mode = 'a'if add else 'w'
        with open(filename, mode) as file:
            file.write(f"{newline.decode('utf-8')}\n")


def readfileraw(return_file=False, filename=FILENAME):
    """Read plain file with stored info."""
    global FILELINES
    # if return_file or not FILELINES :
    try:
        # print(f"{FILELINES=}")
        with open(filename, "r") as file:
            data = file.read()
        FILELINES = data.split('\n')
        if FILELINES == ['']:  # empty file
            FILELINES = []
            return False
    except FileNotFoundError:
        # file doesn't exists
        return False
    if not FILELINES:
        # file exists,but is empty
        return False
    return FILELINES if return_file else True


def validatepass(password, lists):
    """Check if password has characters from all lists."""
    # not needed because string.whitespace are not in use
    # if '\t\t' in password:
    # this is used as splitter when reading file
    # it would make problems ...
    # if it will be improved,then this can be removed
    #    return False
    notfound = [True for i in range(len(lists))]  # indexes of not found lists
    for character in password:
        if sum(notfound) == 0:
            break
        for index, notfoundlists in enumerate(zip(notfound, lists)):
            # if nf[0] is True, character from that list was not used yet
            if notfoundlists[0]:
                if character in notfoundlists[1]:
                    notfound[index] = False
                    break
    # if there are some not used lists,
    # then this returns False
    return sum(notfound) == 0


def genpass(lists, minlen, maxlen):
    """
    Generate 10 random passwords.

    lists with chars needed to be used
    lists = ['adad','ASDASD','13213']
    """
    passwords = []

    while len(passwords) < 10:
        passw = ""
        if minlen < maxlen:
            passlen = random.randint(minlen, maxlen)
        else:
            passlen = minlen
        choice = ''
        for list_ in lists:
            # for equal chance of chosing char from list regardless
            # if some are significantly larger (like extrachars here)
            choice += ''.join(random.choices(list_, k=passlen))
        if len(lists) == 1:
            # len(choice) is already passlen
            # and it was already randomly selected
            passw = choice
        else:
            passw = ''.join(random.choices(choice, k=passlen))

        if validatepass(passw, lists):
            passwords.append(passw)
    return passwords


def extrachars():
    """
    Unicodes of seriously special chars.

    upside: this makes passwords basically
            immune for brute-force
    downside: majority of those chars are
            on some sites (like google)
            invalid... so unusable
    """
    ranges = [
        range(0x2801, 0x2900), range(0x11044, 0x110a8),
        range(0x10cc0, 0x10d24), range(0x10b30, 0x10b94),
        range(0x1093c, 0x109a0), range(0x10a68, 0x10f18),
        range(0x10360, 0x10a04), range(0xfb2c, 0x102fc),
        range(0xa7f8, 0xfa64), range(0x2e7c, 0xa794),
        range(0x2c24, 0x2e18), range(0x2aea, 0x2bc0),
        range(0x283c, 0x2968), range(0x2328, 0x26ac),
        range(0x5d0, 0x5eb)]

    allchars = []
    for range_of_chars in ranges:
        allchars.extend([chr(i) for i in range_of_chars
                         # only printable chars
                         if chr(i).isprintable()
                         # ascii is in another list
                         if not chr(i).isascii()
                         # spaces are usually not permitted
                         if not chr(i).isspace()])
    allchars = list(set(allchars))
    return ''.join(allchars)


def newrandompass(low=True, high=True,
                  use_digits=True, specials=True,
                  extra=True,
                  min_length=10, max_length=20):
    """Gathers info and sends it to actual generator."""
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
    return genpass(use_chars, min_length, max_length)


def decrypt(key, token):
    """Decrypt token with Fernet key."""

    # print(f"{type(key)=}")
    # print(key)
    # print(token)
    # print(f"{type(token)=}")
    try:
        fer = Fernet(key)
        decrypted_data = fer.decrypt(token)
    except InvalidToken:
        # wrong key
        return False
    except TypeError:
        # wrong key
        return False
    except ValueError:
        return False

    except Exception as ex:
        print(f'{ex=} {type(ex)=}in decrypt function at {__file__}')
        return False
    # print(f"{a=}")
    return decrypted_data


def uncode(hashed, filename=FILENAME):
    """Decode stored passwords."""
    # print(f"{thashed=}")
    if not hashed:
        return
    if isinstance(hashed, str):
        hashed = hashed.encode('utf-8')
    keys = []
    readfileraw(filename=filename)
    for i in range(4):
        key = base64.urlsafe_b64encode(hashed[:32])
        hashed = hashed[32:]

        keys.append(key)

    result = []
    for line in FILELINES:
        # if there are some shorter lines than 4
        # remove them
        if len(line) < 4:
            FILELINES.pop(FILELINES.index(line))
            continue
        k = FILELINES.index(line) % 4
        key = keys[k]
        # print(f"{l=}")
        raw = decrypt(key, line.encode('utf-8'))
        try:
            raw = raw.decode('utf-8')
        except AttributeError as exception:
            # this should NEVER happen
            print(f"error in logic (uncode function at {__file__})")
            print(exception)
            raise SystemExit
        result.append(raw)
    return result


def readfile(hashed, full=False, filename=FILENAME):
    """
    Manage reading and decoding file.

    hashed = hashed password
    full : True = read whole file
           False = just check if password matches
    modify : False = read
             True = write
    """
    # temporary stored hash
    global PASSHASH
    if not full:
        # checking if password works
        fileexists = readfileraw(filename=filename)
        if not fileexists:
            # file doesn't exists
            # it is first use
            # password needs to be written twice
            if hashed != PASSHASH:
                PASSHASH = hashed
                return None
            return True
        # FILELINES = FILELINES.split('\n')
        key = base64.urlsafe_b64encode(hashed[:32].encode('utf-8'))
        token = FILELINES[0].encode('utf-8')
        check = decrypt(key, token)

        return bool(check)
    return uncode(filename=filename)


def validate_password(password: str, filename=FILENAME, hashed=False):
    """Solely for checking if main password is ok."""
    if not password or password == password[::-1]:
        return False

    if not hashed:
        password = password[::-1]
        hash2 = hash_it(password)
    else:
        hash2 = password
    check = readfile(hash2, False, filename=filename)
    if check is None:
        # file doesn't exists, password is being created now
        return None
    if not check:
        # wrong password
        return False
    # good password,return its hash
    return hash2
