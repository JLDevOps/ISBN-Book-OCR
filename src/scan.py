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
import csv
import time
from isbn import *

# Global variables
custom_config = r''
online = False
isbn_found = 0
file_found = 0

# PLT variables
plt.figure(figsize=(16,12))

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


def create_csv(output_filename='output.csv', data_list=None):
    # Create a csv with the ISBN and Image OCR results
    header = ['Image Name', 'Rotation', 'ISBN Number', 'Raw Data', 'Found Online', 'URL']
    with open(output_filename, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(header)
    csv_file.close()


def scan_image(file=None, csv=None):
    global custom_config
    global online
    global isbn_found

    isbn_check = False
    row_list = []
    isbn_value = None
    found_angle = None
    raw_data = None

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
        url = None
        # Cleaning up image before rotation
        gray = get_grayscale(image)
        # thresh_image = adaptiveThreshold(gray)
        # noise_removed = remove_noise(thresh_image)

        for index, angle in enumerate(angle_list):
            print('angle is: ' + str(angle))
            rotate_image = rotate(image=gray, rotate_angle=angle)
            raw_data = pytesseract.image_to_string(rotate_image, config=custom_config)
            isbn_value = find_isbn(raw_data)

            if isbn_value:
                # If you want to confirm that the isbn is found online
                print(isbn_value)
                if online:
                    isbn_check, url = check_isbn(isbn_value)

                if(isbn_check):
                    isbn_found+=1
                    found_angle = angle
                    break

        row_list = [str(file), str(found_angle if found_angle else None), str(isbn_value), str(raw_data), str(isbn_check), str(url)]
        print(row_list)
        return row_list
    except Exception as e:
        print("image: " + file + " Error: " + str(e))


def main():
    global file_found
    global isbn_found
    global custom_config
    global online
    global scan_list

    is_file = False

    parser = argparse.ArgumentParser(description='Book ISBN image scanner')
    parser.add_argument('-p', '--path', help='File or Folder Path', required=True)
    parser.add_argument('-c', '--config', help='Tesseract config commands (ex. --oem 3)', required=False)
    parser.add_argument('-o', '--online', help='Allow the scanner to check isbns online', action='store_true', required=False)
    parser.add_argument('-x', '--csv', help='Exports a csv file from the results', required=False)

    args = vars(parser.parse_args())
    path = args['path']
    custom_config = args['config'] if args['config'] else custom_config
    csv_name = args['csv'] if args['csv'] else None

    if isdir(path):  
        is_file = False
    elif isfile(path):
        is_file = True
    else:
        raise Exception('Unable to determine file or directory')
    
    if args['online']:
        online = True
    
    start_time = time.perf_counter()

    if csv_name: 
        create_csv(output_filename=csv_name)
        
        with open(csv_name, 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            
            if is_file:
                csv_writer.writerow(scan_image(path))
                csv_file.flush()
                file_found+=1
            else:
                for files in listdir(path):
                    csv_writer.writerow(scan_image(path + files))
                    csv_file.flush()
                    file_found+=1
        
        csv_file.close()

    end_time = time.perf_counter()

    print("Total files: " + str(file_found))
    print("Total ISBN to Files: " + str(isbn_found) + "/" + str(file_found))
    print(f"Total time: {end_time - start_time:0.4f} seconds")


if __name__ == "__main__":
    main()