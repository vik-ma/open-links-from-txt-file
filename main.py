import tkinter as tk
from tkinter import filedialog, Text, messagebox
import pathlib
import webbrowser
import time
from configparser import ConfigParser

DESKTOP = pathlib.Path.home() / 'Desktop'

batch_warning = 20
delay = 0.25
defaultdir = DESKTOP
autoclose = False
opentxtfile = False

config = ConfigParser(default_section=None)         #Stops [DEFAULT] in config.ini from being overwritten
has_config = pathlib.Path("config.ini").exists()

def write_config():
    with open("config.ini", "w") as configfile:
        config.write(configfile)

if has_config:
    config.read("config.ini")
    batch_warning = config.get("USERCONFIG", "batch_warning")
    delay = config.get("USERCONFIG", "delay")
    defaultdir = config.get("USERCONFIG", "defaultdir") 
    autoclose = config.get("USERCONFIG", "autoclose")
    opentxtfile = config.get("USERCONFIG", "opentxtfile")

else:                                               #Creates default config.ini if it doesn't exist
    config.add_section("DEFAULT")
    config.add_section("USERCONFIG")
    for section in config.sections():
        config.set(section, "batch_warning", str(batch_warning))
        config.set(section, "delay", str(delay))
        config.set(section, "defaultdir", str(DESKTOP))
        config.set(section, "autoclose", str(autoclose))
        config.set(section, "opentxtfile", str(opentxtfile))
    config.add_section("BROWSER_PATHS")
    write_config()

def restore_default_config():
    default_config = config.items("DEFAULT")

    for k, v in default_config:
        config.set("USERCONFIG", k, v)

    write_config()

def set_batch_warning(input):
    if isinstance(input, int):
        config.set("USERCONFIG", "batch_warning", str(input))
        write_config()
    else:
        messagebox.showerror("Error", "Value must be an Int")

def set_delay(input):
    if isinstance(input, float | int):
        config.set("USERCONFIG", "delay", str(input))
        write_config()
    else:
        messagebox.showerror("Error", "Value must be a Float or an Int")

def set_default_dir():
    folder = filedialog.askdirectory(initialdir=DESKTOP)
    if folder != "":
        config.set("USERCONFIG", "defaultdir", folder)
        write_config()

def set_autoclose(value):
    config.set("USERCONFIG", "autoclose", str(value))
    write_config()

def set_opentxtfile(value):
    config.set("USERCONFIG", "opentxtfile", str(value))
    write_config()

def read_file(target_file) -> list:
    """ Takes a .txt file, returns a formatted list for the script

        Each entry in the list corresponds to one line in the .txt-file and consists of another list with 2 indices:
            Index 0 stores the URL as a string
            Index 1 stores the comment (if there is one) next to the URL as a string
    """

    formatted_list = []

    with open (target_file, "r") as file:
        file_contents = file.readlines()
        
        for f in file_contents:
            f = f.strip()
            f = f.lower()
            line_contents = f.split(None,1)
            if (len(line_contents) > 1):            # Replaces "\t" with spaces in the comment (if there is a comment)
                x = line_contents[1].split("\t")    
                x = " ".join(x)
                line_contents[1] = x
            formatted_list.append(line_contents)
        
    return formatted_list


def filter_by_phrase(l, p) -> list:
    phrase = p.lower()
    filtered_list = []

    for i in l:
        if (len(i)==2):
            if (phrase in i[1]):
                filtered_list.append(i)

    return filtered_list


def filter_by_domain(l, p) -> list:
    phrase = p.lower()
    filtered_list = []

    for i in l:
        if (len(i)>0):
            if (phrase in i[0]):
                filtered_list.append(i)

    return filtered_list


def filter_by_lines(l, x, y) -> list:
    start = x-1
    end = y
    return l[start:end]


def print_list(list):
    for i in list:
        print(i)


def print_test_file():
    test_txt_file = "test.txt"
    print_list(read_file(test_txt_file))

def test_filter_phrase():
    list = filter_by_phrase(read_file("test.txt"), "asdf")
    print(list)

def test_filter_by_lines():
    list = filter_by_lines(read_file("test.txt"), 3, 8)
    print(list)

def test_filter_by_domain():
    list = filter_by_domain(read_file("test.txt"), "test")
    print(list)


def select_file():
        filename = filedialog.askopenfilename(initialdir=DESKTOP, title="Select File", 
                                                filetypes=[("Text Documents (*.txt)", "*.txt"), ("All Files", "*.*")])
        print(filename)

def add_browser_path():
    filename = filedialog.askopenfilename(initialdir="/", title="Select File", 
                                         filetypes=[("Executable file (*.exe)", "*.exe"), ("All Files", "*.*")])
    get_browsername = filename.split("/")
    browsername = get_browsername[-1].split(".")

    if filename != "":
        config.set("BROWSER_PATHS", browsername[0], filename)
        write_config()

def remove_browser(browser):
    config.remove_option("BROWSER_PATHS", browser)
    write_config()

def get_browser_list() -> list:
    if config.items("BROWSER_PATHS") == []:
        return ["No Browser Added"]
    else:
        return [option.title() for option in config['BROWSER_PATHS']]

def draw_gui():
    root = tk.Tk()
    root.title("Test")
    browser_selection = tk.StringVar(root)
    browser_selection.set(get_browser_list()[0])

    w = 600
    h = 300
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2) - 0
    y = (hs/2) - (h/2) - 60
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    select_file_button = tk.Button(root, text="Select File", command=select_file)
    select_file_button.place(x=400, y=20)

    browser_menu = tk.OptionMenu(root, browser_selection, *get_browser_list())
    browser_menu.place(x=20, y=150)

    restore_default_button = tk.Button(root, text="Restore Default Settings", command=restore_default_config)
    restore_default_button.place(x=10, y=250)
    
    def check_autoclose(): 
        if config.get("USERCONFIG", "autoclose") != close_check.get():
            set_autoclose(close_check.get())   
        if close_check.get() is True:
            close()

    close_check = tk.BooleanVar()
    autoclose_checkbox = tk.Checkbutton(root, text="Close Program After Opening", variable=close_check, onvalue=True, offvalue=False)
    autoclose_checkbox.place(x=300, y=200)

    
    def reset_browser_menu():
        """Updates the "Select Browser" dropdown menu after a change in the list of added browsers
           Solution from https://stackoverflow.com/questions/17580218/changing-the-options-of-a-optionmenu-when-clicking-a-button
        """
        browser_selection.set(get_browser_list()[0])
        browser_menu['menu'].delete(0, 'end')

        new_choices = get_browser_list()
        for choice in new_choices:
            browser_menu['menu'].add_command(label=choice, command=tk._setit(browser_selection, choice))

    def close():
        root.destroy()

    

    add_browser_button = tk.Button(root, text="Add Browser", command=lambda:[add_browser_path(), reset_browser_menu()])
    add_browser_button.place(x=40, y=20)

    del_browser_button = tk.Button(root, text="Remove Browser", command=lambda:[remove_browser(browser_selection.get()), reset_browser_menu()])
    del_browser_button.place(x=100, y=80)
    
    test_button = tk.Button(root, text="TEST", command="")
    test_button.place(x=200, y=30)

    root.mainloop()
    

draw_gui()
#test_filter_by_domain()
#test_filter_by_lines()
#test_filter_phrase()
#print_test_file()
