# simplepres

This is a PDF drawing tool that allows the user to add annotations and drawings to a PDF file. The code is written in Python, using the PySide6 library for GUI development.

## Features
* The user can select the color and thickness of the drawing/annotation.
* The user can move, delete, or add lines to the annotations.
* The tool provides a render of the PDF page, allowing the user to annotate on top of it.

## How to use

The code takes in a PDF file name as a command line argument. To run the code, execute the following command in your terminal:

```
python3 filename.py -f your_pdf_file.pdf
```

The GUI will appear, displaying the first page of the PDF file. The user can select the color and thickness of the drawing/annotation using the right-click menu. The user can also switch between pages by clicking the “next” and “previous” buttons. To add a new annotation, the user can simply click and drag on the PDF render. To move an annotation, the user can click and drag it to a new location. To delete an annotation, the user can right-click on it and select “delete” from the menu.

## Additional Information

This code is written in Python 3 and requires the PySide6 library. The PySide6 library provides bindings for the Qt library, which is a popular framework for developing cross-platform graphical user interfaces.

## License

MIT
