# TofuTranscribe

TofuTranscribe 是一个使用多种机器学习模型从视频中分析情绪、筛选最佳片段，并自动生成短视频的项目。它从多个维度对视频中的情绪进行建模和评估，帮助用户快速提炼出最有价值的精彩部分。目前支持通过手动输入以及 [录播姬](https://github.com/BililiveRecorder/BililiveRecorder) 的 Webhook 来输入视频信息或素材。

## 功能特性

- **多维度情绪分析**  
  - 集成多种机器学习模型，从情绪、音频特征、文本等角度对视频进行分析。  
  - 根据分析结果筛选出视频中最具吸引力或最具冲击力的片段。

- **自动视频分割与生成**  
  - 分析长视频内容，自动切分并输出多个短视频。  
  - 支持自定义切分规则，例如基于时长、情绪分数。

- **文本与字幕处理**  
  - 可根据音频中的语音识别或现有的字幕文件进行自动提取和处理。  

- **多输入源**  
  - **录播姬 Webhook**：自动接收直播录制完成后的视频信息，快速处理生成短视频。  
  - **手动输入**：可在命令行或脚本内指定本地视频文件，灵活处理不同场景下的视频资源。

## 环境要求

- Python 3.9 及以上
- FFmpeg（用于视频编解码及处理）
- PyTorch（用于深度学习模型的情绪分析、语音识别等）
- 其他依赖可在 `requirements.txt` 中查看

## 安装

1. 克隆本项目到本地：
   ```bash
   git clone https://github.com/Nayutaa/TofuTranscribe
   ```
2. 进入项目目录并安装依赖：
   ```bash
   cd TofuTranscribe
   pip install -r requirements.txt
   ```

## 快速开始

### 1. 通过录播姬 Webhook

1. 在 `config.json` 或其他配置文件中填写 Webhook 的监听端口或地址。  
2. 确保在录播姬中配置好该 Webhook，使录制完成后自动向 TofuTranscribe 发送视频信息。  
3. 启动项目，监听来自录播姬的 HTTP 请求，一旦收到视频文件信息，就会自动进行解析和处理。

### 2. 手动输入视频文件

1. 准备一个视频文件。  
2. 运行脚本示例：
   ```bash
   python main.py \
       --input demo.mp4 \

   ```
   - `--input`: 指定输入视频的路径或文件夹  


3. 等待程序运行完成后，即可在 `demo/` 文件夹查看自动生成的文件

## 参数说明

在运行 `TofuTranscribe.py` 时，可以使用以下可选参数，根据需求对生成短视频的流程进行自定义。

| 参数                        | 默认值         | 说明                                                         |
|----------------------------|---------------|-------------------------------------------------------------|
| `--input_path`             | 无            | 输入视频文件路径或文件夹                                      |
| `--enable_emotion_analysis`| `False`       | 是否启用多维度情绪分析模型                                     |

## 许可证

本项目基于 [MIT License](LICENSE) 开源。你可以自由地使用、复制、修改和分发本项目的源代码，但需要保留原作者信息及许可证声明。

---