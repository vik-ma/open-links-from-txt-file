import tkinter as tk
from tkinter import filedialog, Text
import pathlib
import webbrowser
import time
import configparser
from configparser import ConfigParser

DESKTOP = pathlib.Path.home() / 'Desktop'

batch_warning = 20
delay = 0.25
defaultdir = DESKTOP

config = ConfigParser(default_section=None)         #Stops [DEFAULT] in config.ini from being overwritten
has_config = pathlib.Path("config.ini").exists()

if has_config:
    config.read("config.ini")
    batch_warning = config.get("USERCONFIG", "batch_warning")
    delay = config.get("USERCONFIG", "delay")
    defaultdir = config.get("USERCONFIG", "defaultdir") 
else:                                           #Creates default config.ini if it doesn't exist
    config.add_section("DEFAULT")
    config.add_section("USERCONFIG")
    config.add_section("BROWSER_PATHS")
    config.set("DEFAULT", "batch_warning", str(batch_warning))
    config.set("DEFAULT", "delay", str(delay))
    config.set("DEFAULT", "defaultdir", str(DESKTOP))
    config.set("USERCONFIG", "batch_warning", str(batch_warning))
    config.set("USERCONFIG", "delay", str(delay))
    config.set("USERCONFIG", "defaultdir", str(DESKTOP))
    with open("config.ini", "w") as configfile:
        config.write(configfile)


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
            if (len(line_contents) > 1):                        # Replaces "\t" with spaces in the comment (if there is a comment)
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

def add_browser_path():
    filename = filedialog.askopenfilename(initialdir="/", title="Select File", 
                                         filetypes=[("Executable file (*.exe)", "*.exe"), ("All Files", "*.*")])
    get_browsername = filename.split("/")
    browsername = get_browsername[-1].split(".")

    if filename != "":
        config.set("BROWSER_PATHS", browsername[0], filename)
        with open("config.ini", "w") as configfile:
            config.write(configfile)

def draw_gui():
    root = tk.Tk()
    root.title("Test")

    w = 600
    h = 300
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2) - 0
    y = (hs/2) - (h/2) - 60
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    select_file_button = tk.Button(root, text="Select File", command=select_file)
    select_file_button.place(x=400, y=20)
    add_browser_button = tk.Button(root, text="Add Browser", command=add_browser_path)
    add_browser_button.place(x=40, y=20)
    root.mainloop()

draw_gui()
#test_filter_by_domain()
#test_filter_by_lines()
#test_filter_phrase()
#print_test_file()
