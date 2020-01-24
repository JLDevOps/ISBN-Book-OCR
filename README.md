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
    python scan.py --path isbn_images/test.png
    ```
2. To scan a folder of images, you can run:
    ```shell
    python scan.py --path isbn_images/
    ```

## Authors

* **Jimmy Le** - [Jldevops](https://github.com/jldevops)

## License

Licensed under the [MIT License](LICENSE)