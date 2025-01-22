import json
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


def group_and_average(
    subtitles, 
    group_size=64, 
    step=4, 
    model_name="uer/roberta-base-finetuned-jd-binary-chinese", 
    max_length=512, 
    output_json_path="grouped_emotion_results.json"
):
    """
    Group subtitles using a sliding window and perform sentiment analysis on each group.
    Save the results as a JSON file.
    :param subtitles: List of subtitles (start, end, text).
    :param group_size: Number of subtitles in each group.
    :param step: Step size for sliding window.
    :param model_name: Sentiment analysis model name.
    :param max_length: Maximum token length for each group.
    :param output_json_path: Path to save grouped emotion results as JSON.
    :return: grouped_times, grouped_scores, group_texts, group_labels
    """
    classifier = pipeline("sentiment-analysis", model=model_name, tokenizer=model_name)
    grouped_scores = []
    grouped_times = []
    group_texts = []
    group_labels = []
    results = []  # To store results for JSON

    for i in range(0, len(subtitles) - group_size + 1, step):
        group = subtitles[i:i + group_size]

        # Combine group subtitles into a single text, truncate if necessary
        combined_text = " ".join(text for _, _, text in group)
        while len(combined_text) > max_length and len(group) > 1:
            group = group[:-1]
            combined_text = " ".join(text for _, _, text in group)

        if len(combined_text) > max_length:
            print(f"Skipping group starting at subtitle {i+1} due to excessive length.")
            continue

        avg_time = sum((start + end) / 2 for start, end, _ in group) / len(group)

        # Perform emotion analysis
        emotion = classifier(combined_text)[0]

        grouped_scores.append(emotion['score'])
        grouped_times.append((group[0][0], group[-1][1]))
        group_texts.append(combined_text)
        group_labels.append(emotion['label'])

        # Store results for JSON
        results.append({
            "group_index": len(grouped_scores),
            "group_size": len(group),  # Include the size of the group
            "time_range": {"start": group[0][0], "end": group[-1][1]},
            "average_time": avg_time,
            "combined_text": combined_text,
            "top_emotion": {
                "label": emotion['label'],
                "score": emotion['score']
            }
        })

        # Debugging info
        print(f"Group {len(grouped_scores)}:")
        print(f"  Time Range: {grouped_times[-1][0]}s - {grouped_times[-1][1]}s")
        print(f"  Emotion Label: {emotion['label']}")
        print(f"  Emotion Score: {emotion['score']:.4f}")
        print(f"  Combined Text: {combined_text}\n")

    # Save results to JSON
    with open(output_json_path, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=4)
    print(f"Grouped emotion results saved to {output_json_path}")

    return grouped_times, grouped_scores, group_texts, group_labels



def group_by_individual_scores(individual_results, group_size=64, step=4):
    """基于单句情绪分析结果进行分组"""
    grouped_scores = []
    grouped_times = []
    grouped_texts = []

    for i in range(0, len(individual_results) - group_size + 1, step):
        group = individual_results[i:i + group_size]

        group_score = sum(result['score'] for result in group) / group_size
        group_start = group[0]['start']
        group_end = group[-1]['end']
        group_text = " ".join(result['text'] for result in group)

        grouped_scores.append(group_score)
        grouped_times.append((group_start, group_end))
        grouped_texts.append(group_text)

        print(f"Group {len(grouped_scores)}:")
        print(f"  Time Range: {group_start}s - {group_end}s")
        print(f"  Normalized Group Score: {group_score:.4f}")
        print(f"  Group Text: {group_text[:100]}...\n")

    return grouped_times, grouped_scores, grouped_texts
