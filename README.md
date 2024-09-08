# sarvamTask
Application allows users to upload a PDF and analyzes the text using both PyMuPDF and Tesseract OCR. The application compares the text extracted by each method, detects character mismatches, and annotates them on the PDF. It highlights differences between the original and OCR-extracted text and provides an option to download the annotated PDF.



### Files
```
├── sarvamNwe.py        # Main Flask application
├── templates/
│   └── index.html      # HTML template for the web interface
├── uploads/            # Directory where uploaded PDFs are stored
├── logs/               # Log file
│    └── app.log
└── README.md           # Project README file
```


## How to Run Locally

Clone the repository:

   ```bash
   git clone https://github.com/AmanVerma2202/sarvam3.git
   cd sarvam3
   install dependencies flask,fitz, pytesseract, PIL
   set up your tesseract path
   run python sarvamNwe.py
 ```

## Demo Video
[![Watch the demo video](https://github.com/AmanVerma2202/sarvam3/blob/main/sarvamrec.mp4)](https://github.com/AmanVerma2202/sarvam3/blob/main/sarvamrec.mp4)


## Photos
![Alt text of the image](https://github.com/AmanVerma2202/sarvam3/blob/main/Screenshot%20(100).png)
![Alt text of the image](https://github.com/AmanVerma2202/sarvam3/blob/main/Screenshot%20(101).png)
![Alt text of the image](https://github.com/AmanVerma2202/sarvam3/blob/main/Screenshot%20(102).png)


## Tech Stack
**Flask:** Web framework used for building the backend and handling file uploads.<br/>
**PyMuPDF (Fitz):** Library for extracting text, font, and position information from PDFs.<br/>
**Tesseract OCR:** Optical Character Recognition engine for text extraction from PDF images.<br/>
**PIL (Pillow):** Used for image preprocessing to enhance OCR results.<br/>
**HTML/CSS:** For building a simple user interface.<br/>
**JavaScript:** For adding a loader to indicate processing time.<br/>
**Logging:** For tracking mismatches and processing information.<br/>


## Approach
**File Upload:** <br/>
Users can upload a PDF file through a simple web interface built with HTML/CSS.<br/>
The backend, implemented with Flask, handles the file upload and saves it to the server.<br/>

**Text Extraction:** <br/>
PyMuPDF (Fitz) is used to extract the visible text, font details, and bounding boxes from each page of the uploaded PDF.<br/>
For each word, the bounding box is identified and captured for further processing.<br/>

**Image Preprocessing:** <br/>
Each word's bounding box is used to capture a section of the PDF as an image.<br/>
The image is then preprocessed (converted to grayscale, contrast enhancement, inversion) using the Pillow library to improve the accuracy of the Tesseract OCR engine.<br/>

**Text Recognition and Comparison:** <br/>
Tesseract OCR extracts text from the preprocessed images.<br/>
The extracted text is compared character by character with the original text extracted using PyMuPDF.<br/>
If a mismatch is found (either in the length of the word or individual characters), the system identifies it.<br/>

**Mismatch Annotation:** <br/>
The mismatched characters or words are annotated directly on the PDF.<br/>
Alternating between dark red and dark green colors, boxes are drawn around the mismatched characters.<br/>
Additional annotation text is inserted near the mismatch, indicating the original and corrected Unicode values.<br/>




## Key Features:
**1**. Extracts text from PDF using PyMuPDF and Tesseract OCR.<br/>
**2**. Compares the text and detects mismatches.<br/>
**3**. Annotates mismatched characters in the PDF.<br/>
**4**. User-friendly web interface with file upload and progress loader.<br/>



## Contributing
Feel free to submit issues, fork the repository, and send pull requests if you want to contribute.
