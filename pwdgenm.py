# Create a program that generates a password of 6 random
# alphanumeric characters in the range
# abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?
import random
rangepass = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"#!@#$%^&*()?"

low = "abcdefghijklmnopqrstuvwxyz"
high = low.upper()
digits = "0123456789"
specials ="!@#$%^&*()?"

def valid(passw):
    l = 0
    h = 0
    d = 0
    s = 0
    for a in low:
        if a in passw:
            l+=1
    if l == 0:
        return False
    for a in high:
        if a in passw:
            h+=1
    if h ==0:
        return False
    for a in digits:
        if a in passw:
            d+=1
    if d ==0:
        return False

#    for a in specials:

#        if a in passw:
#            s+=1
#    if s == 0:
#        return False
    return True

def gen():
    count = 0
    while count < 10:
        passw = ""
        passlen = 8
#        passlen = random.randint(12,20)
        while len(passw) < passlen:
            passw+= rangepass[random.randint(0,len(rangepass)-1)]
        if valid(passw):

            print(passw)
            w(passw)
            count+=1


"""
# their solution:
import random
     
characters = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
chosen = random.sample(characters, 6)
password = "".join(chosen)
print(password)

"""
def w(passw):

    with open("fbt.txt","a+") as f:
        f.write(passw + "\n")

gen()
