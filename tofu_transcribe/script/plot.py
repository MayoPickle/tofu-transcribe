import matplotlib.pyplot as plt


class EmotionTrendPlotter:
    """A utility class to plot emotion trends."""

    @staticmethod
    def plot_emotion_trends(
        times,
        scores,
        labels=None,
        positive_group=None,
        negative_group=None,
        output_file="emotion_trend.png",
    ):
        """
        Plot emotion trends with times and scores.
        :param times: List of time intervals for each group
        :param scores: List of emotion scores for each group
        :param labels: Not used in simplified version
        :param positive_group: Not used in simplified version
        :param negative_group: Not used in simplified version
        :param output_file: Path to save the plot
        """
        # Start plotting
        plt.figure(figsize=(12, 6))
        plt.plot(range(len(times)), scores, marker="o", linestyle="-", label="Emotion Score")

        # Add time intervals as x-axis labels
        plt.xticks(range(len(times)), [f"{start}-{end}s" for start, end in times], rotation=45)

        plt.title("Emotion Trends Across Time")
        plt.xlabel("Time Intervals")
        plt.ylabel("Emotion Score")
        plt.grid()

        # Save and show the plot
        plt.tight_layout()
        plt.savefig(output_file)
        print(f"Emotion Trend saved to: {output_file}")
        plt.show()
