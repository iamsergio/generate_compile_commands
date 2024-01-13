# SPDX-FileCopyrightText: 2024 Klarälvdalens Datakonsult AB, a KDAB Group company <info@kdab.com>
# SPDX-License-Identifier: MIT

import os
import json
import sys

# Returns the list of all files with .cpp extension inside path
# does it recursively
def list_cpp_files_recursively(path):
    cpp_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".cpp"):
                cpp_files.append(os.path.join(root, file))
    return cpp_files
    

# Removes files we don't care about. For example, the ones starting with "moc_"
# Returns the filtered list
def filter_out_cruft(cpp_files):
    filtered_files = []
    for file in cpp_files:
        filename = os.path.basename(file)
        if not filename.startswith("moc_") and not filename.startswith("qrc_") and filename not in ["mocs_compilation.cpp"] and "CMakeFiles" not in file:
            filtered_files.append(file)
    return filtered_files
    
def generate_command(cpp_file, config):
    result = []
    result.append(config["compiler"])
    result.extend(config["defines"])
    result.extend(config["includes"])
    result.append(config["flags"])
    # result.extend(["-o", cpp_file + ".unused"])
    result.extend(["-c", cpp_file])

    return " ".join(result)

def generate_compile_commands(cpp_files, config, folder_path):
    result = []
    for cpp_file in cpp_files:
        entry = {}
        entry["directory"] = folder_path
        entry["command"] = generate_command(cpp_file, config)
        entry["file"] = cpp_file
        entry["output"] = cpp_file + ".unused"
        result.append(entry)

    return result

# loads a json filename with config and returns it
def load_config(config_filename):
    with open(config_filename, 'r') as file:
        config = json.load(file)
    return config

# saves the json to file
def save_commands_to_file(filename, commands):
    with open(filename, 'w') as file:
        json.dump(commands, file, indent=4)


if len(sys.argv) != 2:
    print("Usage: generate_compile_commands.py <config.json>")
    exit(-1)

config_filename = sys.argv[1]
config = load_config(config_filename)
folder_path = os.path.abspath(os.path.dirname(config_filename))
commands = generate_compile_commands(filter_out_cruft(list_cpp_files_recursively(folder_path)), config, folder_path)
save_commands_to_file(folder_path + "/compile_commands.json", commands)
