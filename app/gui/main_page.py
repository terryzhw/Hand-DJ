from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from gui.styles import BUTTON_FONT_SIZE, BUTTON_STYLE

class MainPage(QWidget):
    # This is the main menu page of HandDJ
    def __init__(self, on_play_callback, on_instructions_callback):
        super().__init__()
        self.on_play_callback = on_play_callback
        self.on_instructions_callback = on_instructions_callback

        self.create_main_page()

    def create_main_page(self):
        # Creates layout for main menu page
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = self.create_title_label()
        play_btn = self.create_play_button()
        instructions_btn = self.create_instructions_button()

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(play_btn)
        layout.addWidget(instructions_btn)
        layout.addStretch()

        self.setLayout(layout)

    def create_title_label(self):
        # Create title label
        title = QLabel("Menu")
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        return title

    def create_play_button(self):
        # Create play button
        play_btn = QPushButton("Play")
        play_btn.setFont(QFont("Arial", BUTTON_FONT_SIZE))
        play_btn.setStyleSheet(BUTTON_STYLE)
        play_btn.clicked.connect(self.on_play_callback)
        return play_btn

    def create_instructions_button(self):
        # Create instruction button
        instructions_btn = QPushButton("Instructions")
        instructions_btn.setFont(QFont("Arial", BUTTON_FONT_SIZE))
        instructions_btn.setStyleSheet(BUTTON_STYLE)
        instructions_btn.clicked.connect(self.on_instructions_callback)
        return instructions_btn
