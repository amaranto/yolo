FROM ubuntu:24.04 as cv-model-base-2404 
WORKDIR /app
RUN apt-get update --fix-missing -y
RUN apt install -y ffmpeg x264 libx264-dev gcc wget lsof libavcodec-dev libavformat-dev libswscale-dev libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev libgtk-3-dev libpng-dev libjpeg-dev libopenexr-dev libtiff-dev libwebp-dev libopencv-dev libssl-dev python3-opencv\
    && rm -rf /var/lib/apt/lists/*
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
RUN dpkg -i cuda-keyring_1.1-1_all.deb && rm -f cuda-keyring_1.1-1_all.deb
RUN apt-get -y update && apt-get -y install cuda-toolkit-12-6 nvidia-open python3-pip && rm -rf /var/lib/apt/lists/*

FROM cv-model-base-2404
COPY requirements.txt .
RUN pip install --break-system-packages -r requirements.txt
#us-central1-docker.pkg.dev/raizen-genai-01/raizen-sm-artifact/cv-model-base:v1.0.0

COPY . .
EXPOSE 8080
CMD ["python3", "app.py"]
# us-central1-docker.pkg.dev/raizen-genai-01/raizen-sm-artifact/raizen-sm-app:v1.0.0