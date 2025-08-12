from PyQt5.QtWidgets import (
    QLabel, QPushButton, QLineEdit, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from tracking.dj_controller import DJController
from audio.youtube_audio import YouTubeAudio
from gui.styles import *
from gui.base_page import BasePage
import os

class PlayPage(BasePage):
    # This is the play page where the user can input a YouTube link and the run HandDJ
    def __init__(self, on_back_callback, on_play_callback=None):
        super().__init__(on_back_callback, "Play")
        self.on_play_callback = on_play_callback
        self.current_dj_controller = None

    def setup_content(self, layout):
        # Sets up content for the page
        instructions = self.create_instructions_label()
        self.youtube_link_input = self.create_youtube_link_input()
        run_btn = self.create_run_button()

        layout.insertWidget(1, instructions)
        layout.insertWidget(2, self.youtube_link_input)
        layout.insertWidget(3, run_btn)

    def create_instructions_label(self):
        # Creates label for instructions
        instructions = QLabel("Insert YouTube Link")
        instructions.setFont(QFont("Arial", SUBTITLE_FONT_SIZE))
        instructions.setAlignment(Qt.AlignCenter)
        return instructions

    def create_youtube_link_input(self):
        # Creates input field to insert YouTube link
        link_input = QLineEdit()
        link_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        link_input.setFont(QFont("Arial", INPUT_FONT_SIZE))
        link_input.setStyleSheet(INPUT_STYLE)
        return link_input

    def create_run_button(self):
        # Creates button to run HandDJ
        run_btn = QPushButton("Run")
        run_btn.setFont(QFont("Arial", BUTTON_FONT_SIZE))
        run_btn.setStyleSheet(BUTTON_STYLE)
        run_btn.clicked.connect(self.run_hand_dj)
        return run_btn

    def run_hand_dj(self):
        # Retrieves YouTube link, process audio, and starts overlay
        youtube_url = self.youtube_link_input.text().strip()
        if not youtube_url:
            QMessageBox.warning(self, "Error", "Please enter a YouTube link.")
            return
        try:
            self.process_youtube_audio(youtube_url)
        except Exception as error:
            QMessageBox.critical(self, "Error", f"Error starting HandDJ: {error}")

    def process_youtube_audio(self, youtube_url):
        # Fetches audio, creates temporary wav audio file, starts overlay
        audio_fetcher = YouTubeAudio(sample_rate=44100)
        audio_data = audio_fetcher.fetch(youtube_url)
        
        # Get the video title
        if audio_fetcher.video_title:
            video_title = audio_fetcher.video_title
        else:
            video_title = "Unknown Song"

        temp_audio_file = "youtube_audio.wav"
        audio_data.export(temp_audio_file, format="wav")

        try:
            self.current_dj_controller = DJController(audio_file=temp_audio_file)
            # Pass the video title and dj_controller to the callback if available
            if self.on_play_callback:
                self.on_play_callback(video_title, self.current_dj_controller)
            self.current_dj_controller.run()
        finally:
            self.cleanup_temp_file(temp_audio_file)

    def cleanup_temp_file(self, file_path):
        # Cleans up the temporary wav audio file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
