#!/usr/bin/env python3
"""
Gtk gui for password manager
"""
import gi
gi.require_version("Gtk","3.0")
from gi.repository import Gtk, GLib,Gdk

from pwtools import validate_password,uncode,newpass
from pwtools import newrandompass,hash_it

class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self,title="password manager")
        self.connect("destroy",Gtk.main_quit)
        self.connect("event-after",self.checkout)
        try: # no need to crash because of missing icon
            self.set_icon_from_file('tux4.png')
        except:
            print('icon (tux4.png) not found')
        self.set_size_request(200,100)
        self.set_border_width(3)
        self.hashed = ''
        # variables for passwords

        self.data = [' \t\t \t\t ']
        self.data_store = Gtk.ListStore(str,str,str)
        self.data_store.append(self.data[0].split('\t\t'))
        self.data_iterators = [] # selectors
        self.siteshows = [] # labels showing "site"
        self.usershows = [] # labels showing "users"
        self.passshows = [] # labels showing "password"

        self.set_ui()

    def checkout(self,*widget):
        """
        reseting progressbar (timeout) to 0 when some event happens
        """
        self.progressbar.set_fraction(0)
        return

    def set_ui(self):
        self.set_css()
        self.notebook = Gtk.Notebook()
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
        self.box.pack_start(self.notebook,True,True,0)
        self.progressbar = Gtk.ProgressBar()
        self.box.pack_start(self.progressbar, False, False, 0)
        self.add(self.box)

        self.notebook.set_show_tabs(False)
        self.main_page()
        self.notebook.append_page(self.startpage)
        self.pass_page()
        self.notebook.append_page(self.passpage)
        # for ability to copy to clipboard
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        # exit after 30 seconds of inactivity
        self.timeout_id = GLib.timeout_add(30, self.on_timeout, None)

    def on_timeout(self, user_data):
        """
        Update value on the progress bar
        """
        new_value = self.progressbar.get_fraction() + 0.001
        if new_value >= 1:
            # kill .. maybe make it optional?.. nah
            Gtk.main_quit()
        self.progressbar.set_fraction(new_value)
        return True

    def set_css(self):
        screen = Gdk.Screen.get_default()
        self.provider = Gtk.CssProvider()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
                screen,self.provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        css = """
        * { font-size : 20px;
            background : #000000;
            background-image: linear-gradient(#000000, #222222);
            color : grey;
                    }
        *:disabled {
            background-color: #8A8A8A;
                }
        label:focus {
            background-color: #b4940f;
            }

        entry,label { border-color : #FFFFFF;
                font-size : 22px;
                background : transparent;
                }
        spinner {
            -gtk-icon-source: -gtk-icontheme('process-working-symbolic');
            -gtk-icon-palette: success blue, warning #fc3, error magenta;
            }
        *:active { text-shadow: 2px 2px red;
         }
        button {
            border : 10px #05FAC4;
        }
        combobox {
            border : 5px #05FAC4;
            background-image: linear-gradient(grey, black);
        }
        box {
            background : transparent;
        }
        button:active {
            box-shadow: 0 12px 6px 0 rgba(100,100,100,0.24), 0 17px 20px 0 rgba(100,100,100,0.24);
                    }
        button:hover,whitebutton
        {
            background-image: linear-gradient(grey, black);
            box-shadow: 0 8px 6px 0 rgba(0,0,0,0.24), 0 8px 6px 0 rgba(0,0,0,0.19);
        }

        entry:focus {
            color : white;
            text-shadow: 1px 0px grey;
            background: black;
        }
        #nowentry {
            background-image: linear-gradient(#606060,#060606);
            }


        progressbar > trough > progress {
            background-image: linear-gradient(#606060,#060606);
            background-color: green;
            }

            """

        css = css.encode()
        latticed = ",".join(["#262626","#626262"]*40)
        css += f"#noentry {{ background-image: linear-gradient({latticed});}}".encode()
            # window { background : white;}
        self.provider.load_from_data(css)
        #print(f"{self.provider.list_properties()=}")
    def main_page(self):
        self.startpage = Gtk.Grid()
        self.startpage.set_border_width(10)

        self.description1 = Gtk.Label(label="<b>insert password</b>",use_markup=True)
        self.startpage.attach(self.description1,0,0,2,1)

        self.entry = Gtk.Entry()
        self.entry.set_visibility(False)
        self.entry.set_text("password")
        self.entry.connect("activate",self.button_clicked,"password")
        self.startpage.attach(self.entry,0,1,2,1)

        self.button = Gtk.Button(label="Enter")
        self.button.connect("clicked",self.button_clicked,"password")
        self.startpage.attach(self.button,0,2,1,1)

        self.hide_pass = Gtk.CheckButton(label="hidden")
        self.hide_pass.set_active(True)
        self.hide_pass.connect("toggled",self.hide_text,"main_page")
        self.startpage.attach(self.hide_pass,1,2,1,1)

        self.wrong_pass = 0 # counter for invalid passwords

    def startpage_default(self):
        """
        sets first page to default values
        """
        self.description1.set_text("insert password")
        self.entry.set_text("")
        self.hide_pass.set_active(True)
        self.entry.set_visibility(False)
        self.wrong_pass = 0

    def pass_page(self):
        """
        setting up pages with all usual operations
        """
        self.passpage = Gtk.Notebook()
        # page labels on left side:
        self.passpage.set_tab_pos(Gtk.PositionType.LEFT)
        # add password , modify password , read passwords..
        self.manage_add_pass_page()
        self.passpage.append_page(self.add_password_page,Gtk.Label(label="add"))

        # read passwords
        self.manage_read_pass_page()
        self.passpage.append_page(self.read_password_page,Gtk.Label(label="read"))

        # modify password
        self.manage_modify_page()
        self.passpage.append_page(self.modify_password_page,Gtk.Label(label="edit"))

        # delete password
        self.manage_del_pass_page()
        self.passpage.append_page(self.delete_password_page,Gtk.Label(label="delete"))

        # generate_password_window
        self.generate_for = None # which page is password generated for
        self.manage_generate()
        self.passpage.append_page(self.generate_password_page,Gtk.Label(label="generate"))

        self.manage_settings()
        self.passpage.append_page(self.settings_page,Gtk.Label(label="settings"))

    def manage_settings(self):
        """
        setting notebook of pages
        """
        self.settings_page =  Gtk.Notebook()

        self.manage_change_password()
        self.settings_page.append_page(self.change_pass_page,Gtk.Label(label="change password"))
        return

    def manage_change_password(self):
        """
        page for changing main password
        classically should have entered 1x old password
        and 2x new password
        then recode file with new passowrd
        """
        self.change_pass_page = Gtk.Grid()
        label = Gtk.Label(label="<b>change master password : </b>",use_markup=True)
        label.set_justify(Gtk.Justification.FILL)
        self.change_pass_page.attach(label,0,0,4,1)

        ### NEXT ROW
        label = Gtk.Label(label="old password: ")
        self.change_pass_page.attach(label,0,1,1,1)
        self.old_pass = Gtk.Entry()
        self.old_pass.set_visibility(False)
        self.old_pass.connect("changed",self.set_icons)
        self.change_pass_page.attach(self.old_pass,1,1,1,1)
        hide = Gtk.CheckButton(label='hide')
        hide.set_active(True)
        hide.set_can_focus(False)
        hide.connect('toggled',self.hide_master_pasword,self.old_pass)
        self.change_pass_page.attach(hide,2,1,1,1)
        checkbutton = Gtk.ToolButton()
        checkbutton.set_icon_name("edit-insert")
        checkbutton.set_expand(True)
        #checkbutton.set_is_important(True)
        checkbutton.set_can_focus(False)
        self.icons = [checkbutton]
        self.change_pass_page.attach(checkbutton,3,1,1,1)

        ### NEXT ROW
        label = Gtk.Label(label="new password: ")
        self.change_pass_page.attach(label,0,2,1,1)
        self.new_pass = Gtk.Entry()
        self.new_pass.set_visibility(False)
        self.change_pass_page.attach(self.new_pass,1,2,1,1)
        hide = Gtk.CheckButton(label='hide')
        hide.set_active(True)
        hide.set_can_focus(False)
        hide.connect('toggled',self.hide_master_pasword,self.new_pass)
        self.change_pass_page.attach(hide,2,2,1,1)
        checkbutton = Gtk.ToolButton()
        checkbutton.set_icon_name("edit-insert")
        checkbutton.set_expand(True)
        checkbutton.set_can_focus(False)
        self.icons.append(checkbutton)
        self.change_pass_page.attach(checkbutton,3,2,1,1)

        ### NEXT ROW
        label = Gtk.Label(label="new password: ")
        self.change_pass_page.attach(label,0,3,1,1)
        self.new_pass_2 = Gtk.Entry()
        self.new_pass_2.set_visibility(False)
        self.new_pass.connect("changed",self.set_icons)
        self.new_pass_2.connect("changed",self.set_icons)
        self.change_pass_page.attach(self.new_pass_2,1,3,1,1)
        hide = Gtk.CheckButton(label='hide')
        hide.set_active(True)
        hide.connect('toggled',self.hide_master_pasword,self.new_pass_2)
        hide.set_can_focus(False)
        self.change_pass_page.attach(hide,2,3,1,1)
        checkbutton = Gtk.ToolButton()
        checkbutton.set_icon_name("edit-insert")
        checkbutton.set_expand(True)
        checkbutton.set_can_focus(False)
        self.icons.append(checkbutton)
        self.change_pass_page.attach(checkbutton,3,3,1,1)

        ### NEXT ROW
        change = Gtk.Button(label='change')
        change.connect('clicked',self.change_master_password)
        self.change_pass_page.attach(change,0,4,4,1)
        self.set_icons()
        return

    def set_icons(self,*args):
        ok = "emblem-checked" #  "dialog-ok"
        ng = "emblem-unavailable" # "emblem-error" ""
        warning = "gtk-dialog-warning" # "emblem-warning" "dialog-error"
        empty = "emblem-question"
        entries = [self.old_pass,self.new_pass,self.new_pass_2]
        oldtext = self.old_pass.get_text()
        for entry,icon in zip(entries,self.icons):
            #print(entry is self.old_pass)
            icon.set_icon_name(empty)
            if entry.get_text():
                if entry is self.old_pass:
                    result = validate_password(entry.get_text())
                    icon.set_icon_name(ok if result else ng)
                else:
                    text1 = self.new_pass.get_text()
                    text2 = self.new_pass_2.get_text()
                    if (text1 and text2):
                        if (text1 == text2 != oldtext):
                            icon.set_icon_name(ok)
                        else:
                            icon.set_icon_name(ng)

    def hide_master_pasword(self,widget,entry):
        entry.set_visibility(not widget.get_active())

    def save_all_passwords(self):
        """
        saves all data in memory to file
        """
        add = False # overwrite existing
        for record in self.data:
            newpass(self.hashed,record,add)
            if not add:
                add = True # append
        return

    def change_master_password(self,widget):
        """
        everyting needed for change master password
        """
        self.set_icons()
        old = self.old_pass.get_text()
        new = self.new_pass.get_text()
        new2 = self.new_pass_2.get_text()
        if validate_password(old): # correct old password
            if new and new2:       # new password is not empty
                if new == new2 != old:   # both are the same and not old password
                    # now is the time to change main password
                    # update self.hashed
                    self.hashed = hash_it(new[::-1])
                    # save all passwords with new hash
                    self.save_all_passwords()
                    # read them from file
                    self.data_refresh()
                    # clearup entries
                    self.old_pass.set_text('')
                    self.new_pass.set_text('')
                    self.new_pass_2.set_text('')
        return

    def use_generated_password(self,widget):
        self.use_pass.set_label(f"{'copy' if self.generate_for is None else 'use'} pass")
        if self.list_of_passwords:
            value = self.selected_password.get_value_as_int()
            passtouse = self.list_of_passwords[value]
            if self.generate_for is None:
                # copy to memory
                self.clipboard.set_text(passtouse,-1)
            else: # paste chosen password to desired field
                if self.generate_for == 0: # add password page
                    self.entry_password.set_text(passtouse)
                if self.generate_for == 2: # edit password page
                    # no point if nothing is selected
                    if self.site_select_for_edit.get_active_iter() is not None:
                        self.edit_password.set_text(passtouse)

                self.passpage.set_current_page(self.generate_for)
                self.generate_for = None
        self.use_pass.set_label(f"{'copy' if self.generate_for is None else 'use'} pass")
        return

    def manage_generate(self):
        self.generate_password_page = Gtk.Grid()
        self.list_of_passwords = []

        button = Gtk.Button(label='generate')
        button.connect("clicked",self.generate)

        self.generate_password_page.attach(button,0,0,3,1)

        self.chosen_password = Gtk.Label(label='')
        self.chosen_password.set_line_wrap(True)
        self.chosen_password.set_max_width_chars(20)
        #self.chosen_password.set_editable(False)
        #self.chosen_password.set_wrap_mode()
        self.generate_password_page.attach(self.chosen_password,0,1,2,2)

        self.selected_password = Gtk.SpinButton()
        self.selected_password.set_numeric(True)
        self.selected_password.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        self.selected_password.set_adjustment(Gtk.Adjustment(lower=0,upper=0,step_increment=1))
        self.selected_password.connect("changed",self.show_pass)
        self.generate_password_page.attach(self.selected_password,2,1,1,1)

        self.use_pass = Gtk.Button(label=f"{'copy' if self.generate_for is None else 'use'} pass")
        self.use_pass.connect('clicked',self.use_generated_password)
        self.generate_password_page.attach(self.use_pass,2,2,1,1)

        self.use_lowercase = Gtk.CheckButton(label='use lowercase chars')
        self.use_lowercase.set_active(True)
        self.use_lowercase.connect('toggled',self.security_of_password)
        self.generate_password_page.attach(self.use_lowercase,0,3,1,1)

        self.use_uppercase = Gtk.CheckButton(label='use uppercase chars')
        self.use_uppercase.set_active(True)
        self.use_uppercase.connect('toggled',self.security_of_password)
        self.generate_password_page.attach(self.use_uppercase,1,3,1,1)

        self.use_digits = Gtk.CheckButton(label='use digits')
        self.use_digits.set_active(True)
        self.use_digits.connect('toggled',self.security_of_password)
        self.generate_password_page.attach(self.use_digits,0,4,1,1)

        self.use_specials = Gtk.CheckButton(label='use specials')
        self.use_specials.set_active(True)
        self.use_specials.connect('toggled',self.security_of_password)
        self.generate_password_page.attach(self.use_specials,1,4,1,1)

        self.use_extra = Gtk.CheckButton(label='use extra chars')
        self.use_extra.set_active(True)
        self.use_extra.connect('toggled',self.security_of_password)
        self.generate_password_page.attach(self.use_extra,0,5,1,1)

        self.enforce_secure = Gtk.CheckButton(label='enforce secure')
        self.enforce_secure.set_active(True)
        self.enforce_secure.connect('toggled',self.security_of_password)
        self.generate_password_page.attach(self.enforce_secure,1,5,1,1)

        # min length of password
        self.minlen = Gtk.SpinButton()
        self.minlen.set_numeric(True) # only numbers
        self.minlen.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        self.minlen.set_adjustment(Gtk.Adjustment(lower=5,upper=50,step_increment=1,page_increment=10))
        self.minlen.set_value(10)
        self.minlen.connect('changed',self.on_min_change)
        label_minlen = Gtk.Label(label='minimal length')
        self.generate_password_page.attach(self.minlen,0,6,1,1)
        self.generate_password_page.attach(label_minlen,1,6,1,1)
        # max length of password
        self.maxlen = Gtk.SpinButton()
        self.maxlen.set_numeric(True)
        self.maxlen.set_adjustment(Gtk.Adjustment(lower=5,upper=50,step_increment=1,page_increment=10))
        self.maxlen.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        self.maxlen.set_value(20)
        self.maxlen.connect('changed',self.on_max_change)
        label_maxlen = Gtk.Label(label='max length')
        self.generate_password_page.attach(self.maxlen,0,7,1,1)
        self.generate_password_page.attach(label_maxlen,1,7,1,1)

    def clearup_pass(self):
        self.list_of_passwords = []
        self.chosen_password.set_text("")
        self.selected_password.set_value(0)
        self.selected_password.set_range(0,0)

    def on_min_change(self,widget):
        value = self.minlen.get_value_as_int()
        self.maxlen.set_range(value,value+50)
        self.clearup_pass()

    def on_max_change(self,widget):
        value = self.maxlen.get_value_as_int()
        if self.minlen.get_value_as_int() > value:
            self.minlen.set_value(value)
        self.clearup_pass()

    def security_of_password(self,widget):
        """
        computes and sets limit on password length
        """
        # if this is called,then it should be resetted
        self.clearup_pass()
        # security of password with 8 length
        # with uppercase,lowercase,digit and special
        # is 94**8 = optimal 6095689385410816
        optimal = 6095689385410816 * 100
        lower = self.use_lowercase.get_active()
        upper = self.use_uppercase.get_active()
        digits = self.use_digits.get_active()
        specials = self.use_specials.get_active()
        extra = self.use_extra.get_active()
        # minimum must be amount of selected lists
        # (due to checking logic of password validity...)
        x = lower + upper + digits + specials + extra
        if not self.enforce_secure.get_active():
            if x < 3:
                x = 3
            self.minlen.set_range(x,50)
            self.maxlen.set_range(x,50)
            return
        now = 0
        now += 26 if lower else 0
        now += 26 if upper else 0
        now += 32 if specials else 0
        now += 10 if digits else 0
        now += 48647 if extra else 0

        if now: # if none selected,this would go FOREVER..
            while now**x < optimal:
                x+=1
            self.minlen.set_range(x,x+50)
            self.maxlen.set_range(x,x+50)

    def generate(self,widget):
        """
        collects info about settings
        sends it to password generator
        stores it to self.list_of_passwords
        """
        lower = self.use_lowercase.get_active()
        upper = self.use_uppercase.get_active()
        digits = self.use_digits.get_active()
        specials = self.use_specials.get_active()
        extra = self.use_extra.get_active()
        minlen = self.minlen.get_value_as_int()
        maxlen = self.maxlen.get_value_as_int()

        if lower+upper+digits+specials+extra:
            # at least one has to be true
            self.list_of_passwords = newrandompass(lower,upper,digits,specials,
                                                    extra,minlen,maxlen)
            #print(self.list_of_passwords)
            self.chosen_password.set_text(self.list_of_passwords[0])
            self.selected_password.set_value(0)
            self.selected_password.set_range(0,len(self.list_of_passwords)-1)
        return

    def show_pass(self,widget):
        text= ''
        # if there is list to choose from
        if maxv:=len(self.list_of_passwords):
            # pass index is in lists
            if maxv > (selvalue:=self.selected_password.get_value_as_int()) >= 0:
                # assign value
                text = self.list_of_passwords[selvalue]
        self.chosen_password.set_text(text)
        return

    def manage_del_pass_page(self):
        self.delete_password_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
        button = Gtk.Button(label='refresh')
        button.connect("clicked",self.data_refresh)
        self.delete_password_page.pack_start(button,False,True,1)

        self.site_select_for_del = Gtk.ComboBox.new_with_model(self.data_store)
        self.data_iterators.append(self.site_select_for_del)
        self.site_select_for_del.connect('changed',self.display)
        renderer = Gtk.CellRendererText()
        self.site_select_for_del.pack_start(renderer,True)
        self.site_select_for_del.add_attribute(renderer,"text",0)
        self.site_select_for_del.set_entry_text_column(0)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=3)
        button= Gtk.Button(label='delete')
        button.connect('clicked',self.manage_entry,'delete_entry')
        hbox.pack_start(self.site_select_for_del,True,True,1)
        hbox.pack_start(button,False,False,0)

        self.delete_password_page.pack_start(hbox,False,False,0)
        self.record_for_del = ''

        self.user_for_del = Gtk.Label(label='self.user_for_del')
        self.usershows.append(self.user_for_del)
        self.delete_password_page.pack_start(self.user_for_del,False,False,0)
        self.pass_for_del = Gtk.Label(label='self.pass_for_del')
        self.passshows.append(self.pass_for_del)
        self.delete_password_page.pack_start(self.pass_for_del,False,False,0)

    def manage_entry(self,widget,strinfo):
        if strinfo == 'delete_entry':
            if todelete:=self.record_for_del:
                if todelete in self.data:
                    self.data.pop(self.data.index(todelete))
                    if not self.data:
                        # no passwords left
                        newpass(self.hashed,delete=True)
                    self.save_all_passwords()

                self.data_refresh()
        return

    def manage_modify_page(self):
        self.modify_password_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
        button = Gtk.Button(label='refresh')
        button.connect("clicked",self.data_refresh)
        self.modify_password_page.pack_start(button,False,True,1)

        self.site_select_for_edit = Gtk.ComboBox.new_with_model(self.data_store)
        self.data_iterators.append(self.site_select_for_edit)
        self.site_select_for_edit.connect('changed',self.display)
        renderer = Gtk.CellRendererText()
        self.site_select_for_edit.pack_start(renderer,True)
        self.site_select_for_edit.add_attribute(renderer,'text',0)
        self.site_select_for_edit.set_entry_text_column(0)

        self.modify_password_page.pack_start(self.site_select_for_edit,True,True,0)
        returnbutton = Gtk.Button(label=f"{'return':^13}")
        returnbutton.connect('clicked',self.save_modified,'refresh')
        self.edit_site = Gtk.Entry()
        self.edit_site.set_editable(False)
        self.edit_site.set_can_focus(False)
        self.edit_site.set_alignment(0.5) # center
        self.edit_site.set_name("noentry")
        self.siteshows.append(self.edit_site)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=3)
        hbox.pack_start(returnbutton,False,False,0)
        button=Gtk.Button(label=f"{'edit':^10}")
        button.connect('clicked',self.edit_entry,self.edit_site)

        hbox.pack_start(self.edit_site,True,True,0)
        hbox.pack_start(button,False,False,0)
        self.modify_password_page.pack_start(hbox,True,True,0)

        savebutton = Gtk.Button(label=f"{'save':^14}")
        savebutton.connect('clicked',self.save_modified,'save')
        self.edit_username = Gtk.Entry()
        self.edit_username.set_editable(False)
        self.edit_username.set_can_focus(False)
        self.edit_username.set_alignment(0.5) # center
        self.edit_username.set_name("noentry")
        self.usershows.append(self.edit_username)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=3)
        hbox.pack_start(savebutton,False,False,0)
        button=Gtk.Button(label=f"{'edit':^10}")
        button.connect('clicked',self.edit_entry,self.edit_username)

        hbox.pack_start(self.edit_username,True,True,0)
        hbox.pack_start(button,False,False,0)
        self.modify_password_page.pack_start(hbox,True,True,0)

        self.edit_password = Gtk.Entry()
        self.edit_password.set_editable(False)
        self.edit_password.set_can_focus(False)
        self.edit_password.set_alignment(0.5) # center
        self.edit_password.set_name("noentry")
        self.passshows.append(self.edit_password)
        button = Gtk.Button(label=f"{'generate':^10}")
        button.connect("clicked",self.button_generate)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=3)
        hbox.pack_start(button,False,False,0)
        button=Gtk.Button(label=f"{'edit':^10}")
        button.connect('clicked',self.edit_entry,self.edit_password)
        hbox.pack_start(self.edit_password,True,True,0)
        hbox.pack_start(button,False,False,0)
        self.modify_password_page.pack_start(hbox,True,True,0)

    def save_modified(self,widget,action):
        """
        modify entry in passwords
        """
        selected = self.site_selection.get_active_iter()
        if selected is not None:
            model = self.site_selection.get_model()
            oldsite = model[selected][0]
            olduser = model[selected][1]
            oldpassword = model[selected][2]
            old = [oldsite,olduser,oldpassword]
            newsite = self.edit_site.get_text()
            newuser = self.edit_username.get_text()
            newpassword = self.edit_password.get_text()
            new = [newsite,newuser,newpassword]
            if old != new:# something has changed
                if action == 'save':
                    # replace it
                    oldindex = self.data.index('\t\t'.join(old))
                    self.data.pop(oldindex)
                    self.data.insert(oldindex,'\t\t'.join(new))
                    # write it to file
                    self.save_all_passwords()
                    self.data_refresh()

                elif action == 'refresh':
                    self.edit_site.set_text(oldsite)
                    self.edit_username.set_text(olduser)
                    self.edit_password.set_text(oldpassword)
        return

    def set_not_editable(self):
        try:
            editers = [self.edit_site,
                self.edit_username,
                self.edit_password]
            for e in editers:
                e.set_editable(False)
                e.set_can_focus(False)
                e.set_name("noentry")
        except AttributeError:
            return
        return

    def edit_entry(self,widget,entry):
        """
        manages editability of entries on edit page
        """
        if self.site_select_for_edit.get_active_iter() is None:
            # if nothing selected, there is nothing to edit
            return
        set = not entry.get_editable()
        editers = [self.edit_site,
                self.edit_username,
                self.edit_password]
        if not set: # if turn off,just turn off
            entry.set_editable(False)
            entry.set_can_focus(False)
            entry.set_name("noentry")
        if set: # if turn on, turn off others
            for e in editers:
                eisentry = e is entry
                e.set_editable(eisentry)
                e.set_can_focus(eisentry)
                e.set_name("noentry")
                #e.set_has_frame(e is entry) # won't work
                if eisentry:
                    e.grab_focus()
                    e.set_name("nowentry")

        return

    def manage_read_pass_page(self):
        self.read_password_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
        button = Gtk.Button(label='refresh')
        button.connect("clicked",self.data_refresh)
        self.read_password_page.pack_start(button,False,False,0)

        self.site_selection = Gtk.ComboBox.new_with_model(self.data_store)
        self.site_selection.connect("changed",self.display)
        self.data_iterators.append(self.site_selection)
        renderer_text = Gtk.CellRendererText()
        self.site_selection.pack_start(renderer_text,True)
        self.site_selection.add_attribute(renderer_text,"text",0)
        self.site_selection.set_entry_text_column(0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=3)
        button = Gtk.Button(label='copy')
        button.connect("clicked",self.copycontext,"site")
        hbox.pack_start(self.site_selection,True,True,0)
        hbox.pack_start(button,False,False,0)
        self.read_password_page.pack_start(hbox,False,False,0)

        self.username_label = Gtk.Label()
        self.username_label.set_text('')
        self.usershows.append(self.username_label)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=3)
        button = Gtk.Button(label='copy')
        button.connect("clicked",self.copycontext,"username")
        hbox.pack_start(self.username_label,True,True,0)
        hbox.pack_start(button,False,False,0)
        self.read_password_page.pack_start(hbox,True,True,0)

        self.password_label = Gtk.Label()
        self.password_label.set_text('')
        self.passshows.append(self.password_label)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=3)
        button = Gtk.Button(label='copy')
        button.connect("clicked",self.copycontext,'password')

        hbox.pack_start(self.password_label,True,True,0)
        hbox.pack_start(button,False,False,0)
        self.read_password_page.pack_start(hbox,True,True,0)

        self.counter_label = Gtk.Label()
        #self.counter_label.set_text('')
        self.read_password_page.pack_start(self.counter_label,True,True,0)
        self.display('')

    def copycontext(self,widget,string):
        index = ['site','username','password'].index(string)
        selected = self.site_selection.get_active_iter()
        #selected = self.data_store.get_active_iter()
        self.clipboard.set_text(self.data_store[selected][index], -1)

    def manage_add_pass_page(self):
        # add passwods
        self.add_password_page = Gtk.Grid()
        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked",self.button_clicked,"create_pw")
        self.add_password_page.attach(save_button,0,0,3,1)

        label_entry_page = Gtk.Label(label="<b>page</b>",use_markup=True)
        self.entry_page = Gtk.Entry()
        self.entry_page.connect("activate",self.button_clicked,"create_pw")
        self.add_password_page.attach(label_entry_page,0,1,1,1)
        self.add_password_page.attach(self.entry_page,1,1,2,1)
        label_username = Gtk.Label(label="<b>username</b>",use_markup=True)
        self.entry_username = Gtk.Entry()
        self.entry_username.connect("activate",self.button_clicked,"create_pw")
        self.no_username = Gtk.CheckButton(label="none")
        self.no_username.connect("toggled",self.hide_text,"entry_username")

        self.add_password_page.attach(label_username,0,2,1,1)
        self.add_password_page.attach(self.entry_username,1,2,1,1)
        self.add_password_page.attach(self.no_username,2,2,1,1)
        label_password = Gtk.Label(label="<b>password</b>",use_markup=True)
        self.entry_password = Gtk.Entry()
        self.entry_password.connect("activate",self.button_clicked,"create_pw")
        self.entry_password.set_visibility(False)
        self.hide_entry_p = Gtk.CheckButton(label="hide")
        self.hide_entry_p.set_active(True)
        self.hide_entry_p.connect("toggled",self.hide_text,"pw_page")

        self.add_password_page.attach(label_password,0,3,1,1)
        self.add_password_page.attach(self.entry_password,1,3,1,1)
        self.add_password_page.attach(self.hide_entry_p,2,3,1,1)

        button_password = Gtk.Button(label="generate password")
        button_password.connect("clicked",self.button_generate)
        self.add_password_page.attach(button_password,0,4,3,1)

    def hide_text(self,widget,string_info):
        """
        for managing showing/hiding input
        """
        value = widget.get_active()
        if string_info == "pw_page":
            self.entry_password.set_visibility(not value)
            self.entry_password.grab_focus_without_selecting()
        if string_info == "main_page":
            self.entry.set_visibility(not value)
            # ready to another entry of password
            self.entry.grab_focus_without_selecting()
        if string_info == "entry_username":
            self.entry_username.set_editable(not value)
            if value:
                self.last_entry_username = self.entry_username.get_text()
                self.entry_username.set_text("")
            else:
                self.entry_username.set_text(self.last_entry_username)
                self.last_entry_username = ""

    def data_refresh(self,*args):
        self.data = uncode(self.hashed)
        self.data_store.clear()
        self.set_not_editable() # edit entries

        for data in self.data:
            site_user_pass = data.split('\t\t')
            self.data_store.append(site_user_pass)
            # prevent using same password twice
            if (p:=site_user_pass[-1]) in self.list_of_passwords:
                self.list_of_passwords.remove(p)
                self.selected_password.set_range(0,len(self.list_of_passwords)-1)

        if self.data:
            del site_user_pass
        self.display('')
        return

    def display(self,widget):
        site,username,password = ('','','')
        #print(f"{widget=}")
        if widget:
            iter = widget.get_active_iter()
            if iter is not None:
                model = widget.get_model()
                for iterator in self.data_iterators:
                    if iterator.get_active_iter() != iter:
                        iterator.set_active_iter(iter)
                site = model[iter][0]
                username = model[iter][1]
                password = model[iter][2]

        self.set_not_editable()
        for siteiter in self.siteshows:
            siteiter.set_text(site)
        for user in self.usershows:
            user.set_text(username)
        for pw in self.passshows:
            if type(pw) is gi.repository.Gtk.Entry:
                pw.set_text(password)
            else:
                pw.set_text(f"{password[:20]}{'...' if len(password) > 20 else ''}")
        self.counter_label.set_text(f"{len(self.data)} passwords")
        if site+username+password:
            self.record_for_del = f"{site}\t\t{username}\t\t{password}"
        return

    def button_generate(self,widget):
        """
        switches to "generate password" page and remembers where it was sent from
        wherefrom
        """
        # remember where it was sent from
        self.generate_for = self.passpage.get_current_page()
        self.use_pass.set_label(f"{'copy' if self.generate_for is None else 'use'} pass")
        # switch page
        self.passpage.set_current_page(4)
        return

    def button_clicked(self,widget,strinfo):
        if strinfo == "password":
            result = validate_password(self.entry.get_text())
            if bool(result) == True:
                # correct password
                self.hashed = result
                self.data_refresh()
                self.notebook.do_switch_page(self.notebook,self.passpage,1)
                self.startpage_default()

            elif result == None:
                # no password in use
                self.description1.set_markup("<b>enter again for confirmation</b>")
                # ready to another entry of password
                self.entry.grab_focus_without_selecting()
            elif result == False:
                # wrong password
                self.wrong_pass+= 1
                if self.wrong_pass > 2:
                    # three tries tops
                    Gtk.main_quit()
                self.description1.set_markup(f"<b>wrong password {self.wrong_pass}/3 !</b>")
                # ready to another entry of password
                self.entry.grab_focus_without_selecting()
            # reset password entry
            self.entry.set_text("")

        if strinfo == "create_pw":
            # save new password
            site = self.entry_page.get_text().strip()
            if self.no_username.get_active():
                username = '  '
            else:
                username = self.entry_username.get_text().strip()
            password = self.entry_password.get_text().strip()
            # only proceed if all cells are filled
            if site and username and password:
                newpass(self.hashed,[site,username,password],add=True)
                self.entry_username.set_text('')
                self.entry_password.set_text('')
                self.entry_page.set_text('')
                self.data_refresh()

print("""
TBD :

color theme change ; maybe through css

""")

win = MyWindow()
win.show_all()
Gtk.main()
