# Docker Support for Tofu-Transcribe

This document describes how to run Tofu-Transcribe using Docker with GPU support.

## Prerequisites

- Docker installed on your system
- NVIDIA GPU with the NVIDIA Container Toolkit installed (for GPU support)
- NVIDIA drivers installed on the host system

## GPU Setup

Make sure your system has the NVIDIA Container Toolkit installed:

```bash
# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

## Building and Running

### Using docker-compose (Recommended)

1. Build and start the container:
   ```bash
   docker-compose up -d
   ```

2. Check container logs:
   ```bash
   docker-compose logs -f
   ```

3. Stop the container:
   ```bash
   docker-compose down
   ```

### Using Docker commands directly

1. Build the Docker image:
   ```bash
   docker build -t tofu-transcribe .
   ```

2. Run the container with GPU support:
   ```bash
   docker run --gpus all -p 8080:8080 -v $(pwd)/data:/app/data tofu-transcribe
   ```

3. For processing a specific video file:
   ```bash
   docker run --gpus all -v $(pwd)/data:/app/data tofu-transcribe --input /app/data/your_video.mp4
   ```

## Configuration

The Dockerfile automatically copies the example config and sets the device to "cuda". If you need to modify the configuration:

1. Create a custom config.json based on config.json.example
2. Mount it when running the container:
   ```bash
   docker run --gpus all -p 8080:8080 -v $(pwd)/data:/app/data -v $(pwd)/custom_config.json:/app/tofu_transcribe/config.json tofu-transcribe
   ``` 