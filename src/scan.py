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


# Global variables
custom_config = r'-l eng --oem 3 --psm 6'

# PLT variables
plt.figure(figsize=(16,12))

def find_isbn(data):
    regex_pattern = '(ISBN[-]*(1[03])*[ ]*(: ){0,1})*(([0-9Xx][- ]*){13}|([0-9Xx][- ]*){10})'
    x = re.search(regex_pattern, data)
    print(x)
    print(x.group())
    return x.group()

def scan_image(file):
    print('-----------------------------------------')
    print('TESSERACT OUTPUT -->' + file)
    print('-----------------------------------------')

    image = cv2.imread(file)
    try:
        newdata= pytesseract.image_to_osd(image)

        rotation = re.search('(?<=Rotate: )\\d+', newdata).group(0)
        print(file + " rotation: " + rotation)

        if int(rotation) == 0 or int(rotation) == 180:
            noise_removed = remove_noise(image)
            gray = get_grayscale(image)
        else:
            rotated_image = rotate(image)
            # rotated_image = ndimage.rotate(image, float(rotation) * -1)
            noise_removed = remove_noise(rotated_image)
            newdata= pytesseract.image_to_osd(rotated_image)
            rotation = re.search('(?<=Rotate: )\\d+', newdata).group(0)
            print(file + " rotation: " + rotation)
            gray = get_grayscale(rotated_image)

        # gray = get_grayscale(image)
        thresh_image = thresholding(gray)
        # thresh_image = adaptiveThreshold(gray)
        # plt.imshow(thresh_image, cmap='gray')
        # plt.show()
        data = pytesseract.image_to_string(thresh_image, config=custom_config)
        print(data)
        find_isbn(data)
    except Exception as e:
        print("image: " + file + " Error: " + str(e))
    print('-----------------------------------------')


def main():
    parser = argparse.ArgumentParser(description='Book ISBN image scanner')
    parser.add_argument('-p', '--path', help='File or Folder Path', required=True)
    
    args = vars(parser.parse_args())
    path = args['path']
    is_file = False

    if isdir(path):  
        is_file = False
    elif isfile(path):
        is_file = True

    if (is_file):
        scan_image(path)
    else:
        for files in listdir(path):
            scan_image(path + files)

if __name__ == "__main__":
    main()