import os
import torch
import srt
import json
from pydub import AudioSegment
from tqdm import tqdm
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForSequenceClassification


class SpeechEmotionAnalyzer:
    def __init__(self, work_dir, model_name):
        """
        Initialize the audio and SRT files, as well as the emotion analysis model.
        Automatically detects files with .wav and .srt extensions in the given directory.
        :param work_dir: Working directory containing the audio and SRT files
        :param model_name: Hugging Face model name
        """
        self.work_dir = work_dir
        self.model_name = model_name

        # Automatically find .wav and .srt files in the directory
        self.audio_path = self._find_file(extension=".wav")
        self.srt_path = self._find_file(extension=".srt")
        self.output_srt_path = os.path.join(work_dir, "script_with_speech_emotion_analysis_results.srt")
        self.output_json_path = os.path.join(work_dir, "speech_emotion_analysis_results.json")

        # Load audio and SRT files
        self.audio = AudioSegment.from_file(self.audio_path)
        with open(self.srt_path, "r", encoding="utf-8") as file:
            self.srt_content = file.read()
        self.subtitles = list(srt.parse(self.srt_content))

        # Load the model and feature extractor
        self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
        self.model = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)
        
        # Handle gradient_checkpointing if it exists in the config
        if hasattr(self.model.config, "gradient_checkpointing") and self.model.config.gradient_checkpointing:
            # Use the new recommended method instead
            self.model.gradient_checkpointing_enable()
            
        self.id2label = self.model.config.id2label

    def _find_file(self, extension):
        """
        Find a file with the given extension in the working directory.
        :param extension: File extension to search for (e.g., ".wav", ".srt")
        :return: Full path to the file
        :raises FileNotFoundError: If no file with the given extension is found
        """
        files = [f for f in os.listdir(self.work_dir) if f.endswith(extension)]
        if not files:
            raise FileNotFoundError(f"No file with extension {extension} found in {self.work_dir}")
        if len(files) > 1:
            raise ValueError(f"Multiple files with extension {extension} found in {self.work_dir}: {files}")
        return os.path.join(self.work_dir, files[0])

    @staticmethod
    def timestamp_to_milliseconds(timestamp):
        """
        Convert timestamp to milliseconds.
        :param timestamp: datetime.timedelta object
        :return: Millisecond representation of the timestamp
        """
        return int(timestamp.total_seconds() * 1000)

    def analyze_emotion(self, audio_segment):
        """
        Perform emotion analysis on an audio segment.
        :param audio_segment: pydub.AudioSegment object
        :return: (Top emotion label, all emotion scores)
        """
        # Check if audio segment is too short
        if len(audio_segment) < 200:  # Less than 200ms is likely too short
            # Return a default or "unknown" emotion for segments that are too short
            return "neutral", [("neutral", 1.0), ("happy", 0.0), ("sad", 0.0), ("angry", 0.0), ("fearful", 0.0), ("disgust", 0.0), ("surprised", 0.0)]
        
        try:
            samples = audio_segment.get_array_of_samples()
            # Ensure the sample is long enough for the CNN kernel
            if len(samples) < 5:  # A minimum threshold to avoid kernel size error
                return "neutral", [("neutral", 1.0), ("happy", 0.0), ("sad", 0.0), ("angry", 0.0), ("fearful", 0.0), ("disgust", 0.0), ("surprised", 0.0)]
            
            inputs = self.feature_extractor(
                list(samples),
                sampling_rate=self.audio.frame_rate,
                return_tensors="pt",
                padding=True
            )
            inputs["input_values"] = inputs["input_values"].to(torch.float32)

            with torch.no_grad():
                logits = self.model(**inputs).logits
                scores = torch.softmax(logits, dim=-1)

            emotion_scores = sorted(
                [(self.id2label[i], score.item()) for i, score in enumerate(scores[0])],
                key=lambda x: x[1],
                reverse=True
            )
            top_emotion_label = emotion_scores[0][0]
            return top_emotion_label, emotion_scores
            
        except RuntimeError as e:
            # Handle the specific error about kernel size
            if "Kernel size can't be greater than actual input size" in str(e):
                return "neutral", [("neutral", 1.0), ("happy", 0.0), ("sad", 0.0), ("angry", 0.0), ("fearful", 0.0), ("disgust", 0.0), ("surprised", 0.0)]
            else:
                # Re-raise other runtime errors
                raise

    def process_and_save(self):
        """
        Process each subtitle in the SRT file and save a new SRT file with emotion scores and a JSON file.
        """
        new_subtitles = []
        results = []  # To store JSON data

        # Process bar
        for subtitle in tqdm(self.subtitles, desc="Analyzing subtitles", total=len(self.subtitles)):
            start_time = self.timestamp_to_milliseconds(subtitle.start)
            end_time = self.timestamp_to_milliseconds(subtitle.end)
            audio_segment = self.audio[start_time:end_time]

            top_emotion_label, emotion_scores = self.analyze_emotion(audio_segment)

            # Prepare data for JSON
            results.append({
                "index": subtitle.index,
                "start": str(subtitle.start),
                "end": str(subtitle.end),
                "text": subtitle.content,
                "score": emotion_scores[0][1],
                "top_emotion": top_emotion_label,
                "emotion_scores": {label: score for label, score in emotion_scores}
            })

            # Update SRT content
            emotion_scores_text = ", ".join([f"{label}: {score:.2f}" for label, score in emotion_scores])
            new_content = f"[{top_emotion_label}: {emotion_scores}] {subtitle.content} + ({emotion_scores_text})"
            new_subtitle = srt.Subtitle(
                index=subtitle.index,
                start=subtitle.start,
                end=subtitle.end,
                content=new_content
            )
            new_subtitles.append(new_subtitle)

        # Save updated SRT file
        with open(self.output_srt_path, "w", encoding="utf-8") as file:
            file.write(srt.compose(new_subtitles))

        # Save JSON results
        with open(self.output_json_path, "w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=4)

        print(f"Updated SRT file saved to {self.output_srt_path}")
        print(f"Emotion analysis results saved to {self.output_json_path}")
