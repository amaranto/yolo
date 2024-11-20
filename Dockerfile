FROM ubuntu:24.04 as cv-model-base-2404
WORKDIR /app
RUN apt-get update --fix-missing -y
RUN apt install -y ffmpeg x264 libx264-dev gcc wget lsof
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
RUN dpkg -i cuda-keyring_1.1-1_all.deb
RUN apt-get -y update
RUN apt-get -y install cuda-toolkit-12-6
RUN apt-get install -y nvidia-open
RUN apt-get install -y python3-pip libopencv-dev python3-opencv
RUN apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev libgtk-3-dev libpng-dev libjpeg-dev libopenexr-dev libtiff-dev libwebp-dev libopencv-dev libssl-dev 
#RUN rm /usr/lib/python*/EXTERNALLY-MANAGED

FROM cv-model-base-2404
COPY requirements.txt .
RUN pip install --break-system-packages -r requirements.txt 

COPY . .
EXPOSE 8080
CMD ["python3", "app.py"]