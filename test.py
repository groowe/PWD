#!/usr/bin/env python3
import unittest

import hashlib
import random
from string import punctuation, digits
from string import ascii_lowercase, ascii_uppercase
from pwtools import hash_it, validatepass, extrachars, genpass, decrypt
from pwtools import newpass, readfileraw, newrandompass, uncode, readfile
from pwtools import validate_password
from os import remove

FILENAME = 'test_safepasswords'

extrachars = extrachars()
l_string = [ascii_lowercase,
            ascii_uppercase,
            punctuation,
            extrachars,
            digits]
'some more unittests'

class Testpwtools(unittest.TestCase):

    def test_hash_it(self):
        for value in l_string:
            passw = ''.join(random.choices(value, k=random.randint(20, 100)))
            self.assertEqual(hash_it(passw),
                             hashlib.sha512(
                                 passw.encode('utf-8')
                                ).hexdigest())

    def test_validatepass(self):
        for value in l_string:
            passw = ''.join(random.choices(value, k=random.randint(20, 100)))
            self.assertTrue(validatepass(passw, [value]))
            self.assertFalse(validatepass(passw, l_string))

        for i in range(10):
            passw = ''.join([''.join(random.choices(value, k=i+5))
                             for value in l_string])
            self.assertTrue(validatepass(passw, l_string))
            self.assertFalse(validatepass(passw, l_string+[' ']))
            for ls in l_string:
                l_s = [value for value in l_string if value != ls]
                passw = ''.join([''.join(random.choices(value, k=i+5))
                                 for value in l_s])
                self.assertFalse(validatepass(passw, l_string))
                self.assertTrue(validatepass(passw, l_s))

    def test_genpass(self):
        for i in range(10):
            minlen, maxlen = i*2+5, i*3+5
            for value in genpass(l_string, minlen, maxlen):
                self.assertTrue(minlen <= len(value) <= maxlen)
                self.assertTrue(validatepass(value, l_string))
            ls = random.choice(l_string)
            l_s = [value for value in l_string if value != ls]
            for value in genpass(l_s, minlen, maxlen):
                self.assertTrue(minlen <= len(value) <= maxlen)
                self.assertTrue(validatepass(value, l_s))
                self.assertFalse(validatepass(value, l_string))

    def test_validate_password(self):
        self.assertEqual(validate_password('', filename=FILENAME), False)
        self.assertEqual(validate_password('eaae', filename=FILENAME), False)
        self.assertEqual(validate_password('af', filename=FILENAME), None)

    def test_newpass(self):
        pass

    def test_readfileraw(self):
        pass

    def test_newrandompass(self):
        pass

    def test_decrypt(self):
        pass

    def test_uncode(self):
        pass

    def test_readfile(self):
        pass


if __name__ == '__main__':
    unittest.main()
