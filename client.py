import numpy as np
import os,cv2,time,requests,time
import pytesseract
from pdf2image import convert_from_path

url = 'http://100.114.241.89:5001'
# url = 'http://172.17.0.100:5001'
# url = "http://masterNode:5001"

## Add code to download the pdf
def download_pdf(url):
    # Send a request to download the PDF file
    response = requests.get(url+'/download')

    # Check the response from the server
    if response.text == "No more PDF files available":
        # Perform a full computer shutdown if there are no more PDF files available
        # os.system("shutdown /s /t 0")
        print("Waiting for fiels")
        time.sleep(1)
    else:
        # Get the original file name from the response headers
        file_name = response.headers["Content-Disposition"].split("=")[1]

        # Save the PDF file to the local filesystem with the original file name
        file_path = os.path.join("pdfs", file_name)
        with open(file_path, "wb") as f:
            f.write(response.content)
        print("PDF file downloaded successfully")

        # Return the full path of the file
        return file_path

## Add code to Tesseract the pdf
def ocr_image(file_name):
    # Open the PDF file
    print(file_name)
    images = convert_from_path(str(file_name))

    print(file_name)
    # return
    # os.rmdir(tmp_folder)

    text = ''

    for image in images:

        image = np.array(image)

        height, width = image.shape[:2]

        new_height = int(height * 1.5)
        new_width = int(width * 1.5)
        
        image = cv2.resize(image, (new_width, new_height))

        # Blur the image slightly to reduce noise
        img = cv2.blur(image, (3, 3))

        # Convert the image to gray scale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Performing OTSU threshold
        ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

        # Specify structure shape and kernel size.
        # Kernel size increases or decreases the area
        # of the rectangle to be detected.
        # A smaller value like (10, 10) will detect
        # each word instead of a sentence.
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))

        # Applying dilation on the threshold image
        dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)

        # Finding contours
        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,
                                                        cv2.CHAIN_APPROX_NONE)

        # Creating a copy of image
        im2 = img.copy()

        # A text file is created and flushed
        # Looping through the identified contours
        # Then rectangular part is cropped and passed on
        # to pytesseract for extracting text from it
        # Extracted text is then written into the text file
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            
            # Drawing a rectangle on copied image
            rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Cropping the text block for giving input to OCR
            cropped = im2[y:y + h, x:x + w]

            # Get the size of the image
            height, width, _ = cropped.shape

            # Calculate the size of the border (5% of the image size)
            border_size = int(min(height, width) * 0.05)

            # Create a white border around the image
            cropped = cv2.copyMakeBorder(image, 
                                                top=border_size, 
                                                bottom=border_size, 
                                                left=border_size, 
                                                right=border_size, 
                                                borderType=cv2.BORDER_CONSTANT, 
                                                value=[255, 255, 255])

            height, width = cropped.shape[:2]

            new_height = int(height * 2.3)
            new_width = int(width * 2.0)
            
            cropped = cv2.resize(cropped, (new_width, new_height))

        text += '\n-------\n' + pytesseract.image_to_string(image)
        with open('{}.txt'.format(file_name),'w') as f:
            f.write(text)
            f.close()

## Here is code to send it back
def send_text_file(file_name):
    # Set the URL of the Flask app
    # url += "upload_text"

    # Read the text file
    with open(file_name, "r") as f:
        text = f.read()

    # Send the text file to the Flask app
    while True:
        response = requests.post(url+'/upload_text', files={"text_files": (file_name, text)})

        # Check the status code of the response
        if response.status_code == 200:
            # Print the response from the server
            print(response.text)
            break
        else:
            # Wait for a moment and try again
            time.sleep(1)

# Call the function with a file name
while True:
    file__name = download_pdf(url=url)
    ocr_image(file__name)
    send_text_file("{}.txt".format(file__name))
