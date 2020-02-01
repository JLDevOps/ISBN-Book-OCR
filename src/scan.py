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

# Global variables
custom_config = r''
isbn_found = 0
file_found = 0

# PLT variables
plt.figure(figsize=(16,12))

def find_isbn(data):
    regex_pattern = r'(ISBN[-]*(1[03])*[ ]*(: ){0,1})*(([0-9Xx][- \'"]*){13}|([0-9Xx][- \'"]*){10})'
    x = re.search(regex_pattern, data)
    global isbn_found
    isbn_found+=1
    return x.group() if x else None

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
    angle_list = [0, 90, 180, 270]
    try:
        # Cleaning up image before rotation
        gray = get_grayscale(image)
        thresh_image = adaptiveThreshold(gray)
        noise_removed = remove_noise(thresh_image)
        plt.imshow(noise_removed, cmap='gray')
        plt.show()

        for index, angle in enumerate(angle_list):
            rotate_image = rotate(image=noise_removed, rotate_angle=angle)

            isbn_value = find_isbn(pytesseract.image_to_string(rotate_image, config=custom_config))
            print(isbn_value)
            if isbn_value:
                break
    except Exception as e:
        print("image: " + file + " Error: " + str(e))

    print('-----------------------------------------')


def main():
    global file_found
    global isbn_found
    global custom_config

    is_file = False

    parser = argparse.ArgumentParser(description='Book ISBN image scanner')
    parser.add_argument('-p', '--path', help='File or Folder Path', required=True)
    parser.add_argument('-c', '--config', help='Tesseract config commands (ex. --oem 3)', required=False)
    
    args = vars(parser.parse_args())
    path = args['path']
    custom_config = args['config'] if args['config'] else custom_config

    if isdir(path):  
        is_file = False
    elif isfile(path):
        is_file = True
    
    if (is_file):
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