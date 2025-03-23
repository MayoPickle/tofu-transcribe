# Docker Support for Tofu-Transcribe

This document describes how to run Tofu-Transcribe using Docker with GPU support.

## Prerequisites

- Docker installed on your system
- NVIDIA GPU with the NVIDIA Container Toolkit installed (for GPU support)
- NVIDIA drivers installed on the host system

## GPU Setup

Make sure your system has the NVIDIA Container Toolkit installed:

```bash
# Install NVIDIA Container Toolkit (Basic installation)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

## Running Options

### Option 1: Using Pre-built Image (Fastest)

You can directly pull the pre-built image from GitHub Container Registry:

```bash
docker pull ghcr.io/mayopickle/tofu-transcribe:main
```

Then run it with:

```bash
docker run --gpus all -p 8080:8080 -v $(pwd)/data:/app/data ghcr.io/mayopickle/tofu-transcribe:main
```

Or use it in your docker-compose.yml:

```yaml
version: '3.8'

services:
  tofu-transcribe:
    image: ghcr.io/mayopickle/tofu-transcribe:main
    container_name: tofu-transcribe
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### Option 2: Building the Image Yourself

#### Using docker-compose (Recommended)

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

#### Using Docker commands directly

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

## Configuration Options

The Dockerfile automatically copies the example config and sets the device to "cuda". Here are different ways to use your own custom configuration:

### 1. Using Volume Mounting (Recommended)

Create a custom config file and mount it directly:

```bash
docker run --gpus all -p 8080:8080 -v $(pwd)/data:/app/data -v $(pwd)/your_config.json:/app/tofu_transcribe/config.json tofu-transcribe
```

### 2. Using docker-compose with Custom Config

Edit your docker-compose.yml to add the config file as a volume:

```yaml
version: '3.8'

services:
  tofu-transcribe:
    image: ghcr.io/mayopickle/tofu-transcribe:main  # Or use 'build:' section if building locally
    container_name: tofu-transcribe
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
      - ./your_config.json:/app/tofu_transcribe/config.json
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 3. Using Command Line Parameter

Place your config file in a mounted directory and specify it with the --config parameter:

```bash
docker run --gpus all -p 8080:8080 -v $(pwd)/data:/app/data ghcr.io/mayopickle/tofu-transcribe:main --config /app/data/config.json
```

### 4. Building Custom Image with Your Config

Copy your config file to the project directory before building:

```bash
cp your_config.json ./tofu_transcribe/config.json
docker build -t tofu-transcribe-custom .
```

## Example Configuration

Below is a sample of what your configuration file might look like. Create a copy of the config.json.example and modify it:

```json
{
    "model": "medium",
    "device": "cuda",
    "language": "Chinese",
    "flask_host": "0.0.0.0",
    "flask_port": 8080,
    "live_root_dir": "./data",
    "server_chan_key": "your_key_here",
    "open_ai_key": "your_openai_key",
    "semantic_emotion_model": "uer/roberta-base-finetuned-jd-binary-chinese",
    "speech_emotion_model": "superb/wav2vec2-base-superb-er",
    "nlp_model": "gpt-4-turbo",
    "score_threshold": 0.90,
    "ffmpeg_options": {
        "sample_rate": 16000,
        "channels": 1
    }
}
```

## GPU Troubleshooting

If you encounter GPU-related issues (such as "Error: could not select device driver "" with capabilities: [[gpu]]"), follow these steps:

### Verify GPU is Available

First, verify that your NVIDIA GPU is properly detected by the system:

```bash
nvidia-smi
```

This should display information about your GPU. If this works, you have proper NVIDIA drivers installed.

### Complete NVIDIA Container Toolkit Installation

For Ubuntu, follow these exact steps:

```bash
# Remove any old versions first
sudo apt-get remove nvidia-container-toolkit nvidia-container-runtime nvidia-docker2

# Install prerequisites
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg

# Add NVIDIA GPG key
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

# Add the repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Update and install
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker runtime
sudo nvidia-ctk runtime configure --runtime=docker

# Restart Docker
sudo systemctl restart docker
```

### Test NVIDIA Container Support

After installation, test if NVIDIA container support is working:

```bash
# Use a CUDA version that matches your system (check with nvidia-smi)
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

If this works, Docker can now access your GPU.

### Configure Docker Default Runtime

If you still have issues, you can configure the Docker daemon to use NVIDIA as the default runtime:

```bash
sudo nano /etc/docker/daemon.json
```

Add the following content (create the file if it doesn't exist):

```json
{
  "default-runtime": "nvidia",
  "runtimes": {
    "nvidia": {
      "path": "/usr/bin/nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
```

Then restart Docker:

```bash
sudo systemctl restart docker
```

### Alternative: Run Without GPU

If you can't get GPU support working, you can run the application in CPU mode:

1. Run the container without `--gpus all`:
   ```bash
   docker run -p 8080:8080 -v $(pwd)/data:/app/data ghcr.io/mayopickle/tofu-transcribe:main
   ```

2. Modify your config.json to use CPU:
   ```json
   {
     "device": "cpu",
     ...
   }
   ```

Note that CPU-based transcription will be much slower than GPU. 