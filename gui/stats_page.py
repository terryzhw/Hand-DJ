from PyQt5.QtWidgets import (
    QVBoxLayout, QLabel, QWidget, QPushButton, 
    QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer
from gui.base_page import BasePage
from gui.styles import BUTTON_FONT_SIZE, BUTTON_STYLE, SUBTITLE_FONT_SIZE
class StatsPage(BasePage):
 
    def __init__(self, on_back_callback, overlay=None, audio_file_name=None):
        self.overlay = overlay
        self.audio_file_name = audio_file_name or "Unknown Song"
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(100) # in ms
        super().__init__(on_back_callback, "HandDJ Statistics")

    def create_base_page(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        title = self.create_title_label()
        self.main_layout.addWidget(title)
        self.main_layout.addStretch()

        self.setup_content(self.main_layout)

        self.main_layout.addStretch()

        self.setLayout(self.main_layout)

    def setup_content(self, layout):

        song_info = self.create_song_info_widget()
        stats = self.create_stats_widget()
        controls = self.create_controls_widget()
        
        layout.insertWidget(1, song_info)
        layout.insertWidget(2, stats)
        layout.insertWidget(3, controls)

    def create_stats_widget(self):

        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        self.stats_label = self.create_stats_label()
        layout.addWidget(self.stats_label)

        widget.setLayout(layout)
        return widget

    def create_stats_label(self):

        stats_text = self.generate_stats_text()
        stats_label = QLabel(stats_text)
        stats_label.setFont(QFont("Arial", 12))
        stats_label.setWordWrap(True)
        stats_label.setStyleSheet("color: white; padding: 10px;")
        return stats_label

    def generate_stats_text(self):

        if self.overlay and hasattr(self.overlay, 'get_stats'):
            try:
                stats = self.overlay.get_stats()
                return self.format_live_stats(stats)
            except Exception as e:
                return f"<h2>Error Getting Stats</h2><p>Error: {str(e)}</p>"
        else:
            return """
            <h2>🎵 Waiting for Audio...</h2>
            <p style='color: #90CAF9; text-align: center; font-style: italic;'>
                Please start playing a song to see real-time statistics.
            </p>
            <p style='color: #757575; text-align: center; font-size: 12px;'>
                Go to Play page → Enter YouTube URL → Run HandDJ
            </p>
            """

    def format_live_stats(self, stats):

        pitch_val = f"{stats['pitch']:.2f}"
        reverb_val = f"{stats['reverb']:.2f}"
        volume_val = f"{stats['volume']:.2f}"
        volume_percent = f"{stats['volume'] * 100:.0f}%"
        
        return f"""
        <h2>🎵 Current Audio Statistics</h2>
        <table style="width: 100%; color: white; border-spacing: 10px;">
            <tr>
                <td style="width: 50%;"><b>Pitch:</b></td>
                <td style="color: #4CAF50;">{pitch_val}x</td>
            </tr>
            <tr>
                <td><b>Volume:</b></td>
                <td style="color: #2196F3;">{volume_val} ({volume_percent})</td>
            </tr>
            <tr>
                <td><b>Reverb:</b></td>
                <td style="color: #FF9800;">{reverb_val}</td>
            </tr>
        </table>
    
        """

    def get_playback_info(self):

        if hasattr(self.overlay, 'audio_controller'):
            if hasattr(self.overlay.audio_controller, 'audio_loaded') and self.overlay.audio_controller.audio_loaded:
                is_playing = getattr(self.overlay.audio_controller.audio_processor, 'is_playing', False)
                status = "Playing" if is_playing else "Paused"
                color = "#4CAF50" if is_playing else "#FF5722"
                return f"""
            <tr>
                <td><b>Status:</b></td>
                <td style="color: {color};">{status}</td>
            </tr>"""
        return """
            <tr>
                <td><b>Status:</b></td>
                <td style="color: #757575;">No Audio Loaded</td>
            </tr>"""

    def create_song_info_widget(self):

        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        

        self.song_title_label = QLabel(f"♪ {self.audio_file_name}")
        self.song_title_label.setFont(QFont("Arial", SUBTITLE_FONT_SIZE, QFont.Bold))
        self.song_title_label.setAlignment(Qt.AlignCenter)
        self.song_title_label.setStyleSheet("color: #4CAF50; padding: 5px;")
        
        layout.addWidget(self.song_title_label)
        
        widget.setLayout(layout)
        return widget

    def create_controls_widget(self):

        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        

        self.reset_button = QPushButton("Reset")
        self.reset_button.setFont(QFont("Arial", BUTTON_FONT_SIZE))
        self.reset_button.setStyleSheet(BUTTON_STYLE)
        self.reset_button.clicked.connect(self.reset_audio_params)
        

        self.toggle_button = QPushButton("Play/Pause")
        self.toggle_button.setFont(QFont("Arial", BUTTON_FONT_SIZE))
        self.toggle_button.setStyleSheet(BUTTON_STYLE)
        self.toggle_button.clicked.connect(self.toggle_playback)
        

        self.quit_button = QPushButton("Quit")
        self.quit_button.setFont(QFont("Arial", BUTTON_FONT_SIZE))
        self.quit_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f44336;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        self.quit_button.clicked.connect(self.quit_handdj)
        
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.toggle_button)
        buttons_layout.addWidget(self.quit_button)

        
        layout.addLayout(buttons_layout)
        
        widget.setLayout(layout)
        return widget

    def update_stats(self):
        # Update statistics display in real-time
        if hasattr(self, 'stats_label'):
            stats_text = self.generate_stats_text()
            self.stats_label.setText(stats_text)



    def reset_audio_params(self):
        # Reset audio parameters to defaults
        try:
            if self.overlay and hasattr(self.overlay, 'audio_controller'):
                self.overlay.audio_controller.reset_parameters()
                QMessageBox.information(self, "Reset", "Audio parameters reset to default values!")
            else:
                QMessageBox.warning(self, "Reset", "No audio controller available. Please start playing audio first.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset parameters: {str(e)}")

    def toggle_playback(self):
        # Toggle play/pause state
        try:
            if self.overlay and hasattr(self.overlay, 'audio_controller'):
                self.overlay.audio_controller.toggle_playback()
            else:
                QMessageBox.warning(self, "Playback", "No audio controller available. Please start playing audio first.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to toggle playback: {str(e)}")

    def quit_handdj(self):
    
        reply = QMessageBox.question(
            self, 
            "Quit", 
            "Are you sure you want to quit",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.overlay and hasattr(self.overlay, 'cleanup'):
                    self.overlay.cleanup()
            except Exception:
                pass  
            
   
            try:
                import os
                temp_audio_file = "youtube_audio.wav"
                if os.path.exists(temp_audio_file):
                    os.remove(temp_audio_file)
            except Exception:
                pass 
            
     
            import sys
            sys.exit(0)

    def closeEvent(self, event):

        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
        super().closeEvent(event)
