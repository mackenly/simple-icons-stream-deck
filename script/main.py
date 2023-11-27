# Filename: main.py
# Created By: Mackenly Jones on 07/07/2022
# Web: mackenly.com
# Twitter: @mackenlyjones

import os
import json
import shutil
import subprocess
import sys
from tkinter import Tk
from tkinter.filedialog import askdirectory
from tqdm import tqdm

not_allowed_chars = {
    "+": "plus",
    "-": "",
    ".": "dot",
    "'": "",
    "!": "",
    "&": "and",
    "_": "",
    "/": "",
    ":": "",
    "°": "",
    " ": "",
    "đ": 'd',
    "ã": 'a',
    "é": 'e',
    "ë": 'e',
    "É": 'e',
    "ü": 'u',
    "Š": 's',
    "ħ": 'h',
    "ı": 'i',
    "ĸ": 'k',
    "ŀ": 'l',
    "ł": 'l',
    "ß": 'ss',
    "ŧ": 't',
}

slugOverrides = {
    "Sat.1": "sat1",
    "Warner Bros.": "warnerbros",
    "Ferrari N.V.": "ferrarinv",
    "del.icio.us": "delicious",
    "Dassault Systèmes": "dassaultsystemes",
}

# If at least one cli parameter is set, use that as the directory
if len(sys.argv) > 1:
    directory = sys.argv[1]
    # get the current working directory
    cwd = os.getcwd()
    # check to see if the directory is relative or absolute
    if directory[0] == ".":
        directory = cwd + directory[1:]
    # check to see if the directory is a file or a folder
    if os.path.isfile(directory):
        print("Error: " + directory + " is a file, not a directory.")
        sys.exit("File input error.")
    elif not os.path.isdir(directory):
        print("Error: " + directory + " is not a valid directory.")
        sys.exit("File input error.")
    else:
        print("Selected directory: " + directory)
else:
    # Hide the GUI
    Tk().withdraw()

    # Get the directory
    directory = askdirectory()
    print("Selected directory: " + directory)

# Extract the directories we want to use
object = os.scandir(directory)
data_path = ""
icons_path = ""
for i in object:
    if i.name == "_data":
        data_path = i.path
    elif i.name == "icons":
        icons_path = i.path

# remove the old files
try:
    shutil.rmtree(os.getcwd().replace("\\script", "\\out"))
    print("Removed old files.")
except FileNotFoundError:
    print("No old files to remove, continuing...")
except PermissionError:
    print("Permission error, continuing...")

# create directories
os.mkdir(os.getcwd().replace("\\script", "\\out"))
os.mkdir(os.getcwd().replace("\\script", "\\out\\com.mackenly.simpleiconsstreamdeck.sdIconPack"))
os.mkdir(os.getcwd().replace("\\script", "\\out\\com.mackenly.simpleiconsstreamdeck.sdIconPack\\icons"))
print("Created directories.")

# copy the license from the license template
license_template = os.getcwd().replace("\\script", "") + "\\template\\license.txt"
license_out = os.getcwd().replace("\\script", "") + "\\out\\com.mackenly.simpleiconsstreamdeck.sdIconPack\\license.txt"
shutil.copy(license_template, license_out)

# append icon title and source to the license
with open(license_out, "a") as license_file:
    license_file.write("\n\nSources for the icons used in this project:\n")
print("Generated license.")

# copy in preview images from the assets folder
preview_template = os.getcwd().replace("\\script", "") + "\\assets\\previews"
preview_out = os.getcwd().replace("\\script", "") + "\\out\\com.mackenly.simpleiconsstreamdeck.sdIconPack\\previews"
shutil.copytree(preview_template, preview_out)
print("Copied preview images.")

# copy the manifest from the manifest template
manifest_template = os.getcwd().replace("\\script", "") + "\\template\\manifest.json"
manifest_out = os.getcwd().replace("\\script", "") + "\\out\\com.mackenly.simpleiconsstreamdeck.sdIconPack\\manifest.json"
shutil.copy(manifest_template, manifest_out)
print("Copied manifest.")

# if two parameters are passed, use the second as the version. Otherwise, use the template version as is
if len(sys.argv) > 2:
    # edit the manifest with the correct version
    with open(manifest_out, "r") as manifest_file:
        manifest_file_data = manifest_file.read()
        # Get the template version from the manifest which looks like this: "Version": "1.0.0"
        template_version = manifest_file_data.split("\"Version\": \"")[1].split("\"")[0]
        # Replace the current version with the new version
        manifest_file_data = manifest_file_data.replace(template_version, sys.argv[2])
        with open(manifest_out, "w") as manifest_out_file:
            manifest_out_file.write(manifest_file_data)
    print("Updated manifest version to " + sys.argv[2])

# copy the icon from the icon template
icon_template = os.getcwd().replace("\\script", "") + "\\template\\icon.svg"
icon_out = os.getcwd().replace("\\script", "") + "\\out\\com.mackenly.simpleiconsstreamdeck.sdIconPack\\icon.svg"
shutil.copy(icon_template, icon_out)
print("Copied icon.")

# import the json data
with open(data_path + "\\simple-icons.json", encoding="utf8") as json_file:
    data = json.load(json_file)
    data = data["icons"]
    # create the json file
    out_data = []
    for i in tqdm (data,
               desc="Generating output…",
               ascii=False, ncols=75):
        # check to see if title contains characters that are in the not allowed list
        normalized_title = ""

        # check to see if title is in the slugOverrides list, if so use that
        if i["title"] in slugOverrides:
            normalized_title = slugOverrides[i["title"]].lower()
        else:
            for j in i["title"]:
                if j in not_allowed_chars:
                    normalized_title += not_allowed_chars[j].lower()
                else:
                    normalized_title += j.lower()

        try:
            # copy icon to the icons folder
            new_path = os.getcwd().replace("\\script", "") + "\\out\\com.mackenly.simpleiconsstreamdeck.sdIconPack\\icons\\" + normalized_title + ".svg"
            old_path = icons_path + "\\" + normalized_title + ".svg"
            shutil.copy(old_path, new_path)
        except FileNotFoundError:
            # skip if icon doesn't exist
            print("Icon not found for " + i["title"])
            continue

        # add the icon to the out data
        out_data.append({
            "path": normalized_title + ".svg",
            "name": i["title"],
            "tags": [
                i["title"],
                "logo"
            ]
        })

        # edit the icon with the correct color
        with open(os.getcwd().replace("\\script", "") + "\\out\\com.mackenly.simpleiconsstreamdeck.sdIconPack\\icons\\" + normalized_title + ".svg", "r") as icon_file:
            icon_data = icon_file.read()
            icon_data = icon_data.replace("<svg fill=\"#FF0000\" role=\"img\" viewBox=\"0 0 24 24\" xmlns=\"http://www.w3.org/2000/svg\">", "<svg fill=\"#" + i["hex"] + "\" role=\"img\" viewBox=\"0 0 24 24\" xmlns=\"http://www.w3.org/2000/svg\"  style=\"position:relative;height:576px;width:576px;\">")
            icon_data = icon_data.replace("<svg ", "<svg fill=\"#" + i["hex"] + "\" ")
            with open(os.getcwd().replace("\\script", "") + "\\out\\com.mackenly.simpleiconsstreamdeck.sdIconPack\\icons\\" + normalized_title + ".svg", "w") as icon_out:
                icon_out.write(icon_data)

        # append icon title and source to the license
        with open(license_out, "a") as license_file:
            license_file.write("\n\n" + i["title"] + "\n" + i["source"])

    # write the json file
    with open(os.getcwd().replace("\\script", "") + "\\out\\com.mackenly.simpleiconsstreamdeck.sdIconPack\\icons.json", "w") as out_file:
        json.dump(out_data, out_file)


# start the distribution tools
output = subprocess.getstatusoutput(f'.\DistributionTool.exe -b -i ..\out\com.mackenly.simpleiconsstreamdeck.sdIconPack -o ..\out')
shutil.rmtree(os.getcwd().replace("\\script", "\\out\\com.mackenly.simpleiconsstreamdeck.sdIconPack"))

if output[0] == 0:
    print("Done!")
else:
    print("Error!")
    print(output[1])
    sys.exit("Error generating icon file.")
