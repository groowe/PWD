"""CSS styling management for new_pass Gtk GUI."""

CSS_FILE = 'pm.css'  # for saving / loading settings

# default css settings
LATTICED = ", ".join(["#262626", "#626262"]*40)

DEFAULT_CSS = """
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
entry, label { border-color : #FFFFFF;
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
box {  background : transparent; }

button:active {
    box-shadow: 0 12px 6px 0 rgba(100, 100, 100, 0.24),
                0 17px 20px 0 rgba(100, 100, 100, 0.24);
    }
button:hover {
    background-image: linear-gradient(grey, black);
    box-shadow: 0 10px 16px 0 rgba(0, 0, 0, 0.24),
                0 18px 16px 0 rgba(0, 0, 0, 0.19);
    }

entry:focus {
    color : white;
    text-shadow: 1px 0px grey;
    background: black;
    }
#nowentry {
    background-image: linear-gradient(#606060, #060606);
    }

progressbar > trough > progress {
    background-image: linear-gradient(#606060, #6A6A6A, #060606, #A6A6A6);
    }
    """
DEFAULT_CSS += f"#noentry {{ background-image: linear-gradient({LATTICED});}}"


def read_saved_css() -> str:
    """Load saved css as string."""
    # no mechanism for change now,
    # so return variable directly
    return DEFAULT_CSS
    try:  # read saved settings
        with open(CSS_FILE, 'r') as file:
            data = '\n'.join(file.readlines())
    except (FileNotFoundError, UnicodeDecodeError):
        # file doesn't exists yet
        try:
            with open(CSS_FILE, 'w') as file:
                file.writelines(DEFAULT_CSS.split('\n'))
            return read_saved_css()
        except (FileNotFoundError, UnicodeDecodeError):
            # problem with writing file down
            # not problem now, but it could be in future
            # print("unable to save settings, unable remember changes!")
            return DEFAULT_CSS
    return data
