import matplotlib.pyplot as plt

def plot_emotion_trends(times, scores, labels, positive_group, negative_group, output_file="emotion_trend.png"):
    """绘制每个分组的情绪得分，并标注最高和最低分的分组"""
    plt.figure(figsize=(12, 6))
    plt.plot(range(len(times)), scores, marker='o', linestyle='-', label='Emotion Score')

    # 标注最高 Positive 分组
    if positive_group:
        pos_index = times.index(positive_group[0])
        plt.scatter([pos_index], [positive_group[1]], color='green', label='Highest Positive')
        plt.text(
            pos_index, positive_group[1],
            f"Positive\nScore: {positive_group[1]:.4f}\nTime: {positive_group[0][0]}s-{positive_group[0][1]}s",
            color='green', fontsize=8, ha='center'
        )

    # 标注最高 Negative 分组
    if negative_group:
        neg_index = times.index(negative_group[0])
        plt.scatter([neg_index], [negative_group[1]], color='red', label='Highest Negative')
        plt.text(
            neg_index, negative_group[1],
            f"Negative\nScore: {negative_group[1]:.4f}\nTime: {negative_group[0][0]}s-{negative_group[0][1]}s",
            color='red', fontsize=8, ha='center'
        )

    # 显示每个分组的情绪标签
    for i, (x, y) in enumerate(zip(range(len(times)), scores)):
        plt.text(x, y, labels[i], fontsize=8, ha='center', alpha=0.7)

    plt.title("Emotion Trends Across Groups")
    plt.xlabel("Group Index")
    plt.ylabel("Emotion Score")
    plt.legend()
    plt.grid()
    
    # 保存图片
    plt.savefig(output_file)
    print(f"Emotion Trend saved to: {output_file}")
    plt.show()
