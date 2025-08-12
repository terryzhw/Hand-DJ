from modules.constants import *

# Button styling
BUTTON_STYLE = """
    QPushButton {
        background-color: #3a3a3a;
        color: white;
        padding: 10px;
        border-radius: 8px;
    }
    QPushButton:hover {
        background-color: #505050;
    }
    QPushButton:pressed {
        background-color: #2a2a2a;
    }
"""

# Input field styling
INPUT_STYLE = """
    background-color: #2a2a2a; 
    color: white; 
    padding: 8px; 
    border-radius: 6px;
"""

# Background styling
BACKGROUND_STYLE = f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};"

# Font sizes
TITLE_FONT_SIZE = 24
SUBTITLE_FONT_SIZE = 14
BUTTON_FONT_SIZE = 14
INPUT_FONT_SIZE = 12

# Layout spacing
DEFAULT_SPACING = 20 