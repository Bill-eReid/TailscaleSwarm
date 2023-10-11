FROM python:3.8-slim

# Install pip
RUN apt-get update && apt-get install -y python3-pip

# Copy the code and required files into the container
COPY . /app
WORKDIR /app
RUN mkdir /app/pdfs

# Install the necessary dependencies from the requirements file
# RUN python3 -m pip install -r requirements.txt

RUN apt-get update && apt-get install tesseract-ocr -y
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y
RUN pip install -r requirements.txt 


RUN apt-get --fix-missing update && apt-get --fix-broken install && apt-get install -y poppler-utils && apt-get install -y tesseract-ocr && \
    apt-get install -y libtesseract-dev && apt-get install -y libleptonica-dev && ldconfig && apt install -y libsm6 libxext6

RUN pip install pytesseract
RUN pip install numpy
RUN pip install pandas

RUN apt-get install python3-opencv -y

RUN pip install opencv-python

RUN mkdir /output

EXPOSE 5001

# Set the command to run the client code
CMD ["python", "client.py"]
