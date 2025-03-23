# TofuTranscribe

TofuTranscribe is an AI-powered tool that analyzes videos to extract emotions, identify the best segments, and automatically generate short clips. Using multiple machine learning models, it evaluates emotional content from multiple dimensions, helping users quickly distill the most valuable and engaging parts of their videos. The system supports both manual input and automated processing via [BililiveRecorder](https://github.com/BililiveRecorder/BililiveRecorder) Webhooks.

## Key Features

- **Multi-dimensional Emotion Analysis**
  - Leverages multiple ML models to analyze emotions from text, audio characteristics, and speech patterns
  - Identifies the most engaging or impactful segments based on comprehensive analysis
  - Creates visualizations of emotion trends throughout the video

- **Text & Subtitle Processing**
  - Automatically transcribes speech using Whisper model
  - Processes existing subtitle files for emotion extraction

- **Flexible Input Options**
  - **BililiveRecorder Webhook**: Automatically processes videos after they're recorded from livestreams
  - **Manual Input**: Process local video files via command line interface
  
- **Advanced Processing Pipeline**
  - Audio extraction and conversion to analysis-friendly formats
  - Parallel processing of speech and text data
  - Comprehensive scoring system to identify high-value segments
  - Visualization tools for emotion trends

## How It Works

TofuTranscribe combines several AI technologies to analyze video content:

1. **Audio Extraction**: FFmpeg extracts and processes the audio track from videos
2. **Speech Recognition**: Whisper AI transcribes speech to text
3. **Emotion Analysis Pipeline**:
   - **Text Analysis**: Analyzes transcribed text for emotional content using transformer models
   - **Speech Analysis**: Evaluates voice tone, pitch, and other audio features for emotional signals
   - **Combined Scoring**: Integrates both analysis types for comprehensive emotional evaluation
4. **Segment Selection**: Identifies and extracts high-emotion segments based on configurable thresholds
5. **Results Generation**: Creates visualizations, analysis reports, and optional clip compilations

## Requirements

- Python 3.9+
- FFmpeg (for video and audio processing)
- PyTorch (for deep learning models)
- Whisper (for speech recognition)
- Transformers (for NLP models)
- Other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Nayutaa/TofuTranscribe
   ```

2. Navigate to the project directory and install dependencies:
   ```bash
   cd TofuTranscribe
   pip install -r requirements.txt
   ```

3. Create a configuration file:
   ```bash
   cp tofu_transcribe/config.json.example tofu_transcribe/config.json
   ```

4. Edit the configuration file to suit your needs

## Getting Started

### Option 1: Process Videos via BililiveRecorder Webhook

1. Configure your webhook settings in `config.json`:
   ```json
   {
     "flask_host": "0.0.0.0",
     "flask_port": 8080
   }
   ```

2. Start the webhook server:
   ```bash
   python tofu_transcribe/main.py --webserver
   ```

3. Configure BililiveRecorder to send webhooks to your TofuTranscribe instance when recordings are complete

### Option 2: Process Videos Manually

1. Run the script with your video file:
   ```bash
   python tofu_transcribe/main.py --input path/to/video.mp4
   ```

2. Results will be saved in a directory named after your input file

## Configuration Options

The `config.json` file contains several important settings:

| Option | Description |
|--------|-------------|
| `model` | Whisper model size (tiny, base, small, medium, large) |
| `device` | Computing device (cpu, cuda) |
| `language` | Primary language of the videos |
| `semantic_emotion_model` | Model used for text emotion analysis |
| `speech_emotion_model` | Model used for speech emotion analysis |
| `score_threshold` | Threshold for selecting emotional segments |
| `flask_host`/`flask_port` | Webhook server settings |
| `server_chan_key` | Optional key for ServerChan notifications |
| `open_ai_key` | API key for OpenAI services |
| `ffmpeg_options` | Audio processing settings including sample rate and channels |

## Output and Results

After processing a video, TofuTranscribe generates several output files in the working directory:

- **Transcription Files**:
  - `tofu_transcribe.srt`: Full subtitle file of the video
  - `tofu_transcribe.json`: Detailed transcription data with timestamps

- **Emotion Analysis**:
  - `semantic_emotion_analysis_results.json`: Text-based emotion analysis results
  - `speech_emotion_analysis_results.json`: Speech-based emotion analysis results
  - `grouped_semantic_emotion_analysis_results.json`: Combined analysis results

- **Visualizations**:
  - `emotion_trend.png`: Graph showing emotion intensity throughout the video
  - `emotion_heatmap.png`: Visual representation of emotional hotspots

- **Selected Segments**:
  - List of high-emotion timestamps with scores
  - Optionally, extracted video clips of these segments

## Example Outputs

Here's a look at what you can expect from TofuTranscribe:

### Emotion Analysis JSON Format

```json
{
  "segments": [
    {
      "start_time": 15.2,
      "end_time": 20.5,
      "text": "This is absolutely incredible!",
      "semantic_score": 0.92,
      "speech_score": 0.88,
      "combined_score": 0.90
    },
    {
      "start_time": 45.7,
      "end_time": 52.3,
      "text": "I can't believe what we're seeing here.",
      "semantic_score": 0.85,
      "speech_score": 0.89,
      "combined_score": 0.87
    }
  ]
}
```

### Emotion Trend Visualization

The emotion trend graph plots emotion intensity over time, making it easy to identify high-value segments visually:

```
Emotion
Intensity
    ^
1.0 |     *         *        *     
    |    /|\       /|\      /|\    
0.8 |   / | \     / | \    / | \   
    |  /  |  \   /  |  \  /  |  \  
0.6 | /   |   \ /   |   \/   |   \ 
    |/    |    \    |    \   |    \
0.4 |     |     \   |     \  |     
    |     |      \  |      \ |     
0.2 |     |       \ |       \|     
    |_____|________|_________|_____
    0    30        60        90   Time (s)
```

## Advanced Usage

### Fine-tuning Emotion Detection

Adjust the `score_threshold` in your config.json to control sensitivity:
- Higher values (e.g., 0.90) will only select extremely emotional segments
- Lower values (e.g., 0.80) will include more segments with moderate emotion

### Using Custom Models

TofuTranscribe supports using custom-trained models:

1. Train your emotion detection model following transformer model conventions
2. Update your config.json to point to your model:
   ```json
   {
     "semantic_emotion_model": "path/to/your/custom/model"
   }
   ```

### Server Notifications

Configure ServerChan integration to receive notifications when processing is complete:

1. Obtain a ServerChan key
2. Add the key to your config.json:
   ```json
   {
     "server_chan_key": "your-server-chan-key"
   }
   ```

### Batch Processing

Process multiple videos in sequence with a simple script:

```python
import os
import subprocess

video_folder = "./videos"
for video_file in os.listdir(video_folder):
    if video_file.endswith((".mp4", ".mkv", ".avi")):
        video_path = os.path.join(video_folder, video_file)
        subprocess.run(["python", "tofu_transcribe/main.py", "--input", video_path])
```

## Performance Optimization

### Hardware Recommendations

TofuTranscribe's performance varies based on your hardware configuration:

| Component | Minimum | Recommended | Impact |
|-----------|---------|-------------|--------|
| CPU | 4 cores | 8+ cores | Faster audio processing, parallel analysis |
| RAM | 8GB | 16GB+ | Handles larger videos without swapping |
| GPU | N/A | CUDA-compatible | 5-10x speedup for model inference |
| Storage | SSD | NVMe SSD | Faster I/O for large video files |

### Processing Time Benchmarks

Approximate processing times for a 60-minute 1080p video:

| Configuration | Transcription | Emotion Analysis | Total |
|---------------|---------------|------------------|-------|
| CPU only (4-core) | ~45 min | ~30 min | ~75 min |
| CPU only (8-core) | ~25 min | ~20 min | ~45 min |
| CPU + GPU (RTX 3060) | ~10 min | ~5 min | ~15 min |
| CPU + GPU (RTX 4090) | ~5 min | ~2 min | ~7 min |

### Optimization Tips

1. **Use GPU acceleration** by setting `"device": "cuda"` in config.json
2. **Choose appropriate model sizes**:
   - For quick analysis: `"model": "tiny"` or `"model": "base"`
   - For accuracy: `"model": "medium"` or `"model": "large"`
3. **Pre-convert videos** to optimize formats before processing
4. **Split long videos** into smaller segments for parallel processing

## Integration with Other Tools

### Video Editing Software

Export TofuTranscribe results to formats compatible with popular video editors:

#### DaVinci Resolve Integration

1. Process your video with TofuTranscribe
2. Use the script below to convert emotional segments to DaVinci Resolve markers:

```python
# Convert TofuTranscribe results to DaVinci Resolve markers
import json

with open("work_dir/grouped_semantic_emotion_analysis_results.json") as f:
    data = json.load(f)

with open("davinci_markers.csv", "w") as f:
    f.write("Marker Name,Timecode,Color\n")
    for segment in data:
        if segment["combined_score"] > 0.85:
            start_time = segment["start_time"]
            hours = int(start_time / 3600)
            minutes = int((start_time % 3600) / 60)
            seconds = int(start_time % 60)
            frames = int((start_time % 1) * 24)  # Assuming 24fps
            timecode = f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"
            f.write(f"Emotional Segment,{timecode},Blue\n")
```

### Streaming Platforms

TofuTranscribe can automate highlight creation for platforms like:

- **YouTube**: Generate timestamps for video descriptions
- **Twitch**: Identify clips for channel highlights
- **Bilibili**: Create engaging compilations from livestreams

## Technical Deep Dive

### Emotion Analysis Algorithms

TofuTranscribe uses a multi-modal approach to emotion detection:

1. **Text-based Analysis**:
   - Uses Transformer models fine-tuned on emotional text datasets
   - The default model (`uer/roberta-base-finetuned-jd-binary-chinese`) specializes in Chinese sentiment
   - Scores text on multiple dimensions: positive/negative valence, arousal, dominance

2. **Speech-based Analysis**:
   - Analyzes acoustic features using wav2vec2 models
   - Detects emotional signals in voice tone, pitch variation, speaking rate
   - Captures emotions that may not be explicit in the transcribed text

3. **Fusion Algorithm**:
   - Aligns speech and text segments temporally
   - Applies weighted scoring based on confidence levels
   - Uses configurable thresholds to identify significant emotional moments

### Model Selection Logic

The model choice significantly impacts both accuracy and performance:

| Model | Size | Languages | Accuracy | Speed |
|-------|------|-----------|----------|-------|
| Whisper Tiny | 39M | Multilingual (limited) | Basic | Fastest |
| Whisper Base | 74M | Multilingual | Good | Fast |
| Whisper Small | 244M | Multilingual | Better | Medium |
| Whisper Medium | 769M | Multilingual | Excellent | Slow |
| Whisper Large | 1.5GB | Multilingual | Best | Slowest |

## Comparison with Similar Tools

| Feature | TofuTranscribe | Traditional Video Editors | ML-based Highlight Generators |
|---------|----------------|---------------------------|-------------------------------|
| Emotion Analysis | Deep multi-modal | Manual | Limited |
| Processing Speed | Medium-Fast | N/A (manual) | Fast |
| Customizability | High | High | Low |
| Accessibility | Command line & API | GUI | Varies |
| Cost | Free, open-source | Often paid | Often SaaS-based |
| Privacy | Local processing | Local processing | Often cloud-based |

## FAQ

### General Questions

**Q: How accurate is the emotion detection?**  
A: Accuracy varies by language and content type. For Chinese content, accuracy typically ranges from 80-90% when using the recommended models. Factors affecting accuracy include audio quality, speaking clarity, and background noise.

**Q: Can I use this for languages other than Chinese?**  
A: Yes, by changing the language setting and using appropriate models. For optimal results with non-Chinese content, you may need to specify different semantic emotion models in your config.

**Q: Does this work with any video format?**  
A: TofuTranscribe uses FFmpeg for video processing, so it supports most common video formats (MP4, MKV, AVI, etc.). Extremely uncommon formats may require pre-conversion.

### Technical Questions

**Q: Why is GPU memory running out?**  
A: The larger Whisper models (medium, large) require significant GPU memory. Try using a smaller model or processing shorter video segments.

**Q: Can I run this on a server without a display?**  
A: Yes, TofuTranscribe is designed to run headless and can be deployed on servers without displays.

**Q: How can I extend the emotion detection to other dimensions?**  
A: You can replace or supplement the default models with custom-trained ones that detect specific emotional dimensions relevant to your use case.

## Community and Support

### Getting Help

- **GitHub Issues**: Report bugs or request features through the [GitHub issue tracker](https://github.com/Nayutaa/TofuTranscribe/issues)
- **Discussions**: Join discussions about usage and development in the [GitHub Discussions](https://github.com/Nayutaa/TofuTranscribe/discussions) section

### Community Contributions

We welcome contributions of all types:

- **Code**: Add features or fix bugs
- **Models**: Share fine-tuned models for specific languages or domains
- **Documentation**: Improve guides or translate documentation
- **Use Cases**: Share your success stories and applications

## Acknowledgments

TofuTranscribe builds on several outstanding open-source projects:

- [Whisper](https://github.com/openai/whisper) by OpenAI for speech recognition
- [Transformers](https://github.com/huggingface/transformers) by Hugging Face for NLP models
- [PyTorch](https://pytorch.org/) for deep learning capabilities
- [FFmpeg](https://ffmpeg.org/) for video and audio processing
- [BililiveRecorder](https://github.com/BililiveRecorder/BililiveRecorder) for livestream recording integration

## License

This project is released under the [MIT License](LICENSE). You are free to use, copy, modify, and distribute the source code, but you must include the original author information and license notice.

---

# TofuTranscribe [中文文档]

TofuTranscribe 是一款基于人工智能的工具，可以分析视频中的情感内容，识别最佳片段，并自动生成短视频剪辑。该系统利用多种机器学习模型，从多个维度评估情感内容，帮助用户快速提取出视频中最有价值和最具吸引力的部分。系统支持通过手动输入和[录播姬](https://github.com/BililiveRecorder/BililiveRecorder) Webhook自动处理视频。

## 主要功能

- **多维度情感分析**
  - 利用多种机器学习模型分析文本、音频特征和语音模式中的情感
  - 基于综合分析识别最具吸引力或最具冲击力的片段
  - 创建视频情感趋势的可视化表示

- **文本和字幕处理**
  - 使用Whisper模型自动转录语音内容
  - 处理现有字幕文件进行情感提取

- **灵活的输入选项**
  - **录播姬 Webhook**: 在直播录制完成后自动处理视频
  - **手动输入**: 通过命令行处理本地视频文件
  
- **先进的处理流程**
  - 音频提取和格式转换
  - 语音和文本数据的并行处理
  - 全面的评分系统识别高价值片段
  - 情感趋势可视化工具

## 工作原理

TofuTranscribe结合了多种AI技术来分析视频内容：

1. **音频提取**: FFmpeg从视频中提取并处理音轨
2. **语音识别**: Whisper AI将语音转录为文本
3. **情感分析流程**:
   - **文本分析**: 使用transformer模型分析转录文本中的情感内容
   - **语音分析**: 评估语音音调、音高变化和其他音频特征中的情感信号
   - **综合评分**: 整合两种分析类型进行全面的情感评估
4. **片段选择**: 根据可配置的阈值识别并提取高情感片段
5. **结果生成**: 创建可视化、分析报告和可选的片段合集

## 系统要求

- Python 3.9+
- FFmpeg (用于视频和音频处理)
- PyTorch (用于深度学习模型)
- Whisper (用于语音识别)
- Transformers (用于NLP模型)
- 其他依赖项请参阅 `requirements.txt`

## 安装

1. 克隆仓库:
   ```bash
   git clone https://github.com/Nayutaa/TofuTranscribe
   ```

2. 进入项目目录并安装依赖:
   ```bash
   cd TofuTranscribe
   pip install -r requirements.txt
   ```

3. 创建配置文件:
   ```bash
   cp tofu_transcribe/config.json.example tofu_transcribe/config.json
   ```

4. 根据需要编辑配置文件

## 快速入门

### 方式一: 通过录播姬Webhook处理视频

1. 在 `config.json` 中配置webhook设置:
   ```json
   {
     "flask_host": "0.0.0.0",
     "flask_port": 8080
   }
   ```

2. 启动webhook服务器:
   ```bash
   python tofu_transcribe/main.py --webserver
   ```

3. 配置录播姬，使其在录制完成后向TofuTranscribe实例发送webhook

### 方式二: 手动处理视频

1. 使用视频文件运行脚本:
   ```bash
   python tofu_transcribe/main.py --input 视频路径/视频文件.mp4
   ```

2. 结果将保存在以输入文件命名的目录中

## 配置选项

`config.json` 文件包含几个重要设置:

| 选项 | 描述 |
|------|------|
| `model` | Whisper模型大小 (tiny, base, small, medium, large) |
| `device` | 计算设备 (cpu, cuda) |
| `language` | 视频的主要语言 |
| `semantic_emotion_model` | 用于文本情感分析的模型 |
| `speech_emotion_model` | 用于语音情感分析的模型 |
| `score_threshold` | 选择情感片段的阈值 |
| `flask_host`/`flask_port` | Webhook服务器设置 |
| `server_chan_key` | ServerChan通知的可选密钥 |
| `open_ai_key` | OpenAI服务的API密钥 |
| `ffmpeg_options` | 音频处理设置，包括采样率和通道数 |

## 输出和结果

处理视频后，TofuTranscribe会在工作目录中生成几个输出文件:

- **转录文件**:
  - `tofu_transcribe.srt`: 视频的完整字幕文件
  - `tofu_transcribe.json`: 带有时间戳的详细转录数据

- **情感分析**:
  - `semantic_emotion_analysis_results.json`: 基于文本的情感分析结果
  - `speech_emotion_analysis_results.json`: 基于语音的情感分析结果
  - `grouped_semantic_emotion_analysis_results.json`: 综合分析结果

- **可视化**:
  - `emotion_trend.png`: 显示整个视频情感强度的图表
  - `emotion_heatmap.png`: 情感热点的可视化表示

- **选定片段**:
  - 带有评分的高情感时间戳列表
  - 可选的提取视频片段

## 输出示例

以下是TofuTranscribe的预期输出示例:

### 情感分析JSON格式

```json
{
  "segments": [
    {
      "start_time": 15.2,
      "end_time": 20.5,
      "text": "这真是太令人难以置信了！",
      "semantic_score": 0.92,
      "speech_score": 0.88,
      "combined_score": 0.90
    },
    {
      "start_time": 45.7,
      "end_time": 52.3,
      "text": "我无法相信我们正在看到的这一切。",
      "semantic_score": 0.85,
      "speech_score": 0.89,
      "combined_score": 0.87
    }
  ]
}
```

### 情感趋势可视化

情感趋势图绘制了情感强度随时间的变化，方便直观地识别高价值片段:

```
情感
强度
    ^
1.0 |     *         *        *     
    |    /|\       /|\      /|\    
0.8 |   / | \     / | \    / | \   
    |  /  |  \   /  |  \  /  |  \  
0.6 | /   |   \ /   |   \/   |   \ 
    |/    |    \    |    \   |    \
0.4 |     |     \   |     \  |     
    |     |      \  |      \ |     
0.2 |     |       \ |       \|     
    |_____|________|_________|_____
    0    30        60        90   时间(秒)
```

## 高级用法

### 微调情感检测

调整config.json中的`score_threshold`来控制敏感度:
- 较高的值(如0.90)将只选择情感极强的片段
- 较低的值(如0.80)将包含更多中等情感强度的片段

### 使用自定义模型

TofuTranscribe支持使用自定义训练的模型:

1. 按照transformer模型约定训练情感检测模型
2. 更新config.json指向您的模型:
   ```json
   {
     "semantic_emotion_model": "path/to/your/custom/model"
   }
   ```

### 服务器通知

配置ServerChan集成以在处理完成时接收通知:

1. 获取ServerChan密钥
2. 将密钥添加到config.json:
   ```json
   {
     "server_chan_key": "your-server-chan-key"
   }
   ```

### 批量处理

使用简单脚本顺序处理多个视频:

```python
import os
import subprocess

video_folder = "./videos"
for video_file in os.listdir(video_folder):
    if video_file.endswith((".mp4", ".mkv", ".avi")):
        video_path = os.path.join(video_folder, video_file)
        subprocess.run(["python", "tofu_transcribe/main.py", "--input", video_path])
```

## 性能优化

### 硬件推荐

TofuTranscribe的性能根据硬件配置而异:

| 组件 | 最低要求 | 推荐配置 | 影响 |
|------|---------|---------|------|
| CPU | 4核 | 8+核 | 更快的音频处理，并行分析 |
| 内存 | 8GB | 16GB+ | 处理更大视频无需交换内存 |
| GPU | 不必须 | 支持CUDA | 模型推理速度提升5-10倍 |
| 存储 | SSD | NVMe SSD | 大型视频文件更快I/O |

### 处理时间基准

60分钟1080p视频的大致处理时间:

| 配置 | 转录 | 情感分析 | 总计 |
|------|------|---------|------|
| 仅CPU (4核) | ~45分钟 | ~30分钟 | ~75分钟 |
| 仅CPU (8核) | ~25分钟 | ~20分钟 | ~45分钟 |
| CPU + GPU (RTX 3060) | ~10分钟 | ~5分钟 | ~15分钟 |
| CPU + GPU (RTX 4090) | ~5分钟 | ~2分钟 | ~7分钟 |

### 优化技巧

1. **使用GPU加速**，在config.json中设置`"device": "cuda"`
2. **选择适当的模型大小**:
   - 快速分析: `"model": "tiny"` 或 `"model": "base"`
   - 高精度: `"model": "medium"` 或 `"model": "large"`
3. **预先转换视频**格式以优化处理
4. **将长视频拆分**为较小的片段进行并行处理

## 与其他工具集成

### 视频编辑软件

将TofuTranscribe结果导出为兼容流行视频编辑器的格式:

#### DaVinci Resolve集成

1. 用TofuTranscribe处理您的视频
2. 使用以下脚本将情感片段转换为DaVinci Resolve标记:

```python
# 将TofuTranscribe结果转换为DaVinci Resolve标记
import json

with open("work_dir/grouped_semantic_emotion_analysis_results.json") as f:
    data = json.load(f)

with open("davinci_markers.csv", "w") as f:
    f.write("Marker Name,Timecode,Color\n")
    for segment in data:
        if segment["combined_score"] > 0.85:
            start_time = segment["start_time"]
            hours = int(start_time / 3600)
            minutes = int((start_time % 3600) / 60)
            seconds = int(start_time % 60)
            frames = int((start_time % 1) * 24)  # 假设24fps
            timecode = f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"
            f.write(f"情感片段,{timecode},Blue\n")
```

### 流媒体平台

TofuTranscribe可以为以下平台自动创建亮点:

- **YouTube**: 为视频描述生成时间戳
- **Twitch**: 为频道亮点识别片段
- **Bilibili**: 从直播中创建精彩合集

## 技术深度解析

### 情感分析算法

TofuTranscribe使用多模态方法进行情感检测:

1. **基于文本的分析**:
   - 使用在情感文本数据集上微调的Transformer模型
   - 默认模型(`uer/roberta-base-finetuned-jd-binary-chinese`)专门分析中文情感
   - 从多个维度评分文本: 正/负向情感，唤醒度，支配性

2. **基于语音的分析**:
   - 使用wav2vec2模型分析声学特征
   - 检测语音音调、音高变化、语速中的情感信号
   - 捕捉转录文本中可能不明显的情感

3. **融合算法**:
   - 在时间上对齐语音和文本片段
   - 基于置信度应用加权评分
   - 使用可配置阈值识别重要情感时刻

### 模型选择逻辑

模型选择会显著影响准确性和性能:

| 模型 | 大小 | 语言 | 准确性 | 速度 |
|------|------|------|-------|------|
| Whisper Tiny | 39M | 多语言(有限) | 基础 | 最快 |
| Whisper Base | 74M | 多语言 | 良好 | 快速 |
| Whisper Small | 244M | 多语言 | 更好 | 中等 |
| Whisper Medium | 769M | 多语言 | 优秀 | 慢速 |
| Whisper Large | 1.5GB | 多语言 | 最佳 | 最慢 |

## 与类似工具比较

| 功能 | TofuTranscribe | 传统视频编辑器 | 基于ML的亮点生成器 |
|------|---------------|--------------|-------------------|
| 情感分析 | 深度多模态 | 手动 | 有限 |
| 处理速度 | 中等-快速 | 不适用(手动) | 快速 |
| 可定制性 | 高 | 高 | 低 |
| 可访问性 | 命令行和API | 图形界面 | 不同 |
| 成本 | 免费开源 | 通常付费 | 通常基于SaaS |
| 隐私 | 本地处理 | 本地处理 | 通常基于云 |

## 常见问题

### 一般问题

**问: 情感检测有多准确?**  
答: 准确性根据语言和内容类型而异。对于中文内容，使用推荐模型时，准确性通常在80-90%范围内。影响准确性的因素包括音频质量、语音清晰度和背景噪音。

**问: 我可以用于中文以外的语言吗?**  
答: 可以，通过更改语言设置和使用适当的模型。对于非中文内容，您可能需要在配置中指定不同的语义情感模型以获得最佳结果。

**问: 是否适用于任何视频格式?**  
答: TofuTranscribe使用FFmpeg进行视频处理，因此支持大多数常见视频格式(MP4、MKV、AVI等)。极不常见的格式可能需要预转换。

### 技术问题

**问: 为什么GPU内存耗尽?**  
答: 较大的Whisper模型(medium、large)需要大量GPU内存。尝试使用较小的模型或处理较短的视频片段。

**问: 可以在没有显示器的服务器上运行吗?**  
答: 是的，TofuTranscribe设计为可以在没有显示器的服务器上运行。

**问: 如何扩展情感检测到其他维度?**  
答: 您可以用自定义训练的模型替换或补充默认模型，这些模型可以检测与您的使用情况相关的特定情感维度。

## 社区与支持

### 获取帮助

- **GitHub Issues**: 通过[GitHub问题跟踪器](https://github.com/Nayutaa/TofuTranscribe/issues)报告错误或请求功能
- **讨论**: 在[GitHub讨论](https://github.com/Nayutaa/TofuTranscribe/discussions)部分参与使用和开发相关讨论

### 社区贡献

我们欢迎各类贡献:

- **代码**: 添加功能或修复错误
- **模型**: 分享针对特定语言或领域微调的模型
- **文档**: 改进指南或翻译文档
- **使用案例**: 分享您的成功案例和应用

## 致谢

TofuTranscribe基于多个杰出的开源项目:

- [Whisper](https://github.com/openai/whisper): OpenAI开发的语音识别系统
- [Transformers](https://github.com/huggingface/transformers): Hugging Face的NLP模型库
- [PyTorch](https://pytorch.org/): 深度学习框架
- [FFmpeg](https://ffmpeg.org/): 视频和音频处理工具
- [录播姬](https://github.com/BililiveRecorder/BililiveRecorder): 直播录制集成

## 许可证

本项目基于[MIT许可证](LICENSE)发布。您可以自由使用、复制、修改和分发源代码，但必须包含原始作者信息和许可声明。

---