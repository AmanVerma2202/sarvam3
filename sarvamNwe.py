import os
import logging
from flask import Flask, request, render_template, redirect, url_for, send_file
import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageEnhance, ImageOps
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['LOG_FOLDER'] = 'logs/'

# Path to Tesseract executable (adjust for your system)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure logging
logging.basicConfig(filename=os.path.join(app.config['LOG_FOLDER'], 'app.log'), level=logging.INFO)

def preprocess_image(img):
    """Preprocess image for better OCR results."""
    img = img.convert("L")  # Convert to grayscale
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)  # Increase contrast
    img = ImageOps.invert(img)  # Invert colors
    return img

def extract_and_compare(pdf_path, output_txt_file, annotated_pdf_file):
    """Extract text from PDF, compare it with Tesseract OCR results, and annotate mismatches."""
    pdf_document = fitz.open(pdf_path)
    mismatch_found = False

    # Create a new PDF for annotation
    annot_pdf = fitz.open(pdf_path)

    with open(output_txt_file, 'w', encoding='utf-8') as output_file:
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            annot_page = annot_pdf[page_num]
            words = page.get_text("words")

            # Initialize a flag to alternate box styles
            alternate_box = True

            # To track vertical positions of text boxes to avoid overlap
            last_y_position = 0

            for word in words:
                x0, y0, x1, y1, text = word[:5]

                word_image = page.get_pixmap(clip=fitz.Rect(x0, y0, x1, y1), dpi=300)
                img = Image.open(io.BytesIO(word_image.tobytes("png")))

                img = preprocess_image(img)

                tesseract_text = pytesseract.image_to_string(img, config='--psm 8 --oem 3').strip()

                if len(text) == len(tesseract_text):
                    for i, (char_original, char_tesseract) in enumerate(zip(text, tesseract_text)):
                        if ord(char_original) != ord(char_tesseract):
                            mismatch_found = True

                            # Log the mismatch
                            logging.info(f"Mismatch on page {page_num + 1}: "
                                         f"Actual embedded '{char_original}' (U+{ord(char_original):04X}) "
                                         f"To be embedded '{char_tesseract}' (U+{ord(char_tesseract):04X})")

                            # Calculate individual character's bounding box with padding
                            char_x0 = x0 + (x1 - x0) * i / len(text)
                            char_x1 = char_x0 + (x1 - x0) / len(text)
                            padding = 2  # Space between characters
                            char_box = fitz.Rect(char_x0 - padding, y0 - padding, char_x1 + padding, y1 + padding)

                            # Alternate box styles or positions
                            if alternate_box:
                                box_color = (1, 0, 0)  # Red box for original character
                                text_color = (1, 0, 0)  # Red text for original character
                                alternate_box = False
                            else:
                                box_color = (0, 0.5, 0)  # Green box for Tesseract character
                                text_color = (0, 0.5, 0)  # Green text for Tesseract character
                                alternate_box = True

                            # Annotate the mismatch: Draw box around the character
                            annot_page.draw_rect(char_box, color=box_color, width=2)

                            # Calculate the y-position for the annotation text dynamically to avoid overlap
                            vertical_margin = 20
                            current_y_position = max(y1, last_y_position + vertical_margin)
                            last_y_position = current_y_position

                            annotation_text = (f"Actual embedded: '{char_original}' (U+{ord(char_original):04X})\n"
                                               f"To be embedded: '{char_tesseract}' (U+{ord(char_tesseract):04X})")

                            # Create a bounding box for the annotation text with dynamic y-position
                            text_box = fitz.Rect(char_x1 + 20, current_y_position, char_x1 + 200, current_y_position + 30)

                            # Add the annotation text near the box
                            annot_page.insert_textbox(text_box, annotation_text, fontsize=8, color=text_color)

                            # Write mismatch to the output file
                            output_file.write(f"Mismatch on page {page_num + 1}: "
                                              f"Actual embedded '{char_original}' (U+{ord(char_original):04X}) "
                                              f"To be embedded '{char_tesseract}' (U+{ord(char_tesseract):04X})\n")
                else:
                    mismatch_found = True
                    logging.info(f"Mismatch in word length on page {page_num + 1}: Actual embedded '{text}' "
                                 f"vs To be embedded '{tesseract_text}'")

                    # Alternate annotation styles for word length mismatch
                    if alternate_box:
                        box_color = (1, 0, 0)  # Red box for original text
                        text_color = (1, 0, 0)  # Red text for original text
                        alternate_box = False
                    else:
                        box_color = (0, 1, 0)  # Green box for Tesseract text
                        text_color = (0, 1, 0)  # Green text for Tesseract text
                        alternate_box = True

                    # Annotate the entire word length mismatch with padding
                    annot_page.draw_rect(fitz.Rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2), color=box_color, width=2)

                    # Dynamically calculate y-position for annotation text to avoid overlap
                    current_y_position = max(y1, last_y_position + vertical_margin)
                    last_y_position = current_y_position

                    annotation_text = f"Wrong: '{text}'\nCorrect: '{tesseract_text}'"
                    annot_page.insert_textbox(fitz.Rect(x1 + 20, current_y_position, x1 + 50, current_y_position + 30),
                                              annotation_text, fontsize=8, color=text_color)

                    # Write length mismatch to the output file
                    output_file.write(f"Mismatch in word length on page {page_num + 1}: "
                                      f"Original '{text}' vs Tesseract '{tesseract_text}'\n")

    if mismatch_found:
        # Save annotated PDF
        annot_pdf.save(annotated_pdf_file)
        return True
    else:
        logging.info("No mismatches found.")
        return False


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and perform PDF analysis."""
    if 'pdf_file' not in request.files:
        return redirect(request.url)
    file = request.files['pdf_file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        output_txt_file = os.path.join(app.config['UPLOAD_FOLDER'], 'mismatches.txt')
        annotated_pdf_file = os.path.join(app.config['UPLOAD_FOLDER'], 'annotated_output.pdf')

        # Call function to process the PDF and annotate mismatches
        mismatch_found = extract_and_compare(file_path, output_txt_file, annotated_pdf_file)

        if mismatch_found:
            return render_template('index.html', pdf_url=url_for('display_pdf', filename='annotated_output.pdf'))
        else:
            return render_template('index.html', message="No mismatches found.")
    return redirect(url_for('index'))

@app.route('/pdf/<filename>')
def display_pdf(filename):
    """Display the annotated PDF."""
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=False)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    if not os.path.exists('logs'):
        os.makedirs('logs')
    app.run(debug=True)
