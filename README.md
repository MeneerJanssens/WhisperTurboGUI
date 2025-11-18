# Whisper Turbo Transcription

A modern, easy-to-use desktop app for fast audio transcription using OpenAI Whisper Turbo, with GPU/CPU selection, progress bar, and a beautiful Tkinter interface.

## Features
- Transcribe audio files (mp3, wav, m4a, ogg, flac, webm, mp4, etc.)
- Modern, dark-themed GUI with progress bar
- GPU/CPU device selection (auto-detects CUDA)
- Copy and export transcription
- Chunked processing for large files
- Error handling and user feedback

## Requirements
- Python 3.8–3.11 (Python 3.13+ may not be fully supported by all dependencies)
- [ffmpeg](https://ffmpeg.org/) (must be in your PATH)
- pip packages: `openai-whisper`, `torch`, `soundfile`, `tkinter` (usually included with Python)

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/yourusername/whisper-turbo-app.git
   cd whisper-turbo-app
   ```
2. Install dependencies:
   ```sh
   pip install openai-whisper torch soundfile
   ```
3. (Optional) Install ffmpeg if not already installed.

## Usage
Run the app with:
```sh
python WhisperTurboGUI.py
```

### Export as Windows .exe
1. Install PyInstaller:
   ```sh
   pip install pyinstaller
   ```
2. Build the executable:
   ```sh
   pyinstaller --onefile --noconsole WhisperTurboGUI.py
   ```
3. Find your `.exe` in the `dist` folder.

## Screenshots
![App Screenshot](screenshot.png)

## License
MIT

## Credits
- [OpenAI Whisper](https://github.com/openai/whisper)
- [PyTorch](https://pytorch.org/)
- [Tkinter](https://docs.python.org/3/library/tkinter.html)

---
Feel free to open issues or pull requests to improve this app!
