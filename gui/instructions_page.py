from PyQt5.QtWidgets import QVBoxLayout, QLabel, QScrollArea, QWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from gui.base_page import BasePage

class InstructionsPage(BasePage):
    # This page holds the instructions of the program
    def __init__(self, on_back_callback):
        super().__init__(on_back_callback, "HandDJ Instructions")

    def setup_content(self, layout):
        # Sets up content for the page
        scroll_area = self.create_scroll_area()
        layout.insertWidget(1, scroll_area)

    def create_scroll_area(self):
        # Creates scrollable area to hold content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        content_widget = self.create_content_widget()
        scroll_area.setWidget(content_widget)

        return scroll_area

    def create_content_widget(self):
        # Widget to hold content of scrollable area
        content_widget = QWidget()
        content_layout = QVBoxLayout()

        instructions = self.create_instructions_label()
        content_layout.addWidget(instructions)

        content_widget.setLayout(content_layout)
        return content_widget

    def create_instructions_label(self):
        # Label to display instruction text
        instructions_text = """
        <h1>WIP</h1>
        """
        instructions = QLabel(instructions_text)
        instructions.setFont(QFont("Arial", 12))
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: white; padding: 10px;")
        return instructions
