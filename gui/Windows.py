from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtGui import QIcon
from gui.instructions_page import InstructionsPage
from gui.play_page import PlayPage
from gui.control_page import ControlPage
from gui.styles import BACKGROUND_STYLE
from tracking.dj_controller import DJController
from gui.main_page import MainPage

class MainWindow(QMainWindow):
    # Manages the different pages of the application and handles navigation between them.
    def __init__(self):
        super().__init__()
        # The dj_controller will be created when needed
        self.dj_controller = None
        self.setup_window_properties()
        self.setup_page_navigation()
        self.create_application_pages()
        self.add_pages_to_navigation()

    def setup_window_properties(self):
        # Sets up properties of the main window
        self.setWindowTitle("HandDJ")
        self.setGeometry(300, 100, 500, 600)
        self.setWindowIcon(QIcon("HandDJ.png"))
        self.setStyleSheet(BACKGROUND_STYLE)

    def setup_page_navigation(self):
        # Sets up page navigation and uses QStackedWidget to manage pages
        self.page_stack = QStackedWidget()
        self.setCentralWidget(self.page_stack)

    def create_application_pages(self):
        # Creates the pages and connects the navigation signals
        self.main_page = MainPage(
            on_play_callback=self.navigate_to_play_page,
            on_instructions_callback=self.navigate_to_instructions_page
        )
        self.instructions_page = InstructionsPage(on_back_callback=self.navigate_to_main_page)
        self.play_page = PlayPage(
            on_back_callback=self.navigate_to_main_page,
            on_play_callback=self.navigate_to_stats_page
        )
        self.stats_page = ControlPage(on_back_callback=self.navigate_to_main_page, overlay=None)
        self.current_song_title = "Unknown Song"

    def add_pages_to_navigation(self):
        # Adds created pages to the stack
        self.page_stack.addWidget(self.main_page)
        self.page_stack.addWidget(self.instructions_page)
        self.page_stack.addWidget(self.play_page)
        self.page_stack.addWidget(self.stats_page)
        self.page_stack.setCurrentWidget(self.main_page)

    def navigate_to_instructions_page(self):
        # Navigate to instructions page
        self.page_stack.setCurrentWidget(self.instructions_page)

    def navigate_to_main_page(self):
        # Navigate to main page
        self.page_stack.setCurrentWidget(self.main_page)

    def navigate_to_play_page(self):
        # Navigate to play page
        self.page_stack.setCurrentWidget(self.play_page)

    def navigate_to_stats_page(self, song_title=None, dj_controller=None):
        # Navigate to stats page with optional song title and dj_controller
        if song_title:
            self.current_song_title = song_title
            self.stats_page.audio_file_name = song_title
            if hasattr(self.stats_page, 'song_title_label'):
                self.stats_page.song_title_label.setText(f"♪ {song_title}")
        
        if dj_controller:
            self.dj_controller = dj_controller
            self.stats_page.overlay = dj_controller
            
        self.page_stack.setCurrentWidget(self.stats_page)
