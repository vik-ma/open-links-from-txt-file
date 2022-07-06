import tkinter as tk
from tkinter import BooleanVar, StringVar, filedialog, Text, messagebox, Label
import pathlib
import os
import webbrowser
import time
from configparser import ConfigParser

DESKTOP = pathlib.Path.home() / 'Desktop'

batch_warning = 20      #Warns when trying to open more than that many links
delay = 250             #Delay between opening links in milliseconds
defaultdir = DESKTOP    #Default directory when selecting file
autoclose = False       #Closes program after opening links if True
opentxtfile = False     #Opens text file in default text editor if True

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
    if str(input).isdigit():
        config.set("USERCONFIG", "batch_warning", str(input))
        write_config()
    else:
        messagebox.showerror("Error", "Value must be a non-negative integer")

def set_delay(input):
    if str(input).isdigit():
        config.set("USERCONFIG", "delay", str(input))
        write_config()
    else:
        messagebox.showerror("Error", "Value must be a non-negative integer")

def set_default_dir():
    folder = filedialog.askdirectory(initialdir=config.get("USERCONFIG", "defaultdir"))
    if folder != "":
        config.set("USERCONFIG", "defaultdir", folder)
        write_config()

def set_autoclose(value):
    config.set("USERCONFIG", "autoclose", str(value))
    write_config()

def set_opentxtfile(value):
    config.set("USERCONFIG", "opentxtfile", str(value))
    write_config()

def open_file_in_default_editor(filename):
    os.startfile(filename)

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


def filter_by_lines(l, start, end) -> list:
    newlist = []
    [newlist.append(l[n]) for n in range(start-1, end)]
    return newlist


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
    root.title("Open Links")
    browser_selection = tk.StringVar(root)
    browser_selection.set(get_browser_list()[0])

    w = 600
    h = 300
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2) - 0
    y = (hs/2) - (h/2) - 60
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    root.resizable(width=False, height=False)
    
    selected_file = StringVar()
    selected_file.set("No File Selected")
    selected_file_label = tk.Label(root, textvariable=selected_file)
    selected_file_label.place(x=350, y=10)

    def select_file():
        filename = filedialog.askopenfilename(initialdir=config.get("USERCONFIG", "defaultdir"), title="Select File", 
                                                    filetypes=[("Text Documents (*.txt)", "*.txt"), ("All Files", "*.*")])
        if filename != "":
            if open_txt_check.get() is True:
                open_file_in_default_editor(filename)
            selected_file.set(filename)

    select_file_button = tk.Button(root, text="Select Text File", command=select_file, font="Bold")
    select_file_button.place(x=185, y=10)

    def check_if_file_selected():
        if selected_file.get() == "No File Selected":
            messagebox.showerror("Error", "Must select a text file to read from first!")
        else:
            check_if_browser_added()

    def check_if_browser_added():
        if browser_selection.get() == "No Browser Added":
            messagebox.showerror("Error", "Must add a path to a browser first!")
        else:
            validate_input()

    browser_label = tk.Label(root, text="Open In Browser:", font="Bold")
    browser_label.place(x=12, y=10)
    browser_menu = tk.OptionMenu(root, browser_selection, *get_browser_list())
    browser_menu.configure(font="Bold")
    browser_menu.place(x=10, y=35)

    select_filter_label = tk.Label(root, text="Select Filter:", font="Bold")
    select_filter_label.place(x=185, y=50)

    

    filter_phrase_label = tk.Label(root, text="Open all lines containing comment phrase:")
    filter_phrase_label.place(x=185, y=75)
    filter_domain_label = tk.Label(root, text="Open all lines containing URL:")
    filter_domain_label.place(x=185, y=105)
    filter_line_label = tk.Label(root, text="Open all lines in range (Start/End):")
    filter_line_label.place(x=185, y=135)

    set_phrase_filter = tk.Entry(root, width=20)
    set_phrase_filter.place(x=405, y=76)
    set_domain_filter = tk.Entry(root, width=20)
    set_domain_filter.place(x=405, y=106)
    set_line_filter_start = tk.Entry(root, width=5)
    set_line_filter_end = tk.Entry(root, width=5)
    set_line_filter_start.place(x=405, y=136)
    set_line_filter_end.place(x=445, y=136)

    current_filter = StringVar()
    current_filter.set("Open All Lines In Document (No Filter Set)")
    display_filter = tk.Label(root, textvariable=current_filter)
    display_filter.place(x=350, y=30)

    set_phrase_filter_button = tk.Button(root, text="Set", command=lambda:[apply_phrase_filter(set_phrase_filter.get())])
    set_phrase_filter_button.place(x=535, y=73)
    set_domain_filter_button = tk.Button(root, text="Set", command=lambda:[apply_domain_filter(set_domain_filter.get())])
    set_domain_filter_button.place(x=535, y=103)
    set_line_filter_button = tk.Button(root, text="Set", command=lambda:[apply_line_filter(set_line_filter_start.get(), set_line_filter_end.get())])
    set_line_filter_button.place(x=535, y=133)
    set_no_filter_button = tk.Button(root, text="Reset Filter", command=lambda:[reset_filter()])
    set_no_filter_button.place(x=495, y=163)

    

    def apply_phrase_filter(phrase):
        if phrase != "":
            current_filter.set(f"Filter by phrase: {phrase}")
            current_filter_type.set("Phrase")
            current_filter_value.set(phrase)
            clear_filter_entries()

    def apply_domain_filter(domain):
        if domain != "":
            current_filter.set(f"Filter by URL: {domain}")
            current_filter_type.set("Domain")
            current_filter_value.set(domain)
            clear_filter_entries()

    def apply_line_filter(start, end):
        if start != "" and end != "":
            current_filter.set(f"Open Lines {start} - {end}")
            current_filter_type.set("Lines")
            current_filter_value.set(str(start)+","+str(end))
            clear_filter_entries()

    def reset_filter():
        current_filter.set("Open All Lines In Document (No Filter Set)")
        current_filter_type.set("")
        current_filter_value.set("")
        clear_filter_entries()

    def clear_filter_entries():
        set_phrase_filter.delete(0, tk.END)
        set_phrase_filter.insert(0, "")
        set_domain_filter.delete(0, tk.END)
        set_domain_filter.insert(0, "")
        set_line_filter_start.delete(0, tk.END)
        set_line_filter_start.insert(0, "")
        set_line_filter_end.delete(0, tk.END)
        set_line_filter_end.insert(0, "")

    current_filter_type = StringVar()
    current_filter_value = StringVar()

    def validate_input():
        filtertype, filtervalue = current_filter_type.get(), current_filter_value.get()
        file = read_file(selected_file.get())
        if filtertype and filtervalue != "":
            match filtertype:
                case "Phrase":
                    try:
                        if filter_by_phrase(file, filtervalue) != []:
                            check_batch_warning(filter_by_phrase(file, filtervalue))
                        else:
                            messagebox.showerror("Error", f"No phrase '{filtervalue}' in file!")
                    except Exception as e:                                      #Might never catch anything
                        messagebox.showerror("Error", e)

                case "Domain":
                    try:
                        if filter_by_domain(file, filtervalue) != []:
                            check_batch_warning(filter_by_domain(file, filtervalue))
                        else:
                            messagebox.showerror("Error", f"No URL containing '{filtervalue}' in file!")
                    except Exception as e:                                      #Might never catch anything
                        messagebox.showerror("Error", e)

                case "Lines":
                    line_index = filtervalue.split(",")
                    error_msg = "Range values must be valid line numbers in file!"
                    try:
                        if int(line_index[0]) > int(line_index[1]):             #Check if start index is greater than end index     
                            messagebox.showerror("Error", error_msg)
                            return
                        if int(line_index[0]) < 1 or int(line_index[1]) < 1:    #Check if start or end index is 0 or below
                            messagebox.showerror("Error", error_msg)
                            return
                        check_batch_warning(filter_by_lines(file, int(line_index[0]), int(line_index[1])))  
                    except IndexError:                                          #Catches out of bounds indices
                        messagebox.showerror("Error", error_msg)
                    except ValueError:                                          #Catches non-integer values
                        messagebox.showerror("Error", error_msg)
        else:
            check_batch_warning(file)

    def check_batch_warning(link_list):
        if [] in link_list:
            link_list.remove([])
        batch_warning = int(config.get("USERCONFIG", "batch_warning"))
        if len(link_list) >= batch_warning and batch_warning != 0:
            msgbox_warning = messagebox.askquestion("Warning", f"You are about to open {len(link_list)} links. Proceed?")
            if msgbox_warning == "yes":
                open_links(link_list)
        else:
            open_links(link_list)

    def open_links(link_list):
        browser = config.get("BROWSER_PATHS", browser_selection.get()) + " %s"
        delay = int(config.get("USERCONFIG", "delay"))/1000
        for link in link_list:
            webbrowser.get(browser).open_new_tab(link[0])
            time.sleep(delay)
        if close_check.get() is True:
            check_checkboxes()
            close()

    warning_label = tk.Label(root, text="Warn before opening X amount of links (0 = No warning):")
    warning_label.place(x=10, y=240)

    change_warning = tk.Entry(root, width=5)
    change_warning.place(x=325, y=241)
    change_warning.insert(0, config.get("USERCONFIG", "batch_warning"))

    delay_label = tk.Label(root, text="Delay between opening links (In milliseconds):")
    delay_label.place(x=10, y=270)

    change_delay = tk.Entry(root, width=5)
    change_delay.place(x=325, y=271)
    change_delay.insert(0, config.get("USERCONFIG", "delay"))

    defaultdir_get = StringVar()
    defaultdir_get.set("Default Directory: " + config.get("USERCONFIG", "defaultdir"))
    defaultdir_label = tk.Label(root, textvariable=defaultdir_get)
    defaultdir_label.place(x=10, y=210)

    set_warning_button = tk.Button(root, text="Change", command=lambda:[set_batch_warning(change_warning.get()), reset_variables()])
    set_warning_button.place(x=365, y=236)
    set_delay_button = tk.Button(root, text="Change", command=lambda:[set_delay(change_delay.get()), reset_variables()])
    set_delay_button.place(x=365, y=266)
    set_defaultdir_button = tk.Button(root, text="Change", command=lambda:[set_default_dir(), reset_variables()])
    set_defaultdir_button.place(x=365, y=206)

    def check_checkboxes(): 
        if config.get("USERCONFIG", "autoclose") != close_check.get():
            set_autoclose(close_check.get()) 
        if config.get("USERCONFIG", "opentxtfile") != open_txt_check.get():
            set_opentxtfile(open_txt_check.get()) 

    close_check = tk.BooleanVar()
    close_check.set(config.get("USERCONFIG", "autoclose"))
    autoclose_checkbox = tk.Checkbutton(root, text="Close Program After Opening", variable=close_check, onvalue=True, offvalue=False)
    autoclose_checkbox.place(x=150, y=160)

    open_txt_check = tk.BooleanVar()
    open_txt_check.set(config.get("USERCONFIG", "opentxtfile"))
    open_txt_checkbox = tk.Checkbutton(root, text="Also Open File In Default Text Editor", variable=open_txt_check, onvalue=True, offvalue=False)
    open_txt_checkbox.place(x=150, y=180)

    def reset_browser_menu():
        """Updates the "Select Browser" dropdown menu after a change in the list of added browsers
           Solution from https://stackoverflow.com/questions/17580218/changing-the-options-of-a-optionmenu-when-clicking-a-button
        """
        browser_selection.set(get_browser_list()[0])
        browser_menu['menu'].delete(0, 'end')

        new_choices = get_browser_list()
        for choice in new_choices:
            browser_menu['menu'].add_command(label=choice, command=tk._setit(browser_selection, choice))

    def reset_variables():
        defaultdir_get.set("Default Directory: " + config.get("USERCONFIG", "defaultdir"))        
        change_warning.delete(0, tk.END)
        change_delay.delete(0, tk.END)
        change_warning.insert(0, config.get("USERCONFIG", "batch_warning"))
        change_delay.insert(0, config.get("USERCONFIG", "delay"))
    
    def restore_default_warning():
        ask = messagebox.askquestion("Restore Default Config", "Do you really want to reset to default configuration? \nThis cannot be undone.")
        if ask == "yes":
            restore_default_config()
            reset_variables()
            close_check.set(config.get("USERCONFIG", "autoclose"))
            open_txt_check.set(config.get("USERCONFIG", "opentxtfile"))

    def close():
        root.destroy()

    #Updates checkboxes when closing. Executes second command after first one.
    root.protocol("WM_DELETE_WINDOW", lambda:[close(), check_checkboxes()])

    restore_default_button = tk.Button(root, text="Restore Default Settings", command=restore_default_warning)
    restore_default_button.place(x=10, y=175)

    add_remove_browser_label = tk.Label(root, text="Add/Remove Browser Path:")
    add_remove_browser_label.place(x=10, y=87)

    add_browser_button = tk.Button(root, text="Add Browser", command=lambda:[add_browser_path(), reset_browser_menu()])
    add_browser_button.place(x=10, y=110)

    del_browser_button = tk.Button(root, text="Remove Browser", command=lambda:[remove_browser(browser_selection.get()), reset_browser_menu()])
    del_browser_button.place(x=10, y=140)
    
    test_button = tk.Button(root, text="TEST", command=lambda:[check_if_file_selected()])
    test_button.place(x=530, y=230)

    root.mainloop()
    

draw_gui()
#test_filter_by_domain()
#test_filter_by_lines()
#test_filter_phrase()
#print_test_file()
