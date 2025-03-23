FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    MKL_THREADING_LAYER=GNU

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    python3-setuptools \
    ffmpeg \
    git \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies step by step
RUN pip3 install --no-cache-dir -U pip setuptools wheel

# Install PyTorch with CUDA support
RUN pip3 install --no-cache-dir torch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu116

# Install individual dependencies from requirements.txt to isolate issues
RUN pip3 install --no-cache-dir flask argparse
RUN pip3 install --no-cache-dir waitress
RUN pip3 install --no-cache-dir transformers
RUN pip3 install --no-cache-dir pydub
RUN pip3 install --no-cache-dir srt pysrt
RUN pip3 install --no-cache-dir openai
RUN pip3 install --no-cache-dir --verbose openai-whisper

# Copy the application code
COPY . .

# Create default config
RUN cp tofu_transcribe/config.json.example tofu_transcribe/config.json && \
    sed -i 's/"device": "cpu"/"device": "cuda"/g' tofu_transcribe/config.json

# Set the entry point
ENTRYPOINT ["python3", "-m", "tofu_transcribe.main", "--config", "tofu_transcribe/config.json"]

# Default command (can be overridden)
CMD ["--webserver"] 
