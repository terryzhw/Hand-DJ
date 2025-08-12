<h1 align="center">
  <br>
  HandDJ
  <br>
  ![Imgur](https://imgur.com/bbJzZeZ.gif)
  <br>
</h1>

<h4 align="center">A gesture-controlled DJ application built using <a href="https://mediapipe.dev/" target="_blank">MediaPipe</a>.</h4>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#installation">Installation</a> •
  <a href="#controls">Controls</a> •
  <a href="#credits">Credits</a> •
  <a href="#license">License</a>
</p>

## Key Features

* Real-time Hand Tracking - Control your music with natural hand gestures
  - Uses MediaPipe for accurate hand detection and landmark tracking
* Audio Effects Control
  - Pitch manipulation with smooth transitions
  - Volume control through hand positioning
  - Reverb effects for enhanced sound quality
* Interactive GUI
  - Clean, modern interface with multiple control pages
  - Visual feedback for hand tracking and audio parameters
  - Easy navigation between different application modes
* Audio Processing
  - Real-time audio manipulation and effects
  - Support for various audio file formats
  - Smooth parameter transitions to prevent audio artifacts
* Cross Platform
  - Works on Windows and macOS
  - Optimized for different operating system requirements

## How To Use

To clone and run this application, you'll need [Git](https://git-scm.com) and [Python 3.10](https://python.org) installed on your computer. From your command line:

```bash
# Clone this repository
$ git clone https://github.com/terryzhw/hand-recognition

# Go into the repository
$ cd hand-recognition

# Install dependencies (macOS)
$ pip install -r mac_requirements.txt

# Install dependencies (Windows)
$ pip install -r win_requirements.txt

# Go to app 
$ cd app

# Run the application
$ python hand_dj.py
```

> **Note**
> Make sure your camera is connected and accessible before running the application.

## Controls

HandDJ uses computer vision to track your hand movements and translate them into audio controls:

* **Pitch Control** - Move your hand up and down to adjust the pitch of the audio
* **Volume Control** - Control audio volume through hand positioning
* **Reverb Effects** - Add reverb effects using specific hand gestures
* **Real-time Feedback** - Visual indicators show current parameter values

Navigate through the application using the GUI:
- **Main Page** - Start here to access all features
- **Instructions Page** - Learn how to use hand controls
- **Play Page** - Load and control your audio files
- **Control Page** - Monitor real-time audio parameters and hand tracking

## Installation

### Prerequisites

- Python 3.10 (I use 3.10.11)

### Dependencies

The application requires several Python packages for computer vision, audio processing, and GUI:

- **MediaPipe** - Hand tracking and computer vision
- **OpenCV** - Image processing and camera interface
- **PyQt5** - Desktop application framework
- **Audio processing libraries** - For real-time audio manipulation

Use the provided requirements files for your operating system to ensure compatibility.

## Credits

This software uses the following open source packages:

- [MediaPipe](https://mediapipe.dev/) - Google's framework for building perception pipelines
- [OpenCV](https://opencv.org/) - Computer vision and image processing
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - Python bindings for Qt application framework
- [Python](https://python.org/) - Programming language and runtime

For the reverb, I learned a lot from this: http://sites.music.columbia.edu/cmc/MusicAndComputers/chapter5/05_02.php

## Support

If you encounter any issues or have questions about HandDJ, please open an issue on the GitHub repository.

## License

MIT

---

> Developed by Terrance Wong
