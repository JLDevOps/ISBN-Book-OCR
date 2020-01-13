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
from os.path import isfile, join
from matplotlib import pyplot as plt
from scipy import ndimage
import numpy as np

def main():
    images_url = 'images/isbn/'
    custom_config = r'-l eng --oem 3 --psm 6'
    for files in listdir(images_url):
        file_path = images_url + files
        image = cv2.imread(file_path)

        print('-----------------------------------------')
        print('TESSERACT OUTPUT -->' + files)
        print('-----------------------------------------')
        plt.figure(figsize=(16,12))
        try:
            newdata= pytesseract.image_to_osd(image)
            rotation = re.search('(?<=Rotate: )\\d+', newdata).group(0)
            print(files + " rotation: " + rotation)
            print(newdata)
            if int(rotation) == 0 or int(rotation) == 180:
                # noise_removed = remove_noise(image)
                gray = get_grayscale(image)

            else:
                rotated_image = rotate(image)
                # rotated_image = ndimage.rotate(image, float(rotation) * -1)
                # noise_removed = remove_noise(rotated_image)
                newdata= pytesseract.image_to_osd(rotated_image)
                rotation = re.search('(?<=Rotate: )\\d+', newdata).group(0)
                print(files + " rotation: " + rotation)
                gray = get_grayscale(rotated_image)

            thresh_image = thresholding(gray)
            # thresh_image = adaptiveThreshold(gray)
            plt.imshow(thresh_image, cmap='gray')
            plt.show()
            print(pytesseract.image_to_string(thresh_image, config=custom_config))
        except Exception as e:
            print("image: " + files + " Error: " + str(e))
            continue
        print('-----------------------------------------')

if __name__ == "__main__":
    main()