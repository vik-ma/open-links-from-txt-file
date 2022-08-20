import tkinter as tk
from tkinter import BooleanVar, StringVar, filedialog, messagebox, Label, Frame, Button, Entry, Checkbutton, OptionMenu
from tkinter.simpledialog import askstring
import pathlib
import os
import webbrowser
import time
from configparser import ConfigParser

DESKTOP = pathlib.Path.home() / 'Desktop'
                    
#Stops [DEFAULT] in config.ini from being overwritten
config = ConfigParser(default_section=None)
#Checks if config.ini file exits in same directory       
has_config = pathlib.Path("config.ini").exists()    

def write_config():
    """Write changed values to config.ini."""
    with open("config.ini", "w") as configfile:
        config.write(configfile)

if has_config:
    #Reads config.ini if it exists
    config.read("config.ini")
else:
    #Creates default config.ini if it doesn't exist
    config.add_section("DEFAULT")
    config.add_section("USERCONFIG")
    for section in config.sections():
        #Warns when trying to open more than that many links
        config.set(section, "batch_warning", "20")
        #Delay between opening links in milliseconds
        config.set(section, "delay", "250")
        #Default directory when selecting file
        config.set(section, "defaultdir", str(DESKTOP))
        #Closes program after opening links if True
        config.set(section, "autoclose", "False")
        #Opens text file in default text editor if True
        config.set(section, "opentxtfile", "False")
        #Automatically selects saved file on startup if True
        config.set(section, "savetxt", "False")
        #Filepath to the file to be automatically selected
        config.set(section, "savedtxtpath", "No File Selected")
        #Ignores opening links ending with '--' if True
        config.set(section, "ignore_dashes", "True")
    config.add_section("BROWSER_PATHS")
    write_config()

def restore_default_config():
    """Overwrite [USERCONFIG] with [DEFAULT] in config.ini."""
    default_config = config.items("DEFAULT")
    for k, v in default_config:
        config.set("USERCONFIG", k, v)
    write_config()

def set_int_variable(variable, value):
    """Check if integer value is valid and save value to corresponding variable in config.ini."""
    if str(value).isdigit():
        config.set("USERCONFIG", variable, str(value))
        write_config()
    else:
        messagebox.showerror("Error", "Value must be a non-negative integer")

def set_str_variable(variable, value):
    """Save string or boolean value to corresponding variable in config.ini."""
    config.set("USERCONFIG", variable, str(value))
    write_config()

def open_file_in_default_editor(filename):
    """Open file in system's default program."""
    os.startfile(filename)

def read_file(target_file) -> list:
    """ 
    Generate a formatted list.

    Read a .txt file and return a formatted list to be read for the script.
    
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
            if len(line_contents) > 1:
                #Replaces "\t" with spaces in the comment (if there is a comment)        
                x = line_contents[1].split("\t")    
                x = " ".join(x)
                line_contents[1] = x
            formatted_list.append(line_contents)
    return formatted_list


def filter_by_phrase(list, phrase) -> list:
    """
    Generate a filtered list based on phrase.
    
    Take a list of list and return only the items containing the provided phrase in index 1.
    """
    phrase = phrase.lower()
    filtered_list = []
    for line in list:
        if len(line) == 2:
            #Skips if no comment (Index 1 represents the comment)
            if phrase in line[1]:
                filtered_list.append(line)
    return filtered_list


def filter_by_domain(list, phrase) -> list:
    """
    Generate a filtered list based on phrase.

    Take a list of list and return only the items containing the provided phrase in index 0.
    """
    phrase = phrase.lower()
    filtered_list = []
    for line in list:
        if len(line) > 0:
            #Skips empty lines
            if phrase in line[0]:
                filtered_list.append(line)
    return filtered_list


def filter_by_lines(list, start, end) -> list:
    """
    Generate a filtered list based on a given range of numbers.

    Take a list of list and return only the items at the provided indices.
    """
    newlist = []
    [newlist.append(list[n]) for n in range(start-1, end)]
    return newlist

def filter_ignored_links(list) -> list:
    """
    Generate a filtered list based on links that contains two dashes at the end.

    Take a list of list and return only the items which do not end with '--' in index 0.
    """
    filtered_list = []
    for line in list:
        if line[0][-2::] != "--":
            #Checks if the last two characters of the domain are not '--'
            filtered_list.append(line)
    return filtered_list

def strip_dashes_from_links(list) -> list:
    """
    Generate a modified list.

    Take a list of list and return a list where index 0 has had '--' removed from its end.
    """
    filtered_list = []
    for line in list:
        if line[0][-2::] == "--":
            line[0] = line[0][:-2:]
        filtered_list.append(line)
    return filtered_list

def add_browser_path():
    """Save selected browser path and name to config.ini."""
    filename = filedialog.askopenfilename(initialdir="/", title="Select File", 
                                         filetypes=[("Executable file (*.exe)", "*.exe"), ("All Files", "*.*")])
    get_browsername = filename.split("/")
    browsername = get_browsername[-1].split(".")    
    #Takes only the filename of the full path of the file and then splits it by the file extension (.)
    if filename != "":
        #Writes the name of the file selected to [BROWSER_PATHS] in config.ini as well as its full path
        config.set("BROWSER_PATHS", browsername[0], filename)
        write_config()

def remove_browser(browser):
    """Remove selected browser path entry from config.ini."""
    config.remove_option("BROWSER_PATHS", browser)
    write_config()

def get_browser_list() -> list:
    """Return the list of browsers added to config.ini."""
    if config.items("BROWSER_PATHS") == []:
        #If no browsers added in config.ini
        return ["No Browser Added"]
    else:
        #Return the name of all browsers added in [BROWSER_PATHS] in config.ini
        return [option.title() for option in config['BROWSER_PATHS']]

def main():
    """Construct the GUI for the application."""
    root = tk.Tk()
    root.title("Open Links From Text File")

    #Create 600x300 unresizable GUI roughly in the middle of the screen (60px north of center)
    w = 600
    h = 300
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2) - 0
    y = (hs/2) - (h/2) - 60
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    root.resizable(width=False, height=False)
    
    #Lines separating sections of the GUI
    select_file_frame = Frame(height=207, width=410, highlightbackground="black", highlightthickness=1)
    select_file_frame.place(x=-1, y=-1)
    settings_frame = Frame(height=98, width=602, highlightbackground="black", highlightthickness=1)
    settings_frame.place(x=-1, y=203)

    selected_file = StringVar()
    selected_file.set("No File Selected")
    selected_file_label = Label(textvariable=selected_file, fg="#166edb")
    selected_file_label.place(x=8, y=46)

    def select_file():
        """Let user select text file from system and store its path as a variable."""
        filename = filedialog.askopenfilename(initialdir=config.get("USERCONFIG", "defaultdir"), title="Select File", 
                                                    filetypes=[("Text Documents (*.txt)", "*.txt"), ("All Files", "*.*")])
        #If filedialog box gets cancelled, "" is returned
        if filename != "":
            if open_txt_check.get() is True:
                #Opens text file in systems default program if checkbox is checked
                open_file_in_default_editor(filename)
            selected_file.set(filename)

    select_file_button = Button(text="Select Text File", command=select_file, font="arial 13 bold", bg="#3599e6", fg="#1c1c1c")
    select_file_button.place(x=8, y=10)

    select_filter_label = Label(text="Filter:", font="arial 13 bold")
    select_filter_label.place(x=8, y=86)

    current_filter = StringVar()
    current_filter.set("Open All Lines In Document (No Filter Set)")
    display_filter = Label(textvariable=current_filter, fg="#166edb")
    display_filter.place(x=60, y=88)

    filter_phrase_label = Label(text="Open all lines containing comment phrase:")
    filter_phrase_label.place(x=8, y=115)
    filter_domain_label = Label(text="Open all lines containing URL:")
    filter_domain_label.place(x=8, y=145)
    filter_line_label = Label(text="Open all lines in range (Start/End):")
    filter_line_label.place(x=8, y=175)

    set_phrase_filter = Entry(width=20)
    set_phrase_filter.place(x=243, y=116)
    set_phrase_filter_button = Button(text="Set", command=lambda:[apply_phrase_filter(set_phrase_filter.get())])
    set_phrase_filter_button.place(x=373, y=113) 
    #Bind set_phrase_filter entry field to set_phrase_filter_button command when pressing enter
    set_phrase_filter.bind('<Return>', (lambda event: apply_phrase_filter(set_phrase_filter.get()))) 

    set_domain_filter = Entry(width=20)
    set_domain_filter.place(x=243, y=146)
    set_domain_filter_button = Button(text="Set", command=lambda:[apply_domain_filter(set_domain_filter.get())])
    set_domain_filter_button.place(x=373, y=143)
    #Bind set_domain_filter entry field to set_domain_filter_button command when pressing enter
    set_domain_filter.bind('<Return>', (lambda event: apply_domain_filter(set_domain_filter.get())))

    set_line_filter_start = Entry(width=5)
    set_line_filter_end = Entry(width=5)
    set_line_filter_start.place(x=243, y=176)
    set_line_filter_end.place(x=283, y=176)
    set_line_filter_button = Button(text="Set", command=lambda:[apply_line_filter(set_line_filter_start.get(), set_line_filter_end.get())])
    set_line_filter_button.place(x=373, y=173)
    #Bind set_line_filter_start entry field to focus set_line_filter_end when pressing enter
    set_line_filter_start.bind('<Return>', (lambda event: set_line_filter_end.focus()))
    #Bind set_line_filter_enter entry field to set_line_filter_button command when pressing enter
    set_line_filter_end.bind('<Return>', (lambda event: apply_line_filter(set_line_filter_start.get(), set_line_filter_end.get())))

    def apply_phrase_filter(phrase):
        """Set the filter to only include lines which comments contain specific phrase."""
        if phrase != "":
            current_filter.set(f"Open only lines containing comment: '{phrase}'")
            current_filter_type.set("Phrase")
            current_filter_value.set(phrase)
            clear_filter_entries()

    def apply_domain_filter(domain):
        """Set the filter to only include lines which URL contain specific phrase."""
        if domain != "":
            current_filter.set(f"Open only lines containing URL: '{domain}'")
            current_filter_type.set("Domain")
            current_filter_value.set(domain)
            clear_filter_entries()

    def apply_line_filter(start, end):
        """Set the filter to only include lines of a specific index range."""
        if start != "" and end != "":
            current_filter.set(f"Open everything from line {start} to line {end}")
            current_filter_type.set("Lines")
            #Use "," as a delimiter between start value and end value
            current_filter_value.set(str(start)+","+str(end))   
            clear_filter_entries()

    #Determines which type of filter (Comment phrase, link phrase or index range)
    current_filter_type = StringVar()  
    #Stores the actual value to be filtered 
    current_filter_value = StringVar()  

    reset_filter_button = Button(text="Reset Filter", command=lambda:[reset_filter()])
    reset_filter_button.place(x=332, y=83)
    
    def reset_filter():
        """Remove the currently set filter."""
        current_filter.set("Open All Lines In Document (No Filter Set)")
        current_filter_type.set("")
        current_filter_value.set("")
        clear_filter_entries()

    def clear_filter_entries():
        """Empty all filter-related entry fields."""
        set_phrase_filter.delete(0, tk.END)
        set_phrase_filter.insert(0, "")
        set_domain_filter.delete(0, tk.END)
        set_domain_filter.insert(0, "")
        set_line_filter_start.delete(0, tk.END)
        set_line_filter_start.insert(0, "")
        set_line_filter_end.delete(0, tk.END)
        set_line_filter_end.insert(0, "")
    
    open_links_button = Button(text="Open Links", command=lambda:[check_if_file_selected()], font="arial 13 bold", bg="#02f25a", fg="#242424", width=17)
    open_links_button.place(x=415, y=8)
    
    def check_if_file_selected():
        """
        Validate if file has been selected.
        
        If no file has been selected, or if the selected file can't be read as a text file, an error is shown.
        Execute check_if_browser_added() function if no issues found.
        """
        try:
            if selected_file.get() == "No File Selected":
                messagebox.showerror("Error", "Must select a text file to read from first!")
            else:
                #Proceed if no issues
                check_if_browser_added()
        except:
            #If the file cannot be read as a text file
            messagebox.showerror("Error", "Target file can not be read! Select a valid text file.")

    browser_selection = StringVar()
    browser_selection.set(get_browser_list()[0])

    def check_if_browser_added():
        """
        Validate if browse path has been added.
        
        Show error if no browser has ben added. 
        Execute validate_filter() function if no issues found.
        """
        if browser_selection.get() == "No Browser Added":
            messagebox.showerror("Error", "Must add a path to a browser first!")
        else:
            #Proceed if no issues
            validate_filter()

    def validate_filter():
        """
        Validate if filter is legitimate.

        Show error if filter is not valid.
        Generate new list from selected file based of filter settings if filter has been set and is valid.
        Execute check_batch_warning() function if no issues found. 
        """
        filtertype, filtervalue = current_filter_type.get(), current_filter_value.get()
        file = read_file(selected_file.get())
        if filtertype and filtervalue != "":
            match filtertype:
                case "Phrase":
                    #Filter to include only lines containing comment phrase
                    try:
                        if filter_by_phrase(file, filtervalue) != []:
                            #Proceed if no issues
                            check_batch_warning(filter_by_phrase(file, filtervalue))
                        else:
                            #Do not proceed if specific comment phrase was not found in file
                            messagebox.showerror("Error", f"No comment phrase '{filtervalue}' in file!")
                    except Exception as e:
                        #Might be useless
                        messagebox.showerror("Error", e)
                case "Domain":
                    #Filter to include only lines containing domain phrase
                    try:
                        if filter_by_domain(file, filtervalue) != []:
                            #Proceed if no issues
                            check_batch_warning(filter_by_domain(file, filtervalue))
                        else:
                            #Do not proceed if specific domain phrase was not found in file
                            messagebox.showerror("Error", f"No URL containing '{filtervalue}' in file!")
                    except Exception as e:
                        #Might be useless
                        messagebox.showerror("Error", e)
                case "Lines":
                    #Filter to include only lines in specific index range
                    #Start and end value is split by "," delimiter
                    line_index = filtervalue.split(",")
                    error_msg = "Range values must be valid line numbers in file!"
                    try:
                        if int(line_index[0]) > int(line_index[1]):
                            #Do not proceed if start index is greater than end index     
                            messagebox.showerror("Error", error_msg)
                            return
                        if int(line_index[0]) < 1 or int(line_index[1]) < 1:
                            #Do not proceed if start or end index is 0 or below
                            messagebox.showerror("Error", error_msg)
                            return
                        #Proceed if no issues
                        check_batch_warning(filter_by_lines(file, int(line_index[0]), int(line_index[1])))  
                    except IndexError:
                        #Catches out of bounds indices
                        messagebox.showerror("Error", error_msg)
                    except ValueError:
                        #Catches non-integer values
                        messagebox.showerror("Error", error_msg)
        else:
            #Proceed to open whole file if no filter set
            check_batch_warning(file)        

    def check_batch_warning(link_list):
        """Warn user if number of links set to be opened is greater than batch_warning in settings."""
        if [] in link_list:
            #Remove all items containing empty lines
            link_list.remove([])
        if ignore_dash_check.get() is True:
            #Removes all links ending with '--' if checkbox is checked
            link_list = filter_ignored_links(link_list)
        else:
            #Removes double dashes from the end of the links
            link_list = strip_dashes_from_links(link_list)      
        batch_warning = int(config.get("USERCONFIG", "batch_warning"))
        if len(link_list) >= batch_warning and batch_warning != 0:
            #Send warning if number of links is greater than user setting
            msgbox_warning = messagebox.askquestion("Warning", f"You are about to open {len(link_list)} links. Proceed?")
            if msgbox_warning == "yes":
                #Proceed if user clicks yes
                open_links(link_list)
        else:
            #Proceed if number is lower than batch_warning or if batch_warning is set to 0
            open_links(link_list)

    def open_links(link_list):
        """
        Open all links provided in list in selected browser.
        
        Close application if autoclose_checkbox has been ticked.
        """
        browser = config.get("BROWSER_PATHS", browser_selection.get()) + " %s"
        #Converts milliseconds to seconds
        delay = int(config.get("USERCONFIG", "delay"))/1000     
        for link in link_list:
            webbrowser.get(browser).open_new_tab(link[0])
            #Adds delay between every link being opened
            time.sleep(delay)       
        if close_check.get() is True:
            #Closes application after links have been opened if autoclose_checkbox has been ticked
            #Saves any changes made to checkboxes before closing application
            check_checkboxes()      

    #Checkbox to open text file in default text editor if checked when selecting file
    open_txt_check = BooleanVar()
    open_txt_check.set(config.get("USERCONFIG", "opentxtfile"))
    open_txt_checkbox = Checkbutton(text="Also Open File In Default Text Editor", variable=open_txt_check, onvalue=True, offvalue=False)
    open_txt_checkbox.place(x=145, y=5)

    #Checkbox to automatically select same file next time application is opened
    save_txt_check = BooleanVar()
    save_txt_check.set(config.get("USERCONFIG", "savetxt"))
    save_txt_checkbox = Checkbutton(text="Remember file next time program is opened", variable=save_txt_check, onvalue=True, offvalue=False)
    save_txt_checkbox.place(x=145, y=25)

    #Checkbox to ignore opening links ending with '--' if checked
    ignore_dash_check = BooleanVar()
    ignore_dash_check.set(config.get("USERCONFIG", "ignore_dashes"))
    ignore_dash_checkbox = Checkbutton(text="Don't open links ending with '--'", variable=ignore_dash_check, onvalue=True, offvalue=False)
    ignore_dash_checkbox.place(x=7, y=64)

    if save_txt_check.get() is True:
        #Automatically select saved file if setting is on
        selected_file.set(config.get("USERCONFIG", "savedtxtpath"))

    def helpwindow():
        """Show help window in GUI."""
        messagebox.showinfo("Help", "Add the path to the browser you want to use by clicking the 'Add Browser Path' button and then locate the .exe file of the browser on your system. You can add multiple browsers and the paths will be stored in the 'config.ini' file.\n\nSelect a text file to read from. The script will open the first entry of every line up until the first space or tab. Everything after the space is considered as a comment. Empty lines are not considered an entry.\n\nSet a filter only open specific lines in the text document.\n\nIf the script fails to execute, the added browser is not valid.")

    help_button = Button(text="Help", command=helpwindow, font="arial 13 bold")
    help_button.place(x=10, y=212)

    #Show and allow user to change default directory where user selects text files
    defaultdir_get = StringVar()
    defaultdir_get.set("Default Directory: " + config.get("USERCONFIG", "defaultdir"))
    defaultdir_label = Label(textvariable=defaultdir_get)
    defaultdir_label.place(x=155, y=210)
    set_defaultdir_button = Button(text="Change", command=lambda:[set_default_dir()])
    set_defaultdir_button.place(x=542, y=208)

    #Show and allow user to change how many links can be opened without warning
    warning_label = Label(text="Warn before opening X amount of links (0 = No warning):")
    warning_label.place(x=155, y=240)
    change_warning = Entry(width=5)
    change_warning.place(x=500, y=241)
    change_warning.insert(0, config.get("USERCONFIG", "batch_warning"))
    change_warning.config(state = "readonly")
    set_warning_button = Button(text="Change", command=lambda:[show_input_box("batch_warning")])
    set_warning_button.place(x=542, y=238)

    #Show and allow user to change the delay between opening links
    delay_label = Label(text="Delay between opening links (In milliseconds):")
    delay_label.place(x=155, y=270)
    change_delay = Entry(width=5)
    change_delay.place(x=500, y=271)
    change_delay.insert(0, config.get("USERCONFIG", "delay"))
    change_delay.config(state = "readonly")
    set_delay_button = Button(text="Change", command=lambda:[show_input_box("delay")])
    set_delay_button.place(x=542, y=268)

    def show_input_box(variable):
        """Set value for specified config variable based on user input."""
        ask = askstring("Set Value", "Enter new value:")
        if ask != None:
            set_int_variable(variable, ask)
            reset_variables()

    def set_default_dir():
        """Set the default directory when selecting text file and save value in config.ini."""
        folder = filedialog.askdirectory(initialdir=config.get("USERCONFIG", "defaultdir"))
        if folder != "":
            config.set("USERCONFIG", "defaultdir", folder)
            write_config()
            defaultdir_get.set("Default Directory: " + config.get("USERCONFIG", "defaultdir"))       

    def restore_default_warning():
        """Overwrite all variables in config.ini under [USERCONFIG] with [DEFAULT] values if user clicks "Yes"."""
        ask = messagebox.askquestion("Restore Default Config", "Do you really want to reset to default configuration? \nThis can not be undone.")
        if ask == "yes":
            #Proceed if user clicks yes
            restore_default_config()
            reset_variables()
            close_check.set(config.get("USERCONFIG", "autoclose"))
            open_txt_check.set(config.get("USERCONFIG", "opentxtfile"))
            save_txt_check.set(config.get("USERCONFIG", "savetxt"))
            ignore_dash_check.set(config.get("USERCONFIG", "ignore_dashes"))

    restore_default_button = Button(text="Restore Default Settings", command=restore_default_warning)
    restore_default_button.place(x=10, y=265)
    
    def reset_variables():
        """Update values of config variables in GUI."""
        #Remove readonly
        change_delay.config(state = tk.NORMAL)
        change_warning.config(state = tk.NORMAL)    
        #Update fields
        change_warning.delete(0, tk.END)
        change_delay.delete(0, tk.END)
        change_warning.insert(0, config.get("USERCONFIG", "batch_warning"))
        change_delay.insert(0, config.get("USERCONFIG", "delay"))
        #Set readonly again
        change_delay.config(state = "readonly")
        change_warning.config(state = "readonly")

    #Checkbox to automatically close program after opening links
    close_check = BooleanVar()
    close_check.set(config.get("USERCONFIG", "autoclose"))
    autoclose_checkbox = Checkbutton(text="Close Program After Opening", variable=close_check, onvalue=True, offvalue=False)
    autoclose_checkbox.place(x=412, y=42)

    def check_checkboxes(): 
        """Update value of checkboxes if any change has been made."""
        if config.get("USERCONFIG", "autoclose") != close_check.get():
            set_str_variable("autoclose", close_check.get()) 
        if config.get("USERCONFIG", "opentxtfile") != open_txt_check.get():
            set_str_variable("opentxtfile", open_txt_check.get()) 
        if config.get("USERCONFIG", "savetxt") != save_txt_check.get():
            set_str_variable("savetxt", save_txt_check.get())
        if config.get("USERCONFIG", "ignore_dashes") != ignore_dash_check.get():
            set_str_variable("ignore_dashes", ignore_dash_check.get())
        close()

    browser_label = Label(text="Open In Browser:", font="arial 13 bold")
    browser_label.place(x=415, y=75)

    browser_menu = OptionMenu(root, browser_selection, *get_browser_list())
    browser_menu.configure(font="arial 11 bold")
    browser_menu.place(x=413, y=100)
    
    add_browser_button = Button(text="Add Browser Path", command=lambda:[add_browser_path(), reset_browser_menu()])
    add_browser_button.place(x=415, y=143)

    del_browser_button = Button(text="Remove Browser Path", command=lambda:[remove_browser(browser_selection.get()), reset_browser_menu()])
    del_browser_button.place(x=415, y=173)

    def reset_browser_menu():
        """Update the "Select Browser" dropdown menu after a change in the list of added browsers"""
        #Solution from https://stackoverflow.com/questions/17580218/changing-the-options-of-a-optionmenu-when-clicking-a-button
        browser_selection.set(get_browser_list()[0])
        browser_menu['menu'].delete(0, 'end')
        new_choices = get_browser_list()
        for choice in new_choices:
            browser_menu['menu'].add_command(label=choice, command=tk._setit(browser_selection, choice))

    def close():
        """Close application after updating savedtxtpath variable (if changed)."""
        if save_txt_check.get() is True:
            #Saves last selected file to config.ini if save_txt_checkbox is ticked
            set_str_variable("savedtxtpath", selected_file.get())
        else:
            set_str_variable("savedtxtpath", "No File Selected")
        root.destroy()
    
    def test():
        print("ADSdsadsadasasdadss")

    test_button = Button(text="TEST", command=lambda:[test()])
    test_button.place(x=105, y=220)

    #Update checkboxes when closing application. Executes second command before calling root.destroy().
    root.protocol("WM_DELETE_WINDOW", lambda:[check_checkboxes()])

    root.mainloop()
    
if __name__ == "__main__":
    main()