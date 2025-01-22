def extract_highest_groups(grouped_times, grouped_scores, group_texts):
    """提取正情绪和负情绪最高分的分组"""
    max_positive_score = -1
    max_negative_score = -1

    positive_highest = None
    negative_highest = None

    for i, score in enumerate(grouped_scores):
        if score > max_positive_score:
            max_positive_score = score
            positive_highest = (grouped_times[i], grouped_scores[i], group_texts[i])

        if score > max_negative_score:
            max_negative_score = score
            negative_highest = (grouped_times[i], grouped_scores[i], group_texts[i])

    return positive_highest, negative_highest
