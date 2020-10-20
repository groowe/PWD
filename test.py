#!/usr/bin/env python3
import unittest

import hashlib
import random
from string import punctuation, digits
from string import ascii_lowercase, ascii_uppercase
from pwtools import hash_it, validatepass, extrachars, genpass
extrachars = extrachars()
l_string = [ascii_lowercase,
            ascii_uppercase,
            punctuation,
            extrachars,
            digits]


class Testpwtools(unittest.TestCase):

    def test_hash_it(self):
        for value in l_string:
            passw = ''.join(random.choices(value, k=random.randint(20, 100)))
            self.assertEqual(hash_it(passw),
                             hashlib.sha512(
                                    passw.encode('utf-8')
                                ).hexdigest())
            self.assertFalse(validatepass(passw, l_string))

    def test_validatepass(self):

        for value in l_string:
            self.assertTrue(validatepass(value, [value]))
            self.assertFalse(validatepass(value, [ll for ll in l_string
                                                  if ll != value]))

        self.assertFalse(validatepass('aa', [ascii_lowercase, digits]))
        self.assertFalse(validatepass('dWGk=k𐇙~췌oVFoQW', l_string))
        self.assertFalse(validatepass('4WG04=𐇙~췌VF9QW', l_string))
        self.assertFalse(validatepass('4d0k4=k𐇙~췌oo9', l_string))
        self.assertFalse(validatepass('4dWG0k4k췌oVFo9QW', l_string))
        self.assertFalse(validatepass('4dWG0k4=k~oVFo9QW', l_string))
        self.assertTrue(validatepass('4dWG0k4=k𐇙~췌oVFo9QW', l_string))

    def test_genpass(self):
        for i in range(10):
            minlen, maxlen = i*2+5, i*3+5
            for value in genpass(l_string, minlen, maxlen):
                self.assertTrue(minlen <= len(value) <= maxlen)
                self.assertTrue(validatepass(value, l_string))


if __name__ == '__main__':
    unittest.main()
