try:
    from PIL import Image
except ImportError:
    import Image
import re
import pytesseract
import cv2
from pytesseract import Output
from image_processing import *
from os import listdir
from os.path import isfile, join, isdir
from matplotlib import pyplot as plt
from scipy import ndimage
import numpy as np
import argparse
import os
import platform
import pathlib
import requests

# Global variables
custom_config = r''
online = False
isbn_found = 0
file_found = 0

# PLT variables
plt.figure(figsize=(16,12))

def find_isbn(data):
    regex_pattern = r'(ISBN[-:]*(1[03])*[ ]*(: ){0,1})*(([0-9Xx][- \'"]*){13}|([0-9Xx][- \'"]*){10})'
    # regex_pattern = r'/((978[\--– ])?[0-9][0-9\--– ]{10}[\--– ][0-9xX])|((978)?[0-9]{9}[0-9Xx])/'
    x = re.search(regex_pattern, data)

    if x:
        data = re.sub('[ISBN^(: )]+', '', x.group())
        removed_dash = data.replace('-', '')
        return removed_dash
    else:
        None

def check_isbn(isbn):
    # Using abebooks to do a search on the isbn
    # This only works when there is internet
    url = 'https://www.abebooks.com/servlet/SearchResults?isbn=' + isbn
    print(url)
    resp = requests.get(url)
    found_isbn = False

    if url == resp.url:
        found_isbn = True

    return found_isbn

# def clean_data(data):
#     # Removed whitespaces and non-alpha-numeric characters (except new lines)
#     removed_other_char = re.sub('[\W_](?<!\n)+', '', data)
#     return result 

# Converting images to a different image format
def convert_image_format(file, folder=None, dpi=(600,600), extension='.tiff'):
    base = os.path.basename(file)
    split_text = os.path.splitext(base)
    filename = split_text[0] + extension
    im = Image.open(file)
    if folder:
        folder_path = str(pathlib.Path(folder).absolute())
        if platform == 'Windows':
            filename = folder_path + '\\' + filename
        else:
            filename = folder_path + '/' + filename
        im.save(filename, dpi=dpi)
    else:
        im.save(filename, dpi=dpi)
    
    return os.path.abspath(filename)

def create_local_temp_folder(folder=None):
    # Create folder to store temp files
    # Store temp files in them
    if not folder:
        folder = "temp"

    if not os.path.exists(folder):
        os.makedirs(folder)

def scan_image(file):
    global custom_config
    global online

    print('-----------------------------------------')
    print('TESSERACT OUTPUT --> ' + file)
    print('-----------------------------------------')

    base = os.path.basename(file)

    # Checks if the image is tiff, if not convert to tiff temp file
    # .tiff files provide better results for tessseract
    if os.path.splitext(base)[1] != '.tiff':
        create_local_temp_folder()
        file = convert_image_format(file=file, folder='temp')

    image = cv2.imread(file)
    image = cv2.resize(image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    angle_list = [90, 180, 270, 360]
    try:

        # Cleaning up image before rotation
        gray = get_grayscale(image)
        # thresh_image = adaptiveThreshold(gray)
        # noise_removed = remove_noise(thresh_image)
        # plt.imshow(noise_removed, cmap='gray')
        # plt.show()

        for index, angle in enumerate(angle_list):
            rotate_image = rotate(image=gray, rotate_angle=angle)
            data = pytesseract.image_to_string(rotate_image, config=custom_config)
            isbn_value = find_isbn(data)
            global isbn_found

            if isbn_value:
                # If you want to confirm that the isbn is found online
                print(isbn_value)
                if online:
                    isbn_check = check_isbn(isbn_value)
                    if isbn_check:
                        isbn_found+=1
                        break
                else:
                    isbn_found+=1
                    break
    except Exception as e:
        print("image: " + file + " Error: " + str(e))

    print('-----------------------------------------')


def main():
    global file_found
    global isbn_found
    global custom_config
    global online

    is_file = False

    parser = argparse.ArgumentParser(description='Book ISBN image scanner')
    parser.add_argument('-p', '--path', help='File or Folder Path', required=True)
    parser.add_argument('-c', '--config', help='Tesseract config commands (ex. --oem 3)', required=False)
    parser.add_argument('-o', '--online', help='Allow the scanner to check isbns online', action='store_true', required=False)
    
    args = vars(parser.parse_args())
    path = args['path']
    custom_config = args['config'] if args['config'] else custom_config

    if isdir(path):  
        is_file = False
    elif isfile(path):
        is_file = True
    else:
        raise Exception('Unable to determine file or directory')
    
    if args['online']:
        online = True
    
    if is_file:
        scan_image(path)
        file_found+=1
    else:
        for files in listdir(path):
            scan_image(path + files)
            file_found+=1
    
    print("Total files: " + str(file_found))
    print("Total ISBN to Files: " + str(isbn_found) + "/" + str(file_found))

if __name__ == "__main__":
    main()