# ISBN Book OCR

This is an image to text recognition that focuses on ISBN numbers from books.

It can return either ISBN-10 or ISBN-13 codes.

## Usage

To scan, you can call the scan.py script in the src folder:
```shell
python scan.py --path {Path to File}
```

1. To scan an image, you can run:
    ```shell
    python scan.py -p isbn_images/test.png
    ```
2. To scan a folder of images, you can run:
    ```shell
    python scan.py -p isbn_images/
    ```
3. You can check your ISBN results against an online source to make sure that it exists
    ```shell
    python scan.py -p isbn_images/ -o
    ```
    Note: Currently using AbeBooks as a checker.
4. You can export the data as a csv file
    ```shell
    python scan.py -p isbn_images/ -o -x output.csv
    ```

Note: By default, script will output a csv file with the results.

## Authors

* **Jimmy Le** - [Jldevops](https://github.com/jldevops)

## License

Licensed under the [MIT License](LICENSE)