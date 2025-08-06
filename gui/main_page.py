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
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title_label = self.create_title_label()
        play_button = self.create_play_button()
        instructions_button = self.create_instructions_button()

        main_layout.addWidget(title_label)
        main_layout.addStretch()
        main_layout.addWidget(play_button)
        main_layout.addWidget(instructions_button)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def create_title_label(self):
        # Create title label
        title_label = QLabel("HandDJ")
        title_label.setFont(QFont("Arial", 32, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        return title_label

    def create_play_button(self):
        # Create play button
        play_button = QPushButton("Play")
        play_button.setFont(QFont("Arial", BUTTON_FONT_SIZE))
        play_button.setStyleSheet(BUTTON_STYLE)
        play_button.clicked.connect(self.on_play_callback)
        return play_button

    def create_instructions_button(self):
        # Create instruction button
        instructions_button = QPushButton("Instructions")
        instructions_button.setFont(QFont("Arial", BUTTON_FONT_SIZE))
        instructions_button.setStyleSheet(BUTTON_STYLE)
        instructions_button.clicked.connect(self.on_instructions_callback)
        return instructions_button
