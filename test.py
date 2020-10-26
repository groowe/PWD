#!/usr/bin/env python3
import unittest

import hashlib
import base64
import random
import time
import sys

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
COUNTER = 0


def function_name():
    global COUNTER
    COUNTER += 1
    # print(f"running {function_name()} {COUNTER}")
    return sys._getframe().f_back.f_code.co_name


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
    siteusps = []
    rpd = []
    for i in range(5):
        rpd.extend(newrandompass(min_length=10, max_length=10))
    # print(rpd)
    for i in range(10):
        # su = newrandompass(min_length=10, max_length=10)[:4]
        # pss = newrandompass(min_length=10+i, max_length=10+i)[0]
        siteusps.append('\t\t'.join([rpd.pop(), rpd.pop(), (rpd.pop()+rpd.pop()+rpd.pop())[:10+(i*2)]]))
        # print(siteusps[-1])
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
    def setUp(self):
        # print(f"running {function_name()} {COUNTER}")
        if readfileraw(filename=FILENAME):
            remove(FILENAME)

    def tearDown(self):
        # print(f"running {function_name()} {COUNTER}")
        if readfileraw(filename=FILENAME):
            remove(FILENAME)

    def test_hash_it(self):
        print(f"running {function_name()} {COUNTER}")
        for value in l_string:
            self.passw = ''.join(random.choices(value, k=random.randint(20, 100)))
            self.assertEqual(hash_it(self.passw),
                             hashlib.sha512(
                                 self.passw.encode('utf-8')
                                ).hexdigest())

    def test_validatepass(self):
        print(f"running {function_name()} {COUNTER}")
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
        print(f"running {function_name()} {COUNTER}")
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
        print(f"running {function_name()} {COUNTER}")
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
        print(f"running {function_name()} {COUNTER}")
        self.assertFalse(readfileraw(filename=FILENAME))
        info = "plain file"
        with open(FILENAME, 'w') as file:
            file.write(info)
        self.assertTrue(readfileraw(filename=FILENAME))
        self.assertEqual(readfileraw(return_file=True, filename=FILENAME),
                         [info])

    def test_decrypt(self):
        print(f"running {function_name()} {COUNTER}")
        self.hashed = hash_it('userpassword').encode('utf-8')
        self.siteusps = '\t\t'.join(['site', 'user', 'password']).encode('utf-8')
        key = base64.urlsafe_b64encode(self.hashed[:32])
        fer = Fernet(key)
        token = fer.encrypt(self.siteusps)
        key_ = base64.urlsafe_b64encode(self.hashed[32:64])
        fer_ = Fernet(key_)
        token_ = fer_.encrypt(self.siteusps)

        self.assertEqual(decrypt(key, token), self.siteusps)
        self.assertEqual(decrypt(key_, token_), self.siteusps)
        self.assertFalse(decrypt(key_, token))
        self.assertFalse(decrypt(key, token_))
        self.assertFalse(decrypt('\t\t', token_))
        self.assertFalse(decrypt(key, '\t\t'))
        self.assertFalse(decrypt('\t\t', '\t\t'))
        self.assertRaises(TypeError, decrypt)

    def test_uncode(self):
        print(f"running {function_name()} {COUNTER}")
        self.assertRaises(TypeError, uncode)
        self.assertRaises(SystemExit, uncode, '\t\t', filename=FILENAME)
        new = password_to_file()
        # self.passw = new['password']
        self.siteusps = new['siteusps']
        self.hashed = new['hashed']
        self.assertEqual(uncode(self.hashed, filename=FILENAME), self.siteusps)

    def test_readfile(self):
        print(f"running {function_name()} {COUNTER}")
        self.assertRaises(TypeError, readfile)
        new = password_to_file()

        self.passw = new['password']
        self.siteusps = new['siteusps']
        self.hashed = new['hashed']
        self.assertFalse(readfile(self.passw, full=False, filename=FILENAME))
        self.assertTrue(readfile(self.hashed, full=False, filename=FILENAME))
        self.assertEqual(readfile(self.hashed, full=True, filename=FILENAME),
                         self.siteusps)

    def test_validate_password(self):
        print(f"running {function_name()} {COUNTER}")
        self.assertEqual(validate_password('', filename=FILENAME), False)
        self.assertEqual(validate_password('eaae', filename=FILENAME), False)
        self.assertEqual(validate_password('af', filename=FILENAME), None)


    def test_newpass(self):
        print(f"running {function_name()} {COUNTER}")
        if readfileraw(filename=FILENAME):
            remove(FILENAME)
        new = password_to_file()
        # self.passw = new['password']
        self.siteusps = new['siteusps']
        self.hashed = new['hashed']
        new_ps = newrandompass()

        for ps in new_ps:
            self.siteusps_ = ['site', 'user', ps]
            newpass(self.hashed, self.siteusps_, filename=FILENAME)
            self.siteusps.append('\t\t'.join(self.siteusps_))
            self.assertEqual(readfile(self.hashed, full=True, filename=FILENAME),
                             self.siteusps)
        self.assertEqual(newpass(self.hashed, delete=True, filename=FILENAME),
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
    def setUp(self):
        # print(f"running {function_name()} {COUNTER}")
        self.win = MyWindow(file_=FILENAME)
        # self.win.show_all()
        # Gtk.main()
        data = password_to_file()
        self.passw = data['password']
        self.siteusps = data['siteusps']
        self.hashed = data['hashed']

    def tearDown(self):
        # print(f"running {function_name()} {COUNTER}")
        if readfileraw(filename=FILENAME):
            remove(FILENAME)
        del self.win
        del self.passw
        del self.siteusps
        del self.hashed

    def log_in(self):
        # print(f"running {function_name()} {COUNTER}")
        self.win._entry.set_text(self.passw)
        self.win._button.clicked()
        self.assertTrue(refresh_gui())

    def test_progressbar(self):
        print(f"running {function_name()} {COUNTER}")

        self.assertEqual(self.win._progressbar.get_fraction(), 0.0)
        self.win._progressbar.set_fraction(0.5)
        self.assertEqual(self.win._progressbar.get_fraction(), 0.5)
        self.assertTrue(self.win._on_timeout())
        self.assertEqual(self.win._progressbar.get_fraction(), 0.501)
        self.win._progressbar.set_fraction(0.999)
        # self.assertRaises(ValueError, self.win._on_timeout)
        print("expecting following error:")
        print("Gtk-CRITICAL ** gtk_main_quit: assertion 'main_loops != NULL' failed")
        # self.assertRaises(Gtk-CRITICAL, self.win._on_timeout)
        self.assertRaises(SystemExit, self.win._on_timeout)
        # self.assertEqual(self.win._progressbar.get_fraction(), 1)

    def test_main_page(self):
        print(f"running {function_name()} {COUNTER}")
        # self.win = MyWindow(file_=FILENAME)
        self.assertEqual(self.win.file_, FILENAME)
        self.assertEqual(self.win._entry.get_text(), "password")
        self.assertTrue(self.win._hide_pass.get_active())
        self.assertFalse(self.win._entry.get_visibility())
        self.assertFalse(self.win._data_refresh())
        # data = password_to_file()
        self.assertTrue(readfileraw(filename=FILENAME))
        # print(f'{data=}')

        self.win._entry.set_text(self.passw)
        self.assertEqual(self.win._entry.get_text(), self.passw)
        self.assertEqual(self.win._hashed, '')
        # self.win._button_clicked(self.win._entry, "password")
        self.assertEqual(self.win._notebook.get_n_pages(), 2)
        # self.assertEqual(self.win._notebook.get_current_page(), -1)

        self.win._button.clicked()
        self.assertTrue(refresh_gui())
        self.assertEqual(self.win._hashed, self.hashed)
        self.assertEqual(self.win._data, self.siteusps)
        # self.assertEqual(self.win._notebook.get_current_page(), -1)

    def test__add_pass_page(self):
        print(f"running {function_name()} {COUNTER}")

        # self.win = MyWindow(file_=FILENAME)
        # data = password_to_file()
        self.log_in()
        self.assertEqual(self.win._passpage.get_n_pages(), 6)

        self.assertEqual(self.win._data, self.siteusps)
        self.assertEqual(self.win._entry_username.get_text(),
                         self.win._entry_page.get_text())
        self.assertEqual(self.win._entry_password.get_text(),
                         self.win._entry_page.get_text())
        self.assertEqual(self.win._entry_password.get_text(), '')
        self.win._entry_page.set_text('123')
        self.win._entry_password.set_text('456')
        # self.win._last_entry_username = ""
        save_button = self.win._add_password_page.get_child_at(0, 0)
        save_button.clicked()
        self.assertTrue(refresh_gui())
        self.assertEqual(self.win._data, self.siteusps)
        self.win._entry_username.set_text('789')
        save_button.clicked()
        self.assertTrue(refresh_gui())
        self.assertFalse(self.win._data == self.siteusps)
        self.siteusps.append('123\t\t789\t\t456')
        self.assertEqual(self.win._data, self.siteusps)
        # self.assertEqual(self.win._passpage.get_current_page(), -1)

    def test__read_page_pass_page(self):
        print(f"running {function_name()} {COUNTER}")
        # somehow test_read... fails Gtk and unittest won't finish..
        # I have no clue why
        self.log_in()

        children = self.win._read_password_page.get_children()
        refresh_button = children[0]
        # print(children)
        shows = [self.win._data_iterators,
                 self.win._usershows,
                 self.win._passshows]
        self.assertEqual(shows[0][0].get_active_iter(), None)
        self.assertEqual(self.win._counter_label.get_text(), f"{len(self.win._data)} passwords")
        # print(self.siteusps)
        for ii, siteup in enumerate(self.siteusps):
            shows[0][0].set_active(ii)
            # active_iter = shows[0][0].get_active_iter()
            siteusp = siteup.split('\t\t')

            for i, show in enumerate(shows):
                for sh in show:
                    if isinstance(sh, gi.repository.Gtk.ComboBox):
                        self.assertEqual(sh.get_active(), ii)
                    elif i < 2 or (i == 2 and isinstance(sh, gi.repository.Gtk.Entry)):
                        self.assertEqual(sh.get_text(), siteusp[i])
                    else:
                        self.assertEqual(sh.get_text(), f"{siteusp[i][:20]}{'...' if len(siteusp[i]) > 20 else ''}")
            self.assertEqual(len(self.win._data), len(self.siteusps))

            self.assertEqual(self.win._counter_label.get_text(), f"{len(self.win._data)} passwords")

    def test_del_pass_page(self):
        print(f"running {function_name()} {COUNTER}")
        self.log_in()
        # print("test_del_pass_page;;;"*10)
        # print(f"{self.win._data=}")
        children = self.win._delete_password_page.get_children()
        refresh_button = children[0]
        hbox = children[1].get_children()
        selector_combobox = hbox[0]
        delete_button = hbox[1]
        user_label = children[2]
        pass_label = children[3]
        self.assertEqual(selector_combobox.get_active(), -1)
        while self.win._data:
            iter_ = random.randint(0, len(self.win._data)-1)
            selector_combobox.set_active(iter_)
            siteusp = self.siteusps[iter_].split('\t\t')
            self.assertEqual(user_label.get_text(), siteusp[1])
            self.assertEqual(pass_label.get_text(), f"{siteusp[2][:20]}{'...' if len(siteusp[2]) > 20 else ''}")
            delete_button.clicked()
            self.siteusps.pop(iter_)
            self.assertTrue(refresh_gui())
            self.assertEqual(selector_combobox.get_active(), -1)
            self.assertEqual(user_label.get_text(), '')
            self.assertEqual(pass_label.get_text(), '')

    def test_change_password_page(self):
        print(f"running {function_name()} {COUNTER}")
        self.log_in()
        children = self.win._modify_password_page.get_children()
        refresh_button = children[0]
        selector_combobox = children[1]
        hbox = children[2].get_children()
        reset_button = hbox[0]
        site_entry = hbox[1]
        site_button = hbox[2]
        hbox = children[3].get_children()
        save_button = hbox[0]
        user_entry = hbox[1]
        user_button = hbox[2]
        hbox = children[4].get_children()
        generate_button = hbox[0]
        password_entry = hbox[1]
        password_button = hbox[2]
        sup_entry = [site_entry, user_entry, password_entry]
        sup_button = [site_button, user_button, password_button]

        self.assertEqual(selector_combobox.get_active(), -1)

        self.assertTrue('return' in reset_button.get_label())
        self.assertTrue('save' in save_button.get_label())
        self.assertTrue('generate' in generate_button.get_label())

        avail_passes = []
        for i in range(100):
            iter_ = random.randint(0, len(self.win._data)-1)
            selector_combobox.set_active(iter_)
            siteusp = self.siteusps[iter_].split('\t\t')
            self.assertEqual(site_entry.get_text(), siteusp[0])
            self.assertEqual(user_entry.get_text(), siteusp[1])
            self.assertEqual(password_entry.get_text(), siteusp[2])

            self.assertFalse(site_entry.get_editable())
            self.assertFalse(user_entry.get_editable())
            self.assertFalse(password_entry.get_editable())

            # changing part

            sup = random.randint(0, 2)
            if not avail_passes:
                avail_passes.extend(newrandompass())

            new_string = avail_passes.pop()

            sup_button[sup].clicked()
            refresh_gui()
            for i, entry in enumerate(sup_entry):
                self.assertEqual(entry.get_editable(), i == sup)

            sup_entry[sup].set_text(new_string)
            refresh_gui()

            self.assertEqual(sup_entry[sup].get_text(), new_string)
            self.assertFalse(sup_entry[sup].get_text() == siteusp[sup])

            reset_button.clicked()
            refresh_gui()
            self.assertEqual(sup_entry[sup].get_text(), siteusp[sup])
            self.assertFalse(sup_entry[sup].get_text() == new_string)

            sup_entry[sup].set_text(new_string)
            refresh_gui()

            save_button.clicked()
            refresh_gui()

            for entry in sup_entry:
                self.assertEqual(entry.get_text(), '')

            self.assertFalse(self.win._data == self.siteusps)
            siteusp[sup] = new_string
            self.siteusps[iter_] = '\t\t'.join(siteusp)
            # print(f'{self.win._data[iter_]=}')
            # print(f'{self.siteusps[iter_]=}')
            self.assertTrue(self.win._data == self.siteusps)

        # TBD: add here test for generate_button

    def test_generate_pass_page(self):
        print(f"running {function_name()} {COUNTER}")
        self.log_in()
        self.assertTrue(self.win._generate_for is None)
        self.assertTrue(self.win._list_of_passwords == [])

        generate_button = self.win._generate_password_page.get_child_at(0, 0)
        chosen_password_label = self.win._chosen_password
        selected_password_spinbutton = self.win._selected_password
        use_pass = self.win._use_pass
        lowercase = self.win._use_lowercase
        uppercase = self.win._use_uppercase
        digits = self.win._use_digits
        specials = self.win._use_specials
        extra = self.win._use_extra
        enforce_secure = self.win._enforce_secure
        minlen_spinbutton = self.win._minlen
        maxlen_spinbutton = self.win._maxlen
        list_of_passwords = self.win._list_of_passwords

        togglers = [lowercase, uppercase, specials, extra, digits]
        len_tog = len(togglers)
        for b in range(2**len_tog):
            on = [bool(int(i)) for i in f'{bin(b)[2:]:>{len_tog}}'.replace(' ', '0')]
            # set togglers on/off
            for t, tog in enumerate(togglers):
                tog.set_active(on[t])
                self.assertEqual(tog.get_active(), on[t])

            self.assertTrue(refresh_gui())
            min_ = 3 if (sumon := sum(on)) < 3 else sumon
            self.assertTrue(minlen_spinbutton.get_value_as_int() >= min_)
            self.assertEqual(len(self.win._list_of_passwords), 0)
            self.assertEqual(chosen_password_label.get_text(), '')
            self.assertTrue(self.win._generate(generate_button) == bool(sumon))
            self.assertTrue(refresh_gui())

            if not sumon:
                self.assertEqual(len(self.win._list_of_passwords), 0)
                continue

            self.assertEqual(len(self.win._list_of_passwords), 10)
            self.assertFalse(chosen_password_label.get_text() == '')
            pw = self.win._list_of_passwords[0]
            self.assertTrue(chosen_password_label.get_text() == pw)
            for i, pw in enumerate(self.win._list_of_passwords):
                self.win._selected_password.set_value(i)
                self.assertEqual(chosen_password_label.get_text(), pw)
                # TBD: validate if password is what it suppose to be
                min_ = minlen_spinbutton.get_value_as_int()
                max_ = maxlen_spinbutton.get_value_as_int()
                self.assertTrue(min_ <= len(pw) <= max_)

    def test__settings_page(self):
        print(f"running {function_name()} {COUNTER}")
        self.log_in()

        change_pass_button = self.win._change_pass_page.get_child_at(0, 4)
        #  change main password
        entries = [
                self.win._old_pass,
                self.win._new_pass,
                self.win._new_pass_2]
        # get different password than current
        l_p = [i for i in self.passw]
        random.shuffle(l_p)
        l_p = ''.join(l_p)

        for entry in entries:
            self.assertEqual(entry.get_text(), '')
            entry.set_text(l_p)

        # wrong password
        self.assertTrue(refresh_gui())
        change_pass_button.clicked()
        self.assertTrue(refresh_gui())
        for entry in entries:
            self.assertEqual(entry.get_text(), l_p)
            entry.set_text(self.passw)

        # good password,but same as last
        self.assertTrue(refresh_gui())
        change_pass_button.clicked()
        self.assertTrue(refresh_gui())

        # source of random passwords:
        generate_button = self.win._generate_password_page.get_child_at(0, 0)
        generate_button.clicked()
        self.assertTrue(refresh_gui())

        while self.win._list_of_passwords:
            # ensure old password is entered
            if not entries[0].get_text():
                entries[0].set_text(self.passw)
            new_pass = self.win._list_of_passwords.pop()
            # print(f"{new_pass=}")
            entries[1].set_text(new_pass)
            l_p = [i for i in new_pass]
            random.shuffle(l_p)
            l_p = ''.join(l_p)
            entries[2].set_text(l_p)
            # good password,but next two doesn't match
            self.assertTrue(refresh_gui())
            # print("refresh")
            change_pass_button.clicked()
            self.assertTrue(refresh_gui())
            # print("refresh")

            for entry in entries:
                self.assertFalse(entry.get_text() == '')

            entries[2].set_text(new_pass)
            # now all match
            self.assertTrue(refresh_gui())
            # print("refresh")

            self.passw = new_pass


if __name__ == '__main__':
    unittest.main()
    # define the function blocks
