#!/usr/bin/env python3
"""Gtk gui for password manager."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk

from pwtools import validate_password, uncode, newpass
from pwtools import newrandompass, hash_it, extrachars
from css_tools import read_saved_css

FILENAME = 'safepasswords'  # name of file where data are stored

class MyWindow(Gtk.Window):
    def __init__(self, file_=FILENAME):
        Gtk.Window.__init__(self, title="password manager")
        self.connect("destroy", Gtk.main_quit)
        self.file_ = file_
        self.connect("event-after", self._checkout)  # for timeout
        try:  # no need to crash because of icon
            self.set_icon_from_file('tux4.png')
        except FileNotFoundError:
            print('icon (tux4.png) not found')
        self.set_size_request(200, 100)
        self.set_border_width(3)
        self._hashed = ''
        # variables for passwords

        self._data = [' \t\t \t\t ']
        self._data_store = Gtk.ListStore(str, str, str)
        self._data_store.append(self._data[0].split('\t\t'))
        self._data_iterators = []  # selectors
        self._siteshows = []  # labels showing "site"
        self._usershows = []  # labels showing "users"
        self._passshows = []  # labels showing "password"

        self._provider = Gtk.CssProvider()

        self._set_ui()

    def _checkout(self, *_):
        """Reset progressbar (timeout) to 0 after any event."""
        self._progressbar.set_fraction(0)

    def _set_ui(self):
        self._set_css()
        self._notebook = Gtk.Notebook()
        self._box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self._box.pack_start(self._notebook, True, True, 0)
        self._progressbar = Gtk.ProgressBar()
        self._box.pack_start(self._progressbar, False, False, 0)
        self.add(self._box)

        self._notebook.set_show_tabs(False)
        self._main_page()
        self._notebook.append_page(self._startpage)
        self._pass_page()
        self._notebook.append_page(self._passpage)
        # for ability to copy to clipboard
        self._clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        # exit after 30 seconds of inactivity
        self._timeout_id = GLib.timeout_add(30, self._on_timeout, None)

    def _on_timeout(self, *_):
        """Update value on the progress bar."""
        new_value = self._progressbar.get_fraction() + 0.001
        self._progressbar.set_fraction(new_value)
        if new_value >= 1:
            # kill .. maybe make it optional?.. nah
            Gtk.main_quit()
            raise SystemExit

        return True

    def _set_css(self):
        screen = Gdk.Screen.get_default()

        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, self._provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        self._provider.load_from_data(read_saved_css().encode())

    def _main_page(self):
        self._startpage = Gtk.Grid()
        self._startpage.set_border_width(10)

        self._description1 = Gtk.Label(
                label="<b>insert password</b>", use_markup=True
                )
        self._startpage.attach(self._description1, 0, 0, 2, 1)

        self._entry = Gtk.Entry()
        self._entry.set_visibility(False)
        self._entry.set_text("password")
        self._entry.connect("activate", self._button_clicked, "password")
        self._startpage.attach(self._entry, 0, 1, 2, 1)

        self._button = Gtk.Button(label="Enter")
        self._button.connect("clicked", self._button_clicked, "password")
        self._startpage.attach(self._button, 0, 2, 1, 1)

        self._hide_pass = Gtk.CheckButton(label="hidden")
        self._hide_pass.set_active(True)
        self._hide_pass.connect("toggled", self._hide_text, "main_page")
        self._startpage.attach(self._hide_pass, 1, 2, 1, 1)

        self._wrong_pass = 0  # counter for invalid passwords

    def _startpage_default(self):
        """Set first page to default values."""
        self._description1.set_text("insert password")
        self._entry.set_text("")
        self._hide_pass.set_active(True)
        self._entry.set_visibility(False)
        self._wrong_pass = 0

    def _pass_page(self):
        """Set up pages with all usual operations."""
        self._passpage = Gtk.Notebook()
        # page labels on left side:
        self._passpage.set_tab_pos(Gtk.PositionType.LEFT)
        # add password , modify password , read passwords..
        self._manage_add_pass_page()
        self._passpage.append_page(
            self._add_password_page, Gtk.Label(label="add")
            )

        # read passwords
        self._manage_read_pass_page()
        self._passpage.append_page(
            self._read_password_page, Gtk.Label(label="read")
            )

        # modify password
        self._manage_modify_page()
        self._passpage.append_page(
            self._modify_password_page,
            Gtk.Label(label="edit")
            )

        # delete password
        self._manage_del_pass_page()
        self._passpage.append_page(
            self._delete_password_page,
            Gtk.Label(label="delete")
            )

        # generate_password_window
        self._generate_for = None  # which page is password generated for
        self._manage_generate()
        self._passpage.append_page(
            self._generate_password_page, Gtk.Label(label="generate")
            )

        self._manage_settings()
        self._passpage.append_page(
            self._settings_page, Gtk.Label(label="settings")
            )

    def _manage_settings(self):
        """Set notebook of pages."""
        self._settings_page = Gtk.Notebook()

        self._manage_change_password()
        self._settings_page.append_page(
            self._change_pass_page,
            Gtk.Label(label="change password")
            )

    def _manage_change_password(self):
        """
        Page for changing main password.

        classically should have entered 1x old password
        and 2x new password
        then recode file with new passowrd
        """
        self._change_pass_page = Gtk.Grid()
        label = Gtk.Label(
            label="<b>change master password : </b>",
            use_markup=True
            )
        label.set_justify(Gtk.Justification.FILL)
        self._change_pass_page.attach(label, 0, 0, 4, 1)

        # NEXT ROW
        label = Gtk.Label(label="old password: ")
        self._change_pass_page.attach(label, 0, 1, 1, 1)
        self._old_pass = Gtk.Entry()
        self._old_pass.set_visibility(False)
        self._old_pass.connect("changed", self._set_icons)
        self._change_pass_page.attach(self._old_pass, 1, 1, 1, 1)
        hide = Gtk.CheckButton(label='hide')
        hide.set_active(True)
        hide.set_can_focus(False)
        hide.connect('toggled', self._hide_text, self._old_pass)
        self._change_pass_page.attach(hide, 2, 1, 1, 1)
        checkbutton = Gtk.ToolButton()
        checkbutton.set_icon_name("edit-insert")
        checkbutton.set_expand(True)
        checkbutton.set_can_focus(False)
        self._icons = [checkbutton]
        self._change_pass_page.attach(checkbutton, 3, 1, 1, 1)

        # NEXT ROW
        label = Gtk.Label(label="new password: ")
        self._change_pass_page.attach(label, 0, 2, 1, 1)
        self._new_pass = Gtk.Entry()
        self._new_pass.set_visibility(False)
        self._change_pass_page.attach(self._new_pass, 1, 2, 1, 1)
        hide = Gtk.CheckButton(label='hide')
        hide.set_active(True)
        hide.set_can_focus(False)
        hide.connect('toggled', self._hide_text, self._new_pass)
        self._change_pass_page.attach(hide, 2, 2, 1, 1)
        checkbutton = Gtk.ToolButton()
        checkbutton.set_icon_name("edit-insert")
        checkbutton.set_expand(True)
        checkbutton.set_can_focus(False)
        self._icons.append(checkbutton)
        self._change_pass_page.attach(checkbutton, 3, 2, 1, 1)

        # NEXT ROW
        label = Gtk.Label(label="new password: ")
        self._change_pass_page.attach(label, 0, 3, 1, 1)
        self._new_pass_2 = Gtk.Entry()
        self._new_pass_2.set_visibility(False)
        self._new_pass.connect("changed", self._set_icons)
        self._new_pass_2.connect("changed", self._set_icons)
        self._change_pass_page.attach(self._new_pass_2, 1, 3, 1, 1)
        hide = Gtk.CheckButton(label='hide')
        hide.set_active(True)
        hide.connect('toggled', self._hide_text, self._new_pass_2)
        hide.set_can_focus(False)
        self._change_pass_page.attach(hide, 2, 3, 1, 1)
        checkbutton = Gtk.ToolButton()
        checkbutton.set_icon_name("edit-insert")
        checkbutton.set_expand(True)
        checkbutton.set_can_focus(False)
        self._icons.append(checkbutton)
        self._change_pass_page.attach(checkbutton, 3, 3, 1, 1)

        # NEXT ROW
        change = Gtk.Button(label='change')
        change.connect('clicked', self._change_master_password)
        self._change_pass_page.attach(change, 0, 4, 4, 1)
        self._set_icons()

    def _set_icons(self, *_):
        ok_icon = "emblem-checked"  # "dialog-ok"
        ng_icon = "emblem-unavailable"  # "emblem-error" ""
        # warning = "gtk-dialog-warning" # "emblem-warning" "dialog-error"
        empty = "emblem-question"
        entries = [self._old_pass, self._new_pass, self._new_pass_2]
        oldtext = self._old_pass.get_text()
        for entry, icon in zip(entries, self._icons):
            # print(entry is self._old_pass)
            icon.set_icon_name(empty)
            if entry.get_text():
                if entry is self._old_pass:
                    result = validate_password(entry.get_text(), filename=self.file_)
                    icon.set_icon_name(ok_icon if result else ng_icon)
                else:
                    text1 = self._new_pass.get_text()
                    text2 = self._new_pass_2.get_text()
                    if text1 and text2:
                        if text1 == text2 != oldtext:
                            icon.set_icon_name(ok_icon)
                        else:
                            icon.set_icon_name(ng_icon)

    def _save_all_passwords(self):
        """Save all data in memory to file."""
        add = False  # overwrite existing
        for record in self._data:
            newpass(self._hashed, record, add, filename=self.file_)
            if not add:
                add = True  # append

    def _change_master_password(self, *_):
        """Everyting needed for change master password."""
        self._set_icons()
        old = self._old_pass.get_text()
        new = self._new_pass.get_text()
        new2 = self._new_pass_2.get_text()
        if validate_password(old, filename=self.file_):  # correct old password
            if new and new2:       # new password is not empty
                # both are the same and not old password
                if new == new2 != old:
                    # now is the time to change main password
                    # update self._hashed
                    self._hashed = hash_it(new[::-1])
                    # save all passwords with new hash
                    self._save_all_passwords()
                    # read them from file
                    self._data_refresh()
                    # clearup entries
                    self._old_pass.set_text('')
                    self._new_pass.set_text('')
                    self._new_pass_2.set_text('')

    def _use_generated_password(self, *_):
        if self._list_of_passwords:
            value = self._selected_password.get_value_as_int()
            passtouse = self._list_of_passwords[value]
            if self._generate_for is None:
                # copy to memory
                self._clipboard.set_text(passtouse, -1)
            elif self._generate_for == 0:  # add password page
                self._entry_password.set_text(passtouse)
            elif self._generate_for == 2:  # edit password page
                # no point if nothing is selected
                if self._site_select_for_edit.get_active_iter() is not None:
                    self._edit_password.set_text(passtouse)
            if self._generate_for is not None:
                self._passpage.set_current_page(self._generate_for)
                self._generate_for = None
        copy_or_use = "copy" if self._generate_for is None else "use"
        use_pass_label = f"{copy_or_use} pass"
        self._use_pass.set_label(use_pass_label)

    def _manage_generate(self):
        self._generate_password_page = Gtk.Grid()
        self._list_of_passwords = []

        button = Gtk.Button(label='generate')
        button.connect("clicked", self._generate)

        self._generate_password_page.attach(button, 0, 0, 3, 1)

        self._chosen_password = Gtk.Label(label='')
        self._chosen_password.set_line_wrap(True)
        self._chosen_password.set_max_width_chars(20)
        # self._chosen_password.set_editable(False)
        # self._chosen_password.set_wrap_mode()
        self._generate_password_page.attach(self._chosen_password, 0, 1, 2, 2)

        self._selected_password = Gtk.SpinButton()
        self._selected_password.set_numeric(True)
        self._selected_password.set_update_policy(
            Gtk.SpinButtonUpdatePolicy.IF_VALID
            )
        self._selected_password.set_adjustment(
            Gtk.Adjustment(lower=0, upper=0, step_increment=1)
            )
        self._selected_password.connect("changed", self._show_pass)
        self._generate_password_page.attach(
                self._selected_password, 2, 1, 1, 1
            )

        self._use_pass = Gtk.Button(
            label=f"{'copy' if self._generate_for is None else 'use'} pass"
            )
        self._use_pass.connect('clicked', self._use_generated_password)
        self._generate_password_page.attach(self._use_pass, 2, 2, 1, 1)

        self._use_lowercase = Gtk.CheckButton(label='use lowercase chars')
        self._use_lowercase.set_active(True)
        self._use_lowercase.connect('toggled', self._security_of_password)
        self._generate_password_page.attach(self._use_lowercase, 0, 3, 1, 1)

        self._use_uppercase = Gtk.CheckButton(label='use uppercase chars')
        self._use_uppercase.set_active(True)
        self._use_uppercase.connect('toggled', self._security_of_password)
        self._generate_password_page.attach(self._use_uppercase, 1, 3, 1, 1)

        self._use_digits = Gtk.CheckButton(label='use digits')
        self._use_digits.set_active(True)
        self._use_digits.connect('toggled', self._security_of_password)
        self._generate_password_page.attach(self._use_digits, 0, 4, 1, 1)

        self._use_specials = Gtk.CheckButton(label='use specials')
        self._use_specials.set_active(True)
        self._use_specials.connect('toggled', self._security_of_password)
        self._generate_password_page.attach(self._use_specials, 1, 4, 1, 1)

        self._use_extra = Gtk.CheckButton(label='use extra chars')
        self._use_extra.set_active(True)
        self._use_extra.connect('toggled', self._security_of_password)
        self._generate_password_page.attach(self._use_extra, 0, 5, 1, 1)

        self._enforce_secure = Gtk.CheckButton(label='enforce secure')
        self._enforce_secure.set_active(True)
        self._enforce_secure.connect('toggled', self._security_of_password)
        self._generate_password_page.attach(self._enforce_secure, 1, 5, 1, 1)

        # min length of password
        self._minlen = Gtk.SpinButton()
        self._minlen.set_numeric(True)  # only numbers
        self._minlen.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        self._minlen.set_adjustment(
            Gtk.Adjustment(
                lower=5, upper=50, step_increment=1, page_increment=10
                )
            )
        self._minlen.set_value(10)
        self._minlen.connect('changed', self._on_min_change)
        label_minlen = Gtk.Label(label='minimal length')
        self._generate_password_page.attach(self._minlen, 0, 6, 1, 1)
        self._generate_password_page.attach(label_minlen, 1, 6, 1, 1)
        # max length of password
        self._maxlen = Gtk.SpinButton()
        self._maxlen.set_numeric(True)
        self._maxlen.set_adjustment(
            Gtk.Adjustment(
                lower=5, upper=50, step_increment=1, page_increment=10
                )
            )
        self._maxlen.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        self._maxlen.set_value(20)
        self._maxlen.connect('changed', self._on_max_change)
        label_maxlen = Gtk.Label(label='max length')
        self._generate_password_page.attach(self._maxlen, 0, 7, 1, 1)
        self._generate_password_page.attach(label_maxlen, 1, 7, 1, 1)

    def _clearup_pass(self):
        self._list_of_passwords = []
        self._chosen_password.set_text("")
        self._selected_password.set_value(0)
        self._selected_password.set_range(0, 0)

    def _on_min_change(self, widget):
        value = widget.get_value_as_int()
        self._maxlen.set_range(value, value+50)
        self._clearup_pass()

    def _on_max_change(self, widget):
        value = widget.get_value_as_int()
        if self._minlen.get_value_as_int() > value:
            self._minlen.set_value(value)
        self._clearup_pass()

    def _security_of_password(self, widget):
        """Compute and set limit on password length."""
        # if this is called, then it should be resetted
        self._clearup_pass()
        # security of password with 8 length
        # with uppercase, lowercase, digit and special
        # is 94**8 = optimal 6095689385410816
        optimal = 6095689385410816 * 10
        lower = self._use_lowercase.get_active()
        upper = self._use_uppercase.get_active()
        digits = self._use_digits.get_active()
        specials = self._use_specials.get_active()
        extra = self._use_extra.get_active()
        # minimum must be amount of selected lists
        # (due to checking logic of password ...)
        minpasslen = lower + upper + digits + specials + extra
        if not self._enforce_secure.get_active():
            if minpasslen < 3:
                minpasslen = 3
            self._minlen.set_range(minpasslen, 50)
            self._maxlen.set_range(minpasslen, 50)
            return
        # security of password is enabled
        # base depends on lists selected
        base = 0
        base += 26 if lower else 0
        base += 26 if upper else 0
        base += 32 if specials else 0
        base += 10 if digits else 0
        base += 20 if extra else 0

        if base:  # if none selected, this would go FOREVER..
            while base**minpasslen < optimal:
                minpasslen += 1
            self._minlen.set_range(minpasslen, minpasslen+50)
            self._maxlen.set_range(minpasslen, minpasslen+50)

    def _generate(self, widget):
        """
        Collects info about settings,
        sends it to password generator
        and stores result to self._list_of_passwords.
        """
        lower = self._use_lowercase.get_active()
        upper = self._use_uppercase.get_active()
        digits = self._use_digits.get_active()
        specials = self._use_specials.get_active()
        extra = self._use_extra.get_active()
        minlen = self._minlen.get_value_as_int()
        maxlen = self._maxlen.get_value_as_int()

        if lower+upper+digits+specials+extra:
            # at least one has to be true
            self._list_of_passwords = newrandompass(
                                        lower, upper, digits,
                                        specials, extra, minlen, maxlen
                                        )
            # print(self._list_of_passwords)
            self._chosen_password.set_text(self._list_of_passwords[0])
            self._selected_password.set_value(0)
            self._selected_password.set_range(
                0, len(self._list_of_passwords)-1
            )

    def _show_pass(self, *_):
        text = ''
        # if there is list to choose from
        if maxv := len(self._list_of_passwords):
            # pass index is in lists
            if maxv > (val := self._selected_password.get_value_as_int()) >= 0:
                # assign value
                text = self._list_of_passwords[val]
        self._chosen_password.set_text(text)
        return

    def _manage_del_pass_page(self):
        self._delete_password_page = Gtk.Box(
                            orientation=Gtk.Orientation.VERTICAL, spacing=6
                            )
        button = Gtk.Button(label='refresh')
        button.connect("clicked", self._data_refresh)
        self._delete_password_page.pack_start(button, False, True, 1)

        self._site_select_for_del = Gtk.ComboBox.new_with_model(
                                        self._data_store
                                    )
        self._data_iterators.append(self._site_select_for_del)
        self._site_select_for_del.connect('changed', self._display)
        renderer = Gtk.CellRendererText()
        self._site_select_for_del.pack_start(renderer, True)
        self._site_select_for_del.add_attribute(renderer, "text", 0)
        self._site_select_for_del.set_entry_text_column(0)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        button = Gtk.Button(label='delete')
        button.connect('clicked', self._manage_entry, 'delete_entry')
        hbox.pack_start(self._site_select_for_del, True, True, 1)
        hbox.pack_start(button, False, False, 0)

        self._delete_password_page.pack_start(hbox, False, False, 0)
        self._record_for_del = ''

        self._user_for_del = Gtk.Label(label='self._user_for_del')
        self._usershows.append(self._user_for_del)
        self._delete_password_page.pack_start(
            self._user_for_del, False, False, 0
        )
        self._pass_for_del = Gtk.Label(label='self._pass_for_del')
        self._passshows.append(self._pass_for_del)
        self._delete_password_page.pack_start(
            self._pass_for_del, False, False, 0
        )

    def _manage_entry(self, _, strinfo):
        if strinfo == 'delete_entry':
            if todelete := self._record_for_del:
                if todelete in self._data:
                    self._data.pop(self._data.index(todelete))
                    if not self._data:
                        # no passwords left
                        newpass(self._hashed, delete=True, filename=self.file_)
                    self._save_all_passwords()

                self._data_refresh()

    def _manage_modify_page(self):
        self._modify_password_page = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        button = Gtk.Button(label='refresh')
        button.connect("clicked", self._data_refresh)
        self._modify_password_page.pack_start(button, False, True, 1)

        self._site_select_for_edit = Gtk.ComboBox.new_with_model(
            self._data_store
        )
        self._data_iterators.append(self._site_select_for_edit)
        self._site_select_for_edit.connect('changed', self._display)
        renderer = Gtk.CellRendererText()
        self._site_select_for_edit.pack_start(renderer, True)
        self._site_select_for_edit.add_attribute(renderer, 'text', 0)
        self._site_select_for_edit.set_entry_text_column(0)

        self._modify_password_page.pack_start(
            self._site_select_for_edit, True, True, 0
            )
        returnbutton = Gtk.Button(label=f"{'return':^13}")
        returnbutton.connect('clicked', self._save_modified, 'refresh')
        self._edit_site = Gtk.Entry()
        self._edit_site.set_editable(False)
        self._edit_site.set_can_focus(False)
        self._edit_site.set_alignment(0.5)  # center
        self._edit_site.set_name("noentry")
        self._siteshows.append(self._edit_site)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        hbox.pack_start(returnbutton, False, False, 0)
        button = Gtk.Button(label=f"{'edit':^10}")
        button.connect('clicked', self._edit_entry, self._edit_site)

        hbox.pack_start(self._edit_site, True, True, 0)
        hbox.pack_start(button, False, False, 0)
        self._modify_password_page.pack_start(hbox, True, True, 0)

        savebutton = Gtk.Button(label=f"{'save':^14}")
        savebutton.connect('clicked', self._save_modified, 'save')
        self._edit_username = Gtk.Entry()
        self._edit_username.set_editable(False)
        self._edit_username.set_can_focus(False)
        self._edit_username.set_alignment(0.5)  # center
        self._edit_username.set_name("noentry")
        self._usershows.append(self._edit_username)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        hbox.pack_start(savebutton, False, False, 0)
        button = Gtk.Button(label=f"{'edit':^10}")
        button.connect('clicked', self._edit_entry, self._edit_username)

        hbox.pack_start(self._edit_username, True, True, 0)
        hbox.pack_start(button, False, False, 0)
        self._modify_password_page.pack_start(hbox, True, True, 0)

        self._edit_password = Gtk.Entry()
        self._edit_password.set_editable(False)
        self._edit_password.set_can_focus(False)
        self._edit_password.set_alignment(0.5)  # center
        self._edit_password.set_name("noentry")
        self._passshows.append(self._edit_password)
        button = Gtk.Button(label=f"{'generate':^10}")
        button.connect("clicked", self._button_generate)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        hbox.pack_start(button, False, False, 0)
        button = Gtk.Button(label=f"{'edit':^10}")
        button.connect('clicked', self._edit_entry, self._edit_password)
        hbox.pack_start(self._edit_password, True, True, 0)
        hbox.pack_start(button, False, False, 0)
        self._modify_password_page.pack_start(hbox, True, True, 0)

    def _save_modified(self, widget, action):
        """Modify entry in passwords."""
        selected = self._site_selection.get_active_iter()
        if selected is not None:
            model = self._site_selection.get_model()
            oldsite = model[selected][0]
            olduser = model[selected][1]
            oldpassword = model[selected][2]
            old = [oldsite, olduser, oldpassword]
            newsite = self._edit_site.get_text()
            newuser = self._edit_username.get_text()
            newpassword = self._edit_password.get_text()
            new = [newsite, newuser, newpassword]
            if old != new:  # something has changed
                if action == 'save':
                    # replace it
                    oldindex = self._data.index('\t\t'.join(old))
                    self._data.pop(oldindex)
                    self._data.insert(oldindex, '\t\t'.join(new))
                    # write it to file
                    self._save_all_passwords()
                    self._data_refresh()

                elif action == 'refresh':
                    self._edit_site.set_text(oldsite)
                    self._edit_username.set_text(olduser)
                    self._edit_password.set_text(oldpassword)

    def _set_not_editable(self):
        try:
            editers = [
                self._edit_site,
                self._edit_username,
                self._edit_password
                ]
            for editor in editers:
                editor.set_editable(False)
                editor.set_can_focus(False)
                editor.set_name("noentry")
        except AttributeError:
            return
        return

    def _edit_entry(self, _, entry):
        """Manage editability of entries on edit page."""
        if self._site_select_for_edit.get_active_iter() is None:
            # if nothing selected, there is nothing to edit
            return
        status = not entry.get_editable()
        editers = [self._edit_site,
                   self._edit_username,
                   self._edit_password]
        if not status:  # if turn off, just turn off
            entry.set_editable(False)
            entry.set_can_focus(False)
            entry.set_name("noentry")
        if status:  # if turn on, turn off others
            for editer in editers:
                eisentry = editer is entry
                editer.set_editable(eisentry)
                editer.set_can_focus(eisentry)
                editer.set_name("noentry")
                # e.set_has_frame(e is entry) # won't work
                if eisentry:
                    editer.grab_focus()
                    editer.set_name("nowentry")

    def _manage_read_pass_page(self):
        self._read_password_page = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6
        )
        button = Gtk.Button(label='refresh')
        button.connect("clicked", self._data_refresh)
        self._read_password_page.pack_start(button, False, False, 0)

        self._site_selection = Gtk.ComboBox.new_with_model(self._data_store)
        self._site_selection.connect("changed", self._display)
        self._data_iterators.append(self._site_selection)
        renderer_text = Gtk.CellRendererText()
        self._site_selection.pack_start(renderer_text, True)
        self._site_selection.add_attribute(renderer_text, "text", 0)
        self._site_selection.set_entry_text_column(0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        button = Gtk.Button(label='copy')
        button.connect("clicked", self._copycontext, "site")
        hbox.pack_start(self._site_selection, True, True, 0)
        hbox.pack_start(button, False, False, 0)
        self._read_password_page.pack_start(hbox, False, False, 0)

        self._username_label = Gtk.Label()
        self._username_label.set_text('')
        self._usershows.append(self._username_label)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        button = Gtk.Button(label='copy')
        button.connect("clicked", self._copycontext, "username")
        hbox.pack_start(self._username_label, True, True, 0)
        hbox.pack_start(button, False, False, 0)
        self._read_password_page.pack_start(hbox, True, True, 0)

        self._password_label = Gtk.Label()
        self._password_label.set_text('')
        self._passshows.append(self._password_label)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        button = Gtk.Button(label='copy')
        button.connect("clicked", self._copycontext, 'password')

        hbox.pack_start(self._password_label, True, True, 0)
        hbox.pack_start(button, False, False, 0)
        self._read_password_page.pack_start(hbox, True, True, 0)

        self._counter_label = Gtk.Label()
        # self._counter_label.set_text('')
        self._read_password_page.pack_start(self._counter_label, True, True, 0)
        self._display('')

    def _copycontext(self, widget, string):
        index = ['site', 'username', 'password'].index(string)
        selected = self._site_selection.get_active_iter()
        if selected:
            self._clipboard.set_text(self._data_store[selected][index], -1)

    def _manage_add_pass_page(self):
        # add passwods
        self._add_password_page = Gtk.Grid()
        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self._button_clicked, "create_pw")
        self._add_password_page.attach(save_button, 0, 0, 3, 1)

        label_entry_page = Gtk.Label(label="<b>page</b>", use_markup=True)
        self._entry_page = Gtk.Entry()
        self._entry_page.connect("activate", self._button_clicked, "create_pw")
        self._add_password_page.attach(label_entry_page, 0, 1, 1, 1)
        self._add_password_page.attach(self._entry_page, 1, 1, 2, 1)
        label_username = Gtk.Label(label="<b>username</b>", use_markup=True)
        self._entry_username = Gtk.Entry()
        self._last_entry_username = ''
        self._entry_username.connect(
            "activate", self._button_clicked, "create_pw"
            )
        self._no_username = Gtk.CheckButton(label="none")
        self._no_username.connect("toggled", self._hide_text, "entry_username")

        self._add_password_page.attach(label_username, 0, 2, 1, 1)
        self._add_password_page.attach(self._entry_username, 1, 2, 1, 1)
        self._add_password_page.attach(self._no_username, 2, 2, 1, 1)
        label_password = Gtk.Label(label="<b>password</b>", use_markup=True)
        self._entry_password = Gtk.Entry()
        self._entry_password.connect(
            "activate", self._button_clicked, "create_pw"
            )
        self._entry_password.set_visibility(False)
        self._hide_entry_p = Gtk.CheckButton(label="hide")
        self._hide_entry_p.set_active(True)
        self._hide_entry_p.connect("toggled", self._hide_text, "pw_page")

        self._add_password_page.attach(label_password, 0, 3, 1, 1)
        self._add_password_page.attach(self._entry_password, 1, 3, 1, 1)
        self._add_password_page.attach(self._hide_entry_p, 2, 3, 1, 1)

        button_password = Gtk.Button(label="generate password")
        button_password.connect("clicked", self._button_generate)
        self._add_password_page.attach(button_password, 0, 4, 3, 1)

    def _hide_text(self, widget, string_info):
        """For managing showing/hiding input."""
        value = widget.get_active()
        if not isinstance(string_info, str):
            # it is entry
            string_info.set_visibility(not value)
        if string_info == "pw_page":
            self._entry_password.set_visibility(not value)
            self._entry_password.grab_focus_without_selecting()
        if string_info == "main_page":
            self._entry.set_visibility(not value)
            # ready to another entry of password
            self._entry.grab_focus_without_selecting()
        if string_info == "entry_username":
            self._entry_username.set_editable(not value)
            if value:
                self._last_entry_username = self._entry_username.get_text()
                self._entry_username.set_text("")
            else:
                self._entry_username.set_text(self._last_entry_username)
                self._last_entry_username = ""

    def _data_refresh(self, *args):
        data = uncode(self._hashed, filename=self.file_)
        if data is None:
            return False
        self._data = data
        self._data_store.clear()
        self._set_not_editable()  # edit entries

        for data in self._data:
            site_user_pass = data.split('\t\t')
            self._data_store.append(site_user_pass)
            # prevent using same password twice
            if (used_pass := site_user_pass[-1]) in self._list_of_passwords:
                self._list_of_passwords.remove(used_pass)
                self._selected_password.set_range(
                    0, len(self._list_of_passwords)-1
                    )
        if self._data:
            del site_user_pass
        self._display('')

    def _display(self, widget):
        site, username, password = ('', '', '')
        # print(f"{widget=}")
        if widget:
            iteration = widget.get_active_iter()
            if iteration is not None:
                model = widget.get_model()
                for iterator in self._data_iterators:
                    if iterator.get_active_iter() != iteration:
                        iterator.set_active_iter(iteration)
                site = model[iteration][0]
                username = model[iteration][1]
                password = model[iteration][2]

        self._set_not_editable()
        for siteiter in self._siteshows:
            siteiter.set_text(site)
        for useriter in self._usershows:
            useriter.set_text(username)
        for pwiter in self._passshows:
            if isinstance(pwiter, gi.repository.Gtk.Entry):
                pwiter.set_text(password)
            else:
                pwiter.set_text(
                    f"{password[:20]}{'...' if len(password) > 20 else ''}"
                    )
        self._counter_label.set_text(f"{len(self._data)} passwords")
        if site+username+password:
            self._record_for_del = f"{site}\t\t{username}\t\t{password}"

    def _button_generate(self, widget):
        """
        Switches to "generate password" page
        and remembers where it was sent from.
        """
        # remember where it was sent from
        self._generate_for = self._passpage.get_current_page()
        self._use_pass.set_label(
            f"{'copy' if self._generate_for is None else 'use'} pass"
            )
        # switch page
        self._passpage.set_current_page(4)

    def _button_clicked(self, widget, strinfo):
        if strinfo == "password":
            if not (notempty := self._entry.get_text()):
                return
            # print(f"{notempty=}")
            if result := validate_password(notempty, filename=self.file_):
                self._hashed = result
                self._data_refresh()
                self._notebook.set_current_page(1)
                # self._passpage.set_current_page(self._generate_for)
                self._startpage_default()

            elif result is None:
                # no password in use
                print(f"{result=}")
                self._description1.set_markup(
                    "<b>enter again for confirmation</b>"
                    )
                # ready to another entry of password
                self._entry.grab_focus_without_selecting()
            elif not result:
                # wrong password
                # print(f"{result=}")
                self._wrong_pass += 1
                if self._wrong_pass > 2:
                    # three tries tops
                    Gtk.main_quit()
                self._description1.set_markup(
                    f"<b>wrong password {self._wrong_pass}/3 !</b>"
                )
                # ready to another entry of password
                self._entry.grab_focus_without_selecting()
            # reset password entry
            self._entry.set_text("")

        if strinfo == "create_pw":
            # save new password
            site = self._entry_page.get_text().strip()
            if self._no_username.get_active():
                username = '  '
            else:
                username = self._entry_username.get_text().strip()
            password = self._entry_password.get_text().strip()
            # only proceed if all cells are filled
            if site and username and password:
                newpass(self._hashed, [site, username, password], add=True, filename=self.file_)
                self._entry_username.set_text('')
                self._entry_password.set_text('')
                self._entry_page.set_text('')
                self._data_refresh()


if __name__ == '__main__':
    # """  TBD : color theme change ; maybe through css """
    win = MyWindow()
    win.show_all()
    Gtk.main()
