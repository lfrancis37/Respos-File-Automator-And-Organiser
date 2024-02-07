
'''
    Make sure required dependencies are installed
'''

import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog, ttk, PhotoImage
import sys
import configparser
import csv
import os
import pickle
import shutil
from datetime import datetime
import platform
from itertools import combinations

try:
    import customtkinter as ctk

except ImportError:
    import subprocess
    messagebox.showinfo("Installing Dependencies", "Installing required dependencies...")
    subprocess.check_call(['pip', 'install', 'customtkinter'])
    messagebox.showinfo("Installation Complete", "Installation complete.")
    

import customtkinter as ctk

"""
    Declared variables and setup
"""
config_file = "config.ini"
instances_file = "instances.pkl"
dir_to = None
pickle_exists = False
directory_to_empty = False
num_of_errors = 0
num_plus_button_clicked = 0
running = False
make_backup = True
errors = False
# Passing the config file for retaining data on text boxes and dropdowns in the program
config = configparser.ConfigParser()

# Checks if config file exists, if not use the default values
if not os.path.exists(config_file):
    config["Settings"] = {
        "default_backup_directory": "Enter Directory",
        "interval_timing": "5 Min",
        "backup_saves": "Last 3 Saves",
    }
    # It would also create a config file which things can be saved to
    with open(config_file, "w") as configfile:
        config.write(configfile)

# Read the config file
config.read(config_file)

# Assign these variables the ones that are loaded
Backup_Directory = config.get("Settings", "default_backup_directory")
default_directory_from = config.get("Settings", "directory_going_from")
backup_history = config.get("Settings", "backup_history")
run_delay = config.get("Settings", "run_delay")

# Dict that holds the amount of backup that will be saved. Used in one of the dropdown menus
backup_saves_dict = {
    "Last Save": 1,
    "Last 3 Saves": 3,
    "Last 6 Saves - Not Recommended": 6,
    "Last 10 Saves - Not Recommended": 10,
}

# Dict that contains the intervals of running the program
intervals_dict = {
    "10 Second - Test": 10000,
    "5 Min": 5 * 60000,
    "10 Min": 10 * 60000,
    "30 Min": 30 * 60000,
    "1 hr": 3600000,
    "4hr": 4 * 3600000,
    "12hr": 12 * 3600000,
}

"""
    This is a simple function that displays a error message. 
    
    Parameters:
    - error_message: A string input that is used in top line of the error message
    - error_info: A string input that is used to give more detail on what the error is 
"""


def error(error_message, error_info):
    global errors
    # Set error to true
    errors = True
    # Display message box
    tk.messagebox.showerror("Error", f"{error_message}\n{error_info}")
    # Calling stop as some widgets may need to be updated
    stop()



"""
    This simply checks for errors when running or saving the program.
    
    It checks if all the directories that are used in the program are valid
    and if one or more of the directories are the same. It also checks if you have selected the same file type in the 
    instances of AppGrid instances. This is in order not to have collisions in the sorting.
    
    Returns:
    - drop_down_check: A dict containing the values in the dropdowns in the instances of AppGrid class
                       used to find what type of file to sort by
    - directory_check: This is another dict which holds all the directories hold in AppGrid instances 
    - directory_sort_from: Contains the value of the directory to sort from
"""


def error_checking():
    directory_sort_from = entry_var.get()

    # Check if directory_sort_from is a real directory
    if os.path.isdir(directory_sort_from) is False:
        return error(
            "Directory does not exist",
            f"The directory to sort to may not be valid: Directory - {directory_sort_from}",
        )

    # Check if the backup directory(Value in backup directory box) is a real directory
    if os.path.isdir(backup_directory_var.get()) is False:
        return error(
            "Backup directory does not exist",
            f"The backup directory may not be valid: Directory - {backup_directory_var.get()}",
        )

    # Dictionary to store iterations of contents in AppGrid instances
    drop_down_check = []
    directory_check = []

    # Check every instance in the AppGrid object
    for instance in AppGrid.instances:
        # Append the drop-down for later checking
        drop_down_check.append(instance.dropdown_var.get())

        # Check if that instance is an actual directory
        if os.path.isdir(instance.entry_var.get()):
            # Append directory in one instance of AppGrid instance if its real
            directory_check.append(instance.entry_var.get())

            are_directories_same = any(
                os.path.samefile(dir1, dir2)
                for dir1, dir2 in combinations(
                    [
                        backup_directory_var.get(),
                        entry_var.get(),
                        instance.entry_var.get(),
                    ],
                    2,
                )
            )
            # Check if two or more directories are the same in backup directory, directory from and the instance
            if are_directories_same:
                return error(
                    "Colliding Directories",
                    "Two or more directories for backing up, sorting from or to is the same.",
                )

        else:
            # Return error if one of instance directory is not real
            return error("Directory does not exist", "Error - Directory doesn't exist")

    if len(set(drop_down_check)) != len(drop_down_check):
        return error(
            "Error - Duplicate File Types",
            "Duplicate File Types - Can only sort one file type to one directory",
        )

    # Check if there is duplicate directories in instances by comparing length of a set to length of a list.
    # The list and set being the directories in AppGrid instances
    if len(set(directory_check)) != len(directory_check):
        return error("Error - Duplicate Directories", "Duplicate Directories")

    return drop_down_check, directory_check, directory_sort_from


"""
    This is used to load the categories of file types from a csv file.
    
    This is called in at the start of the program
    
    Parameters:
    - file_path: A string that holds file path of csv file
    
    Returns: 
    - category_file_types: Returns a dictionary holding the file type and there extensions 
    - None: Returns nothing if it cant read the file
    
    Raises:
        - Exception: If there is a error in reading the csv file. 
    
"""


def load_categories_from_csv(file_path):
    try:
        with open(file_path, "r") as csvfile:
            reader = csv.reader(csvfile)
            # Extract first element as keys and the later elements as values
            category_file_types_creation = {row[0]: row[1:] for row in reader if row}

    # Display error message if cant read
    except Exception as e:
        error("Error reading CSV file", str(e))
        return None

    # Returns the dict when loading the csv
    return category_file_types_creation


"""
    Used in the GUI implementation, this is used to deliver a window to select a directory and that value,
    gets stored in a text box.
    
    Parameters:
    - text_box_value: The value of what that textbox is
"""


def select_main_directory(text_box_value):
    # This is in order to preserve previous directory if someone clicks cancel
    previous_directory = text_box_value
    # Gives directory prompt
    directory = filedialog.askdirectory()
    # If directory is not empty just return
    if directory:
        return directory
    else:
        return previous_directory  # Used to preserve previous directory if closed of


"""
    This class is used to dynamically add places to add info on sorting from part of the program.
    
    It provides a + button to add instances and a close button to close it. There are also buttons to 
    add a directory to a input box or you can manually add things to input box yourself.
    
    Attributes:
    - self.directory_path: String that holds default directory path
    - self.appGrid: Create a frame based of the master which should be root
    - self.options: List that holds objects of category_file_types so file type can be in the dropdown menu
    - self.dropdown_var: Variable which holds the default value of self.options
    - self.dropdown_var.set: Sets the dropdown_var to a default value
    - self.dropdown_menu: Dropdown menu for file types
    - self.entry_var: Variable that holds a directory
    - self.entry: Entry box for the directory 
    - self.entry.grid: Grids the entry
    - self.exit_button: A button to close a new instance
    - self.exit_button.grid: Grids exit button in place
    - self.plus_button: A button to add a new instance
    - self.plus_button.grid: Grids plus button in place
    - self.all_widgets: List that holds all widgets so they can be disabled or enabled
    Methods 
    - __init__(self, master): Initializes an instance of AppGrid while also passing in the master
                              window
    - select_directory: Gives prompt to select directory when clicking on the directory button
    - close_button_click: Closes a instance of the AppClass when clicking on close button
    - grid: Wrapper for configuring grid layout 
    - create_new_instance: Creates a instance of AppClass when clicking on plus button 
    - disable_everything: Disables all widgets on AppClas when running the program in order not to mess with things
                          when running
    - enable_everything: Enables all widgets after the program stops running 
    
    
"""


class AppGrid:
    global category_file_types

    # A list, so we can loop through the instances if needed
    instances = []

    # Stores the number of instances so it can check
    numberOfInstance = 0

    def __init__(self, master):
        # Keeps track the number of instances
        AppGrid.numberOfInstance += 1

        # Append the instance to the list
        AppGrid.instances.append(self)

        # Default directory path is Enter directory
        self.directory_path = "Enter Directory"

        # Create a frame based of the master which should be root
        self.appGrid = ctk.CTkFrame(master)

        # Adjust weight of the text box in AppGrid
        self.appGrid.columnconfigure(1, weight=12)

        # We assign the options as the keys in the category_file_types dictionary
        self.options = list(category_file_types.keys())
        self.dropdown_var = ctk.StringVar(self.appGrid)

        # We set our starting values
        self.dropdown_var.set(self.options[0])

        # Dropdown menu for file types
        self.dropdown_menu = ctk.CTkComboBox(
            self.appGrid,
            variable=self.dropdown_var,
            width=150,
            values=self.options,
            state="readonly",
        )
        self.dropdown_menu.grid(row=0, column=0, pady=5, padx=1, sticky="ew")

        # Entry box for directory going to
        self.entry_var = ctk.StringVar(value=self.directory_path)
        self.entry = ctk.CTkEntry(
            self.appGrid, textvariable=self.entry_var, font=("Arial", 14)
        )
        self.entry.grid(row=0, column=1, pady=5, padx=1, sticky="ew")

        # Directory button to prompt select directory
        self.directory_button = ctk.CTkButton(
            self.appGrid,
            text="Directory",
            width=10,
            command=lambda: self.select_directory(entry_var.get()),
        )
        self.directory_button.grid(row=0, column=2, pady=5, padx=1, sticky="ew")

        # Exit button to close of an instance created
        self.exit_button = ctk.CTkButton(
            self.appGrid, text="Close", width=10, command=self.close_button_click
        )
        self.exit_button.grid(row=0, column=3, pady=5, padx=1, sticky="ew")

        # Plus button to create a new instance
        self.plus_button = ctk.CTkButton(
            self.appGrid, text="+", width=10, command=self.create_new_instance
        )
        self.plus_button.grid(row=0, column=4, pady=5, padx=1, sticky="ew")

        # Stores all the widgets, so it can be disabled when running
        self.all_widgets = [
            self.dropdown_menu,
            self.entry,
            self.directory_button,
            self.exit_button,
            self.plus_button,
        ]

    # It is the select directory function for the object
    def select_directory(self, variable=None):
        new_directory_path = filedialog.askdirectory()
        if new_directory_path:
            # If entry_var is provided, update its value
            if variable is not None:
                # If not we set it back to new_directory_path, so we do not get blank box
                self.entry_var.set(new_directory_path)

    # Closes an instance when clicking the close button
    def close_button_click(self):
        global num_plus_button_clicked
        # Conditional to make sure we cant close the last instance
        if AppGrid.numberOfInstance > 1:
            self.appGrid.destroy()
            AppGrid.numberOfInstance -= 1
            AppGrid.instances.remove(self)
        # If it is the last one, we pass and do nothing
        else:
            pass
        # Used to reset num_plus_button_clicked, so it can be used in create_new_instance again
        num_plus_button_clicked = AppGrid.numberOfInstance

    def grid(self, **kwargs):
        self.appGrid.grid(**kwargs)

    @staticmethod
    def create_new_instance():
        global num_plus_button_clicked
        # Increment num_plus_button_clicked
        num_plus_button_clicked += 1

        # Make sure we can only create up to 15 instances
        if len(AppGrid.instances) <= 15:
            new_instance = AppGrid(dir_to)
            new_instance.grid(sticky="ew", padx=25, pady=5)
        # If person attempts to add more when there are 15 instances, we provide an error message
        if num_plus_button_clicked > 16:
            error("Error", "No more than 15 directories to sort to ")

    def disable_everything(self):
        for widget in self.all_widgets:
            widget.configure(state="disabled")

    def enable_everything(self):
        for widget in self.all_widgets:
            # Combobox need to be read only to not change the dropdown while everything else should be normal
            if isinstance(widget, ctk.CTkComboBox):
                widget.configure(state="readonly")
            else:
                widget.configure(state="normal")


"""
    Loads instances from pickle file in order to retrieve instances when saved.
    
    Raises:
    - FileNotFoundError: When pickle is not found.
"""


def load_instances():
    global pickle_exists
    try:
        if os.path.exists(instances_file):
            pickle_exists = True

            # Read the pickle file
            with open(instances_file, "rb") as pickle_file:
                # Load the file
                instances_data = pickle.load(pickle_file)

                # Loop through the pickle file
                for data in instances_data:
                    new_instance = AppGrid(dir_to)
                    # Sets dropdown_var of the new instance to the stored value in the pickle file
                    new_instance.dropdown_var.set(data["dropdown_value"])
                    # Sets entry_var of the new instance to the stored value in the pickle file
                    new_instance.entry_var.set(data["entry_value"])
                    # We grid the instance and adjust the row to avoid overlap
                    new_instance.grid(
                        row=AppGrid.numberOfInstance, padx=25, sticky="ew"
                    )
    except (FileNotFoundError, EOFError):
        # If there is no pickle file or its empty, we just create a new one.
        with open(instances_file, "wb"):
            pass


"""'
    This function simply saves the dropdown and the entry box values in a pickle file. This is called on when saving 
    the file. 
    
    It uses a list that contains a dict. In this dict, the key and
    value pairs are the things we want to preserve. We then write it to the pickle file
"""


def save_all_instances_to_pickle():
    # List to hold the dict
    instances_data = []

    # Loop through the instances in appGrid instances
    for instance in AppGrid.instances:
        # Make a dict based of the values in the dropdown and the one in the entry box
        instance_data = {
            "dropdown_value": instance.dropdown_var.get(),
            "entry_value": instance.entry_var.get(),
        }
        # Append the dict to the list
        instances_data.append(instance_data)
    # Open up the pickle and write the list to it
    with open(instances_file, "wb") as pickle_file:
        pickle.dump(instances_data, pickle_file)


"""
    Used to save every instance in AppGrid and every text box in the program. It also shows that a save
    has been executed at the bottom of the program in the bottom box
    
    Parameters:
    - backup_directory_var: This is the variable that stores the backup directory in a entry box
"""


def save(directory_var):
    global Backup_Directory, errors
    errors = False
    # Before saving, check for errors
    error_checking()
    if errors:
        return

    # We preserve what is in AppGrid by calling save_all_instances_to_pickle
    save_all_instances_to_pickle()

    # Save text boxes and dropdowns (Not the ones in AppGrid) into configration file
    config["Settings"]["default_backup_directory"] = directory_var.get()
    config["Settings"]["directory_going_from"] = entry_var.get()
    config["Settings"]["backup_history"] = backup_saves_var.get()
    config["Settings"]["run_delay"] = interval_var.get()

    # Write the changes to the configuration file
    with open(config_file, 'w') as configfile:
        config.write(configfile)

    # Show the user that everything has been saved in bottom box of the GUI
    run_status_var.set("Saved")
    # After 5 seconds, we reset saved and keep it blank
    dir_to.after(5000, reset_save)


"""
    Resets the label at the bottom box of the GUI
"""


def reset_save():
    run_status_var.set("")


"""
    Used when clicking the stop button while running automatically. This sets running to false so when u try to run 
    again, it will not and will break the loop.
    
    It also turns the stop button back into a run button as the execution has stopped.
"""


def stop():
    global running
    running = False
    enable_on_run()
    run_button.configure(text="Run", command=run_with_delay)
    run_status_var.set("")


"""
    Shows the running status at the bottom box of the GUI
    
    It recursively adds dots to the running string to show that it is in operation.
"""


def show_running_status(count=0):
    global running
    if running:
        dots = "." * (count % 4 + 1)
        run_status_var.set(f"Running{dots}")
        dir_to.after(1000, show_running_status, count + 1)


"""
    Used for when automatically running, It calls running in background and calls other functions to set up to set up 
    the process of running
"""


def run_with_delay():
    global running
    running = True
    run_button.configure(text="Stop", command=stop)
    disable_on_run()
    show_running_status()
    run_in_background()


"""
    This is called when running the program either automatically or manually.
    
    This deletes old backups based on the date it was created and only keeps the amount specified in the backup history 
    text box.
    Raises:
    - Exception: This could happen when there is a error in the deletion of a zip file
"""


def delete_old_zips():
    try:
        backup_directory = backup_directory_var.get()

        print("Deleting old backup files...")
        # Find all the files in the backup directory
        backup_file_names = os.listdir(backup_directory)

        # Find the number of zip files in the backup directory
        num_backup_files = len([f for f in backup_file_names if f.endswith(".zip")])
        print(f"Number of backup files before deletion: {num_backup_files}")

        # Find how many saved backups we need to store
        backup_saves_value = backup_saves_dict[backup_saves_var.get()]
        print(f"Backup_saves_value: {backup_saves_value}")

        # Sort all the files by the time that they were created, oldest to newest
        sorted_files = sorted(
            os.scandir(backup_directory), key=lambda entry_: entry_.stat().st_ctime
        )

        # Determine the number of files to delete based on the values in the dictionary
        to_delete_count = max(num_backup_files - backup_saves_value, 0)
        print(f"To Delete Count: {to_delete_count}")

        # Will only delete if the number of files in the backup folder is greater than the amount of backups we need to
        # save
        if num_backup_files >= backup_saves_value:
            # Variable to store how many files we deleted
            deleted_count = 0
            for entry__ in sorted_files:
                # Make sure we only delete the zip files
                if entry__.name.endswith(".zip"):
                    print(
                        f"Deleting file: {entry__.name}, created at: {entry__.stat().st_ctime}"
                    )
                    os.remove(entry__.path)
                    deleted_count += 1

                    # Check if the required number of files have been deleted
                    if deleted_count > to_delete_count:
                        break

            # Find the updated number of backup files after deletion
            updated_num_backup_files = len(
                [f for f in os.listdir(backup_directory) if f.endswith(".zip")]
            )
            print(f"Number of backup files after deletion: {updated_num_backup_files}")

        print("Deletion complete.")

    except Exception as e:
        error("Error", f"An error occurred during backup deletion: {str(e)}")


"""
    Used to run the program only when the user clicks on it.
"""


def run_on_click():
    global running
    if not running:
        # Call running_implementation to actually run the program
        running_implemenation()
        if not errors:
            # Show that a run has been executed
            run_status_var.set("Run Executed")
            # Reset the run_status_var to improve clarity
            root.after(5000, reset_save)


"""
    This calls upon the running implementation and is what makes the program loop over and over again depending on what 
    the user put as there runtime delay
"""


def run_in_background():
    global make_backup, category_file_types
    # Start running the actual program
    running_implemenation()

    # Loop the program
    if running and interval_var.get() in intervals_dict.keys():
        delay = intervals_dict[interval_var.get()]
        dir_to.after(
            delay, run_in_background
        )  # Schedule the function to run again in 5000 milliseconds (5 seconds)
    else:
        run_button.configure(text="Auto Run", command=run_with_delay)
        run_status_var.set("")


"""
    This is the actual bulk of what the program does. 
    
    This function calls error checking and so does saving. It also calls the delete old zips every time it runs.
    However, this function is responsible for creating the backups, so the zip files to the backup directory and 
    is responsible for moving the file from the from directory to the to directories depending on file types.
    
    This function uses two dictionaries which is combined and category_file type in which they work in like a relational
    database with the primary key of combined liking to the foreign key of category_file_types where the values can be
    established 
    
    Raises:
    - Exception: This could happen when the program is unable to zip a file or move from directory from to to depending 
                 on type
"""


def running_implemenation():
    # Check for any errors in checking before running
    check_result = error_checking()

    # If error check doesn't return any values, and error has occurred and we should not run
    if check_result is None:
        return

    # Function is called to delete old backups
    delete_old_zips()

    # If we do have returned values, we use this in our running stage
    drop_down_check, directory_check, directory_sort_from = check_result

    try:
        # Checks if the directory going to is empty so that it move anything or produce a corrupted zip file
        if not [f for f in os.listdir(directory_sort_from) if not f.startswith(".")]:
            print("Empty")
        else:

            # Combine the two lists to the dropdown becomes the keys and directory check the values
            combined = dict(zip(drop_down_check, directory_check))

            # Find all the file names in directory we are sorting from
            file_names = os.listdir(entry_var.get())

            # Create a backup folder from the backup directory
            folder_name = f"backup_folder"
            folder_path = os.path.join(backup_directory_var.get(), folder_name)
            os.makedirs(folder_path, exist_ok=True)

            # Loop through all the files in the directory we are sorting from
            for file_name in file_names:
                if "." in file_name:
                    # Finds file type by including everything after the dot
                    file_type = file_name.split(".")[-1]
                    print(f"Filename in directories to {file_name} {file_type}")

                    for key in combined.keys():
                        if (
                                key in category_file_types.keys()
                                and file_type in category_file_types[key]
                        ):
                            source = os.path.join(directory_sort_from, file_name)
                            destination = os.path.join(combined[key], file_name)
                            print(f"Source: {source} Destination {destination}")

                            # Now we can move the file
                            shutil.move(source, destination)

                            if make_backup:
                                # We copy the file to the folder path in order for it to be zipped
                                shutil.copy2(destination, folder_path)
            if make_backup:
                # Find the current time
                current_time = datetime.now()

                # Format the time as hours and minutes
                formatted_time = current_time.strftime("%H_%M_%S")

                # Format another variable as day-month-year
                formatted_date = current_time.strftime("%d-%m-%Y")

                # Print the formatted time and date
                print("Formatted Time (HH_MM_SS):", formatted_time)
                print("Formatted Date (DD-MM-YYYY):", formatted_date)

                zip_folder_name = f"{formatted_date} {formatted_time}"
                zip_folder_path = os.path.join(backup_directory_var.get(), zip_folder_name)

                # Zip the entire backup_folder

                shutil.make_archive(zip_folder_path, "zip", folder_path)

                print("Backup made")

                # Remove the temporary backup_folder
                shutil.rmtree(folder_path)

    except Exception as e:
        error(
            f"An error occurred: {str(e)}",
            "There is a error in the running of the program",
        )


"""
    Disables widgets when you are running automatically in order to not change a directory when running or 
    click on the "Run On Click" button.
    
    This is to prevent accidental changes when running and prevent user errors.
"""


def disable_on_run():
    # Disable everything in object
    for instance in AppGrid.instances:
        instance.disable_everything()
    # Disable widgets in widgets_main declared in GUI implementation
    for widget in widgets_main:
        widget.configure(state="disabled")


"""
    Enables widgets after running in order for the user to modify it.
"""


def enable_on_run():
    # Loops through instances in the object calling instance.enable_everything method
    for instance in AppGrid.instances:
        instance.enable_everything()
    # Loops through the widgets in widgets_main that is declared in GUI implementation
    for widget in widgets_main:
        # Combobox must be read only as we do not want people to change contents of dropdown
        if isinstance(widget, ctk.CTkComboBox):
            widget.configure(state="readonly")
        else:
            # Enable everything else
            widget.configure(state="normal")

def check_if_backup():
    if backup_saves_var.get() == "No Backup - Not Recommended":
        selected_backup = False
    else:
        selected_backup = True
    return selected_backup

"""
    Implementation of gui and calling functions to start the program
"""

if __name__ == "__main__":
    global entry_var
    category_file_types = load_categories_from_csv("fileTypeAndExtensions.csv")

    root = ctk.CTk()
    root.geometry("1200x450")
    root.minsize(1200, 450)

    os_type = platform.system()

    # Change icon depending on what OS it is
    if os_type == "Windows":
        icon_path = "respos 3.ico"
        root.iconbitmap(default=icon_path)
    else:
        root.iconphoto(True, tk.PhotoImage(file="respos 3.png"))

    if category_file_types is None:
        sys.exit(1)

    root.title("Respos")
    ctk.set_appearance_mode("dark")

    dir_from_container = ctk.CTkFrame(root, fg_color="transparent")
    dir_from_container.grid(row=1, column=1, sticky="nsew")

    dir_from_container.columnconfigure(0, weight=1)
    dir_from_container.rowconfigure(0, weight=1)
    dir_from_container.rowconfigure(1, weight=100)

    dir_to = ctk.CTkScrollableFrame(dir_from_container, fg_color="#1c1b1b")
    dir_to.grid(row=1, column=0, sticky="nsew", padx=25, pady=10)

    dir_to.columnconfigure(0, weight=1)

    load_instances()

    root.columnconfigure(0, weight=2)
    root.columnconfigure(1, weight=50)
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1000)
    root.rowconfigure(3, weight=1)

    first_row_frame = ctk.CTkFrame(root, fg_color="#1c1b1b")
    first_row_frame.grid(row=0, column=0, sticky="nsew", padx=25, pady=10, columnspan=2)

    run_button_save = ctk.CTkButton(
        first_row_frame,
        text="Save",
        width=120,
        command=lambda: save(backup_directory_var),
    )
    run_button_save.grid(row=0, column=0, sticky="w", padx=(10, 5), pady=20)

    run_click_button = ctk.CTkButton(
        first_row_frame, text="Run on click", width=120, command=run_on_click
    )
    run_click_button.grid(row=0, column=1, padx=5, pady=20, sticky="w")

    run_button = ctk.CTkButton(
        first_row_frame, text="Auto Run", width=120, command=run_with_delay
    )
    run_button.grid(row=0, column=2, sticky="w", padx=5, pady=20)

    backup_settings_container = ctk.CTkFrame(root, fg_color="#1c1b1b")
    backup_settings_container.grid(row=1, column=0, sticky="nsew", padx=25, pady=10)

    backup_settings_container.columnconfigure(0, weight=1)

    label = ctk.CTkLabel(
        backup_settings_container, text="Enter Backup Directory", font=("Arial", 18)
    )
    label.grid(row=1, column=0, padx=25, pady=20, sticky="w")

    backup_directory_var = ctk.StringVar(value=Backup_Directory)
    directory_label = ctk.CTkEntry(
        backup_settings_container, textvariable=backup_directory_var
    )
    directory_label.grid(row=2, column=0, padx=(25, 10), sticky="ew", pady=10)

    directory_button_backup = ctk.CTkButton(
        backup_settings_container,
        text="Directory",
        width=20,
        command=lambda: backup_directory_var.set(
            select_main_directory(backup_directory_var.get())
        ),
    )
    directory_button_backup.grid(row=2, column=1, sticky="w", padx=(0, 25))

    backup = ctk.CTkLabel(
        backup_settings_container, text="Backup History", font=("Arial", 18)
    )
    backup.grid(row=3, column=0, padx=25, sticky="w")

    backup_saves_list = list(backup_saves_dict.keys())

    backup_saves_var = ctk.StringVar(value=backup_history)

    backup_saves_menu = ctk.CTkComboBox(
        backup_settings_container,
        variable=backup_saves_var,
        values=backup_saves_list,
        state="readonly",
    )
    backup_saves_menu.grid(row=4, column=0, pady=5, padx=25, sticky="w")

    backup = ctk.CTkLabel(
        backup_settings_container, text="Run Time Intervals", font=("Arial", 18)
    )
    backup.grid(row=5, column=0, padx=25, sticky="w")

    intervals_list = list(intervals_dict.keys())

    interval_var = tk.StringVar(value=run_delay)

    interval_menu = ctk.CTkComboBox(
        backup_settings_container,
        variable=interval_var,
        values=intervals_list,
        state="readonly",
    )
    interval_menu.grid(row=6, column=0, pady=5, padx=25, sticky="w")

    dir_from = ctk.CTkFrame(dir_from_container, fg_color="#1c1b1b")
    dir_from.grid(row=0, column=0, sticky="nsew", padx=25, pady=10)

    dir_from.columnconfigure(0, weight=1)

    label = ctk.CTkLabel(
        dir_from, text="Enter directory to sort from", font=("Arial", 18)
    )
    label.grid(row=0, column=0, pady=10, padx=25, sticky="w")

    entry_var = ctk.StringVar(value=default_directory_from)
    entry = ctk.CTkEntry(dir_from, textvariable=entry_var, font=("Arial", 14))
    entry.grid(row=1, column=0, padx=(25, 10), sticky="ew", pady=25)

    directory_button = ctk.CTkButton(
        dir_from,
        text="Directory",
        width=20,
        command=lambda: entry_var.set(select_main_directory(entry_var.get())),
    )
    directory_button.grid(row=1, column=1, sticky="w", padx=(0, 25))

    labeltwo = ctk.CTkLabel(
        dir_to, text="Enter directory and file type to sort to", font=("Arial", 18)
    )
    labeltwo.grid(row=0, column=0, padx=25, pady=20, sticky="w")

    if not pickle_exists:
        toSort = AppGrid(dir_to)
        toSort.grid(row=1, column=0, sticky="ew", padx=25, pady=5)

    last_frame = ctk.CTkFrame(root, fg_color="#1c1b1b")
    last_frame.grid(row=3, column=0, sticky="nsew", padx=25, pady=10, columnspan=2)

    run_status_var = ctk.StringVar(value="")
    run_status = ctk.CTkLabel(
        last_frame, textvariable=run_status_var, font=("Arial", 20)
    )
    run_status.grid(row=0, column=0, sticky="w", padx=10, pady=10)

    widgets_main = [
        directory_label,
        directory_button_backup,
        directory_button,
        backup_saves_menu,
        interval_menu,
        run_click_button,
        entry,
    ]

    root.mainloop()
