from setuptools import setup, find_packages

setup(
    name="tofu-transcribe",
    version="0.0.1",
    description="A tool for transcribing videos into scripts using FFmpeg and Whisper.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="nayutaa",
    author_email="me@noir.run",
    url="https://github.com/nayutaa/TofuTranscribe",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask",
        "waitress"
    ],
    entry_points={
        "console_scripts": [
            "tofu-transcribe=tofu_transcribe.main:MainApp.main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
