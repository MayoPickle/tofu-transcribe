from transformers import pipeline

def analyze_individual_sentences(subtitles, model_name="uer/roberta-base-finetuned-jd-binary-chinese"):
    """对每条字幕单独进行情绪分析"""
    classifier = pipeline("sentiment-analysis", model=model_name, tokenizer=model_name)
    individual_results = []

    for start, end, text in subtitles:
        emotion = classifier(text)[0]  # 对单句分析
        individual_results.append({
            "start": start,
            "end": end,
            "text": text,
            "label": emotion['label'],
            "score": emotion['score']
        })

    return individual_results


def group_and_average(subtitles, group_size=64, step=4, model_name="uer/roberta-base-finetuned-jd-binary-chinese", max_length=512):
    """将字幕按滑动窗口分组，整组推理情绪，按句子裁剪超长组"""
    classifier = pipeline("sentiment-analysis", model=model_name, tokenizer=model_name)
    grouped_scores = []
    grouped_times = []
    group_texts = []
    group_labels = []  # 记录每组的情绪标签

    for i in range(0, len(subtitles) - group_size + 1, step):
        group = subtitles[i:i + group_size]

        # 合并组内字幕为一个文本，按句子逐步裁剪
        combined_text = " ".join(text for _, _, text in group)
        while len(combined_text) > max_length and len(group) > 1:
            group = group[:-1]  # 移除最后一句
            combined_text = " ".join(text for _, _, text in group)

        # 如果裁剪到只剩一条字幕仍超出长度，直接跳过
        if len(combined_text) > max_length:
            print(f"Skipping group starting at subtitle {i+1} due to excessive length.")
            continue

        avg_time = sum((start + end) / 2 for start, end, _ in group) / len(group)

        # 整组推理情绪
        emotion = classifier(combined_text)[0]

        grouped_scores.append(emotion['score'])
        grouped_times.append((group[0][0], group[-1][1]))
        group_texts.append(combined_text)
        group_labels.append(emotion['label'])  # 保存情绪标签

        # 打印调试信息
        print(f"Group {len(grouped_scores)}:")
        print(f"  Time Range: {grouped_times[-1][0]}s - {grouped_times[-1][1]}s")
        print(f"  Emotion Label: {emotion['label']}")
        print(f"  Emotion Score: {emotion['score']:.4f}")
        print(f"  Combined Text: {combined_text}\n")

    return grouped_times, grouped_scores, group_texts, group_labels


def group_by_individual_scores(individual_results, group_size=64, step=4):
    """基于单句情绪分析结果进行分组"""
    grouped_scores = []
    grouped_times = []
    grouped_texts = []

    for i in range(0, len(individual_results) - group_size + 1, step):
        group = individual_results[i:i + group_size]

        # 计算组的总得分（简单加和）
        group_score = sum(result['score'] for result in group)
        group_start = group[0]['start']
        group_end = group[-1]['end']
        group_text = " ".join(result['text'] for result in group)

        grouped_scores.append(group_score)
        grouped_times.append((group_start, group_end))
        grouped_texts.append(group_text)

        # 打印调试信息
        print(f"Group {len(grouped_scores)}:")
        print(f"  Time Range: {group_start}s - {group_end}s")
        print(f"  Group Score (Sum of Individual Scores): {group_score:.4f}")
        print(f"  Group Text: {group_text[:100]}...\n")  # 打印前100字符避免过长

    return grouped_times, grouped_scores, grouped_texts
