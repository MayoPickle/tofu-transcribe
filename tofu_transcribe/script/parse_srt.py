import pysrt

def parse_srt(file_path):
    """解析 SRT 文件"""
    subs = pysrt.open(file_path, encoding='utf-8')
    return [(sub.start.ordinal // 1000, sub.end.ordinal // 1000, sub.text) for sub in subs]

