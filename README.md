# HandDJ: Music Manipulation with Your Hands! 🎶🖐️

Use your webcam and hand gestures to control your music like a DJ! Change pitch, bass, and volume just by moving your hands.

## What You Can Do:

* **Left Hand (Pinch Closer/Wider):** Adjusts the music's PITCH.
* **Right Hand (Pinch Closer/Wider):** Adjusts the music's BASS.
* **Both Hands (Move Closer/Further Apart):** Adjusts the music's VOLUME.
* **Keyboard:**
    * `Spacebar`: Play or Pause music.
    * `r`: Reset pitch, bass, and volume to default.
    * `q`: Quit the program.

## How It Works:

Your webcam watches your hands. The program sees your gestures (like pinching) and uses them to tell the `AudioManipulationModule.py` how to change the music's sound in real-time.

## Get Started:

### What You Need:

1.  **Python 3.7+**
2.  **A Webcam**
3.  **FFmpeg:** This is important for playing different audio files (like MP3s).
    * Download from [FFmpeg's official site](https://ffmpeg.org/download.html) and add it to your system's PATH. (Search online for "how to add ffmpeg to PATH" for your operating system).

### Steps:

1.  **Download Files:** Get `HandDJ.py`, `AudioManipulationModule.py`, and `HandTrackingModule.py` and put them in a folder.
2.  **Open Terminal/Command Prompt:** Navigate to that folder.
3.  **Install Software:**
    ```bash
    pip install opencv-python mediapipe numpy pygame pydub
    ```
4.  **Add Music:** Put an MP3 (or WAV) audio file in the same folder.
    * The program will try to play files named "owa.mp3", "test\_audio.wav", "audio.mp3", or "music.mp3" first. You can edit `HandDJ.py` to use your specific file name if needed.

### How To Run:

```bash
python HandDJ.py
