# Lecture Transcriber

Creates transcriptions of sound files using a variety of platforms.

Currently supports:
* Vosk (off-line model)
* Azure Speech-to-Text

Additionally, this project has additional tooling using [ffmpeg](https://www.ffmpeg.org/) to convert video and audio files into formats accepted by the models.

This project was initially created to solve a number of problems:
* Lectures are often-times long and boring, while text can be skimmed to quickly extract relevant information
* Lectures cannot be searched like text, making it difficult to move between topics to learn or revise a certain topic
* It's often difficult to know what's important in the middle of a lecture, and transcripts let you come back to where the topic was first covered

By having transcriptions for lectures ready, content can be learned faster, revision can be made simpler, and lectures can be broken down from multi-hour seminars into the bite-sized chunks relevant to a specific topic a student needs to learn and revise.

# Requirements

Create a python virtual environment and install the required packages:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# Usage

**For online models**
* Create an account on the relevant portal and save API keys in the provided .env_example file. Then rename the file to .env

**For vosk models**
* Install a model from [vosk](https://alphacephei.com/vosk/models) and unpack it in a folder called "model"

Set up environment variables as specified in .env_example
Run lecture_transcriber.py with the following:

```bash
python3 lecture_transcriber.py
```

# Note

Note this project is for long running audio processing with the main purpose of extracting and summarising speech from a long (longer than 60 seconds) sound recording.
