#!/usr/bin/env python3
import unittest

import hashlib
import base64
import random
import time
from string import punctuation, digits
from string import ascii_lowercase, ascii_uppercase
from os import remove
from cryptography.fernet import Fernet

from pwtools import hash_it, validatepass, extrachars, genpass, decrypt
from pwtools import newpass, readfileraw, newrandompass, uncode, readfile
from pwtools import validate_password
from new_gen import MyWindow

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk

FILENAME = 'test_safepasswords'

extrachars = extrachars()
l_string = [ascii_lowercase,
            ascii_uppercase,
            punctuation,
            extrachars,
            digits]
'some more unittests'



def password_to_file(filename=FILENAME):

    passw = random.choice(newrandompass())
    hashed = hash_it(passw)
    siteusps = ['\t\t'.join(['site', 'user', 'password'])]*10
    keys = []
    for i in range(4):
        key = base64.urlsafe_b64encode(
                hashed[i*32:(i+1)*32].encode('utf-8')
                )
        keys.append(key)

    fers = [Fernet(key)for key in keys]
    new = True
    for i, siteusp in enumerate(siteusps):
        fer = fers[i % 4]
        newline = fer.encrypt(siteusp.encode('utf-8'))
        with open(filename, 'w' if new else 'a') as file:
            file.write(f"{newline.decode('utf-8')}\n")
        if new:
            new = False
    return {'password': passw[::-1], 'siteusps': siteusps, 'hashed': hashed}


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

    def test_newrandompass(self):
        vars_ = [newrandompass(low=False),
                 newrandompass(high=False),
                 newrandompass(specials=False),
                 newrandompass(extra=False),
                 newrandompass(use_digits=False)]
        for var, ls in zip(vars_, l_string):
            l_s = [value for value in l_string if value != ls]
            self.assertEqual(len(var), 10)
            for data in var:
                self.assertTrue(validatepass(data, l_s))
                self.assertTrue(10 <= len(data) <= 20)
                self.assertFalse(validatepass(data, l_string))

    def test_readfileraw(self):
        self.assertFalse(readfileraw(filename=FILENAME))
        info = "plain file"
        with open(FILENAME, 'w') as file:
            file.write(info)
        self.assertTrue(readfileraw(filename=FILENAME))
        self.assertEqual(readfileraw(return_file=True, filename=FILENAME),
                         [info])
        remove(FILENAME)

    def test_decrypt(self):
        hashed = hash_it('userpassword').encode('utf-8')
        siteusps = '\t\t'.join(['site', 'user', 'password']).encode('utf-8')
        key = base64.urlsafe_b64encode(hashed[:32])
        fer = Fernet(key)
        token = fer.encrypt(siteusps)
        key_ = base64.urlsafe_b64encode(hashed[32:64])
        fer_ = Fernet(key_)
        token_ = fer_.encrypt(siteusps)

        self.assertEqual(decrypt(key, token), siteusps)
        self.assertEqual(decrypt(key_, token_), siteusps)
        self.assertFalse(decrypt(key_, token))
        self.assertFalse(decrypt(key, token_))
        self.assertFalse(decrypt('\t\t', token_))
        self.assertFalse(decrypt(key, '\t\t'))
        self.assertFalse(decrypt('\t\t', '\t\t'))
        self.assertRaises(TypeError, decrypt)

    def test_uncode(self):
        self.assertRaises(TypeError, uncode)
        self.assertRaises(SystemExit, uncode, '\t\t', filename=FILENAME)
        new = password_to_file()
        # passw = new['password']
        siteusps = new['siteusps']
        hashed = new['hashed']
        self.assertEqual(uncode(hashed, filename=FILENAME), siteusps)
        if readfileraw(filename=FILENAME):
            remove(FILENAME)

    def test_readfile(self):
        self.assertRaises(TypeError, readfile)
        new = password_to_file()

        passw = new['password']
        siteusps = new['siteusps']
        hashed = new['hashed']
        self.assertFalse(readfile(passw, full=False, filename=FILENAME))
        self.assertTrue(readfile(hashed, full=False, filename=FILENAME))
        self.assertEqual(readfile(hashed, full=True, filename=FILENAME),
                         siteusps)
        if readfileraw(filename=FILENAME):
            remove(FILENAME)

    def test_validate_password(self):
        if readfileraw(filename=FILENAME):
            remove(FILENAME)
        self.assertEqual(validate_password('', filename=FILENAME), False)
        self.assertEqual(validate_password('eaae', filename=FILENAME), False)
        self.assertEqual(validate_password('af', filename=FILENAME), None)

    def test_newpass(self):
        if readfileraw(filename=FILENAME):
            remove(FILENAME)
        new = password_to_file()
        # passw = new['password']
        siteusps = new['siteusps']
        hashed = new['hashed']
        new_ps = newrandompass()

        for ps in new_ps:
            siteusps_ = ['site', 'user', ps]
            newpass(hashed, siteusps_, filename=FILENAME)
            siteusps.append('\t\t'.join(siteusps_))
            self.assertEqual(readfile(hashed, full=True, filename=FILENAME),
                             siteusps)
        self.assertEqual(newpass(hashed, delete=True, filename=FILENAME),
                         None)
        self.assertFalse(newpass('tfds', filename=FILENAME))
        remove(FILENAME)


# Stolen from Kiwi
# https://unpythonic.blogspot.com/2007/03/unit-testing-pygtk.html
def refresh_gui(delay=0):
    while Gtk.events_pending():
        # Gtk.main_iteration_do(block=False)
        Gtk.main_iteration_do(False)
        # print(0)
    time.sleep(delay)
    return True

class TestMyWindow(unittest.TestCase):
    def test_progressbar(self):
        win = MyWindow(file_=FILENAME)
        # win.show_all()
        # Gtk.main()
        self.assertEqual(win._progressbar.get_fraction(), 0.0)
        win._progressbar.set_fraction(0.5)
        self.assertEqual(win._progressbar.get_fraction(), 0.5)
        self.assertTrue(win._on_timeout())
        self.assertEqual(win._progressbar.get_fraction(), 0.501)
        win._progressbar.set_fraction(0.999)
        # self.assertRaises(ValueError, win._on_timeout)
        print("expecting following error:")
        print("Gtk-CRITICAL ** gtk_main_quit: assertion 'main_loops != NULL' failed")
        # self.assertRaises(Gtk-CRITICAL, win._on_timeout)
        self.assertRaises(SystemExit, win._on_timeout)
        # self.assertEqual(win._progressbar.get_fraction(), 1)

    def test_main_page(self):
        win = MyWindow(file_=FILENAME)
        self.assertEqual(win.file_, FILENAME)
        self.assertEqual(win._entry.get_text(), "password")
        self.assertTrue(win._hide_pass.get_active())
        self.assertFalse(win._entry.get_visibility())
        self.assertFalse(win._data_refresh())
        data = password_to_file()
        self.assertTrue(readfileraw(filename=FILENAME))
        # print(f'{data=}')
        passw = data['password']
        siteusps = data['siteusps']
        hashed = data['hashed']
        win._entry.set_text(passw)
        self.assertEqual(win._entry.get_text(), passw)
        self.assertEqual(win._hashed, '')
        # win._button_clicked(win._entry, "password")
        self.assertEqual(win._notebook.get_n_pages(), 2)
        # self.assertEqual(win._notebook.get_current_page(), -1)

        win._button.clicked()
        self.assertTrue(refresh_gui())
        self.assertEqual(win._hashed, hashed)
        self.assertEqual(win._data, siteusps)
        # self.assertEqual(win._notebook.get_current_page(), -1)

    def test_pass_add_pass_page(self):

        win = MyWindow(file_=FILENAME)
        data = password_to_file()
        self.assertEqual(win._passpage.get_n_pages(), 6)
        passw = data['password']
        siteusps = data['siteusps']
        hashed = data['hashed']
        win._entry.set_text(passw)
        win._button.clicked()
        self.assertTrue(refresh_gui())
        self.assertEqual(win._data, siteusps)
        self.assertEqual(win._entry_username.get_text(),
                         win._entry_page.get_text())
        self.assertEqual(win._entry_password.get_text(),
                         win._entry_page.get_text())
        self.assertEqual(win._entry_password.get_text(), '')
        win._entry_page.set_text('123')
        win._entry_password.set_text('456')
        # win._last_entry_username = ""
        save_button = win._add_password_page.get_child_at(0, 0)
        save_button.clicked()
        self.assertTrue(refresh_gui())
        self.assertEqual(win._data, siteusps)
        win._entry_username.set_text('789')
        save_button.clicked()
        self.assertTrue(refresh_gui())
        self.assertFalse(win._data == siteusps)
        siteusps.append('123\t\t789\t\t456')
        self.assertEqual(win._data, siteusps)
        # self.assertEqual(win._passpage.get_current_page(), -1)



if __name__ == '__main__':
    unittest.main()
