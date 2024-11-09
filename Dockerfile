FROM ubuntu:24.04
WORKDIR /app
RUN apt update -y
RUN apt install -y ffmpeg x264 libx264-dev gcc wget
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
RUN dpkg -i cuda-keyring_1.1-1_all.deb
RUN apt-get -y update
RUN apt-get -y install cuda-toolkit-12-6
RUN apt-get install -y nvidia-open
RUN apt-get install -y python3-pip
COPY requirements.txt .
RUN pip install -r requirements.txt --break-system-packages
COPY . .
EXPOSE 8080
CMD ["python3", "app.py"]