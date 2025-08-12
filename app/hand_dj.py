# Terrance Wong
# HandDJ 

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.windows import MainWindow


def main():
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as error:
        QMessageBox.critical(None, "Error", f"Failed to start: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()