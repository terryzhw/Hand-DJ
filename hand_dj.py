# Terrance Wong
# HandDJ 8/3/25

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.windows import MainWindow


def main():
    try:
        application = QApplication(sys.argv)
        main_window = MainWindow()
        main_window.show()
        sys.exit(application.exec_())
    except Exception as error:
        QMessageBox.critical(None, "Error", f"Failed to start: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()