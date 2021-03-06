import os
import time
import json
import utility_functions as UF


def cd_into_drive():
    """
    Will change the current directory into the directory where the files that will be sorted are.
    """
    project_location = os.getcwd()
    directory_layers = len(project_location.split("/"))
    command_parts = ["../"]
    for i in range(directory_layers):
         command_parts.append("../")
    path = "".join(command_parts)
    os.chdir(path)
    if "Volumes" in os.listdir():
        os.chdir("Volumes")
        while True:
            UF.clear_output(50)
            print("-------------------------------------------------------")
            drive_numbers = 0
            for drive in os.listdir():
                drive_numbers += 1
                print("Drive {drive_nums}: {item}".format(drive_nums=drive_numbers, item=drive))
            print("")
            drive_name = input("What is the drive that you wanna use?\n")
            if drive_name in os.listdir():
                os.chdir(drive_name)
                UF.print_colored("The program is now set to this drive:" + str(os.getcwd()), "green")
                break
            else:
                UF.print_colored("That is not a valid drive. The program will restart in 5 seconds", "red")
                time.sleep(5)
                continue


# Testing:
# cd_into_drive()


def pre_import_file_types():
    """
    Will get the file types from the supported_file_types.json file
    :return: array of file types.
    """
    with open("supported_file_types.json") as json_file:
        file_types = json.load(json_file)
    return file_types


# Testing
# print(pre_import_file_types())


def new_file_path(photo_date):
    """
    Get the new file path for the photo. An example would be 2019/January/31st
    :param photo_date: The list for the date that is supplied from the exif data
    :return: Array of all the new file paths
    """
    if len(photo_date) == 3:
        month = photo_date[0]
        day = int(photo_date[1])
        year = int(photo_date[2])
        if day in (1, 21, 31):
            new_day = str(day) + "st"
        elif day in (2, 22):
            new_day = str(day) + "nd"
        elif day == 23:
            new_day = str(day) + "rd"
        else:
            new_day = str(day) + "th"
        final_string = "./" + str(year) + "/" + str(month) + "/" + str(month) + "-" + str(new_day)
        return final_string


# Testing
# print(new_file_path(["August",  22, 2019]))


def init_folders(raw_exif_data):
    """
    Will create all the folders in the current directory
    :param raw_exif_data: the raw exif data for all the photos.
    :return: folders that were created
    """
    folders = []
    for photo in raw_exif_data:
        photo_folder = photo["New Path"]
        if photo_folder not in folders:
            folders.append(photo_folder)
    for folder_path in folders:
        UF.run_command(["mkdir", "-p", folder_path], False)
    UF.run_command(["mkdir", "Duplicates"], False)
    return folders


def rename_file(file_path, number):
    """
    Will create the string to rename a file to ./currentname_copy.file extension
    :param file_path: the current file path
    :param number: the number that will be added to the end of _COPY
    :return: new path, new_name
    """
    characters = list(file_path)
    dot_index = ''.join(characters).rindex('.')  # Find the last instance of a dot
    last_slash_index = ''.join(characters).rindex('/')
    name_section = characters[last_slash_index:dot_index]
    current_name = "".join(name_section)
    new_name = current_name + "_COPY" + str(number)
    before_name = "".join(characters[0:last_slash_index])
    after_name = "".join(characters[dot_index:len(characters)])
    new_path = before_name + new_name + after_name
    return [new_path, new_name]


# Testing:
# print(rename_file("/Users/matthewgleich/Documents/GitHub/Get_Tempature/.idea/Get_Tempature.iml"))


def put_photos_in_folders(raw_exif_data):
    """
    Will take all the photos and put them in their folders
    :param raw_exif_data: the raw exif data
    :return: number of duplicates in put in folder
    """
    move_files = {}
    duplicate_file_paths = []  # list of their current paths
    duplicate_file_names = []  # list of their current names
    for file in raw_exif_data:
        file_name = file["File Name"]
        current_path = file["Current Path"]
        new_path = file["New Path"]
        if file_name in duplicate_file_names:
            copies = 0
            while True:
                copies += 1
                rename_file_command = rename_file(current_path, copies)
                new_name = rename_file_command[1]
                new_path = rename_file_command[0]
                if new_name in duplicate_file_names or new_path in duplicate_file_paths:
                    continue
                else:
                    duplicate_file_paths.append(new_path)
                    duplicate_file_names.append(new_name)
                    UF.run_command(["mv", current_path, new_path], False)
                    break
        elif file_name not in move_files.keys():
            move_files[file_name] = [current_path, new_path]
        elif file_name in move_files.keys():
            duplicate_file_paths.append(current_path)
            duplicate_file_names.append(file_name)
            duplicate_file_orig_path = move_files[file_name][0]
            rename_file_command = rename_file(duplicate_file_orig_path, 0)
            UF.run_command(["mv", duplicate_file_orig_path, rename_file_command[0]], False)
            move_files.pop(file_name)
            duplicate_file_paths.append(rename_file_command[0])
            duplicate_file_names.append(rename_file_command[1])
    for name, paths in move_files.items():
        current_path = paths[0]
        new_path = paths[1]
        UF.run_command(["mv", current_path, new_path], False)
    if len(duplicate_file_paths) >= 2:
        for path in duplicate_file_paths:
            UF.run_command(["mv", path, "./Duplicates"], False)
    else:
        UF.run_command(["rm", "-r", "Duplicates"], False)
    return int(len(duplicate_file_paths) / 2)


def cd_into_folder(go_to_root):
    """
    Will list the folders in the current directory and cd into the one that user chooses.
    :param go_to_root: If the program should cd up to the root (boolean)
    :return: current directory
    """
    if go_to_root:
        current_pwd = os.getcwd()
        levels = current_pwd.split("/")
        levels.pop(0)  # Removes blank space that is right before users.
        number_of_levels = len(levels) - 2  # Minus 2 because we wanna be a user root not system root.
        for i in range(number_of_levels):
            os.chdir("..")
    while True:
        UF.clear_output(50)
        command_output = os.popen("echo */").read()  # Won't work with subprocess for some strange reason
        raw_directories = command_output.split("/")
        directories = []
        current_directory = os.getcwd()
        print("The current path is:", current_directory)
        for directory in raw_directories:
            cleaned_directory = directory.strip()
            directories.append(cleaned_directory)
        for directory in directories:
            print(directory)
        folder = input("Please choose one of the folders above. If the current folder is the folder that you wanna sort, the please type *\n")
        if folder == "*":
            UF.print_colored("The folder the program will run in is now set to" + folder, "green")
            break
        elif folder in directories:
            os.chdir(folder)
            continue
        elif folder == "*":
            UF.print_colored("The folder the program will run in is now set to" + folder, "green")
            break
        else:
            print("That is not one of the folders shown above.")
            continue
    UF.clear_output(10)
    return os.getcwd()


def setup_duplicates_folder():
    """
    Will setup the duplicates folder. It needs to already exist though.
    :return: none
    """
    UF.run_command(["mkdir", "./Duplicates/Keep"], False)
    UF.run_command(["mkdir", "./Duplicates/Remove"], False)
    instructions = \
    "In this folder are all the duplicate files. When looking through the files, and you find the one that you wanna keep, just drag it into the folder called Keep. For all the ones that you would like to discard of, put them a folder called Remove. Once you have at least one file in the Keep folder, you can restart the program and use the move duplicates command and it will move all the files in the Keep folder to their correct folders. You can repeat this process as many times as you like. Also, when you are putting the files in the keep folder, you don't need to remove the _COPY extension, the program will do that automattically when they get moved into their folders."
    with open("./Duplicates/instructions.txt", "w") as instructions_file:
        instructions_file.write(instructions)
    UF.print_colored("Go into the Duplicates folder and read the instructions.txt file to know what to do with the duplicates.", "yellow")


def duplicates_folder_management(keep):
    """
    Moves the files in the Keep folder and removes the the files in the Remove Folder
    :param keep: either Remove or Keep (answer with boolean)
    :return: none
    """
    while True:
        if keep:
            try:
                orig_file_names = os.listdir("./Duplicates/Keep")
            except FileNotFoundError:
                raise Exception("It seems as though the program has not been ran here before here. This is due to the fact that there is no folder called Duplicates/Keep.")
            fixed_file_names = {}
            for file in orig_file_names:
                if "_COPY" in file:
                    characters = list(file)
                    _COPY_index = "".join(characters).rindex("_COPY")
                    dot_index = "".join(characters).rindex(".")
                    file_extension = "".join(characters[dot_index:len(characters)])
                    file_name = "".join(characters[0:_COPY_index])
                    new_name = file_name + file_extension
                    if new_name in fixed_file_names:
                        copies = 0
                        while True:
                            copies += 1
                            fixed_new_name = file_name + "_" + str(copies) + file_extension
                            if fixed_new_name in fixed_file_names:
                                continue
                            else:
                                fixed_file_names[file] = fixed_new_name
                    else:
                        fixed_file_names[file] = new_name
            for orig_name in fixed_file_names.keys():
                for new_name in fixed_file_names.values():
                    orig_path = "Duplicates/Keep/" + orig_name
                    new_path = "Duplicates/Keep/" + new_name
                    UF.run_command(["mv", orig_path, new_path], False)
                    move_path = new_file_path(UF.file_creation_date(new_path))
                    UF.run_command(["mv", new_path, move_path], False)
            num_of_files = len(fixed_file_names.values())
            UF.print_colored("Moved " + str(num_of_files) + " files to their proper folders", "green")
            break
        else:
            folder_name = "Remove"
            orig_file_names = os.listdir("./Duplicates/" + folder_name)
            if len(orig_file_names) == 0:
                UF.print_colored(
                    "There are no files in the " + folder_name + " folder. Once files are in there, please restart the program and run this command again.", "red")
                break
            for file in orig_file_names:
                path = "Duplicates/" + folder_name + "/" + file
                UF.run_command(["rm" ,path], False)
            UF.print_colored("Removed " + str(len(orig_file_names)) + " files in the Remove folder", "green")
            break
