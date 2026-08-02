import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget


class MusicPlayerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Music Player")
        self.resize(900, 600)

        # 1) Create a central widget and set it on the main window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 2) Create a vertical layout for the central widget
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # 3) Add a simple header label
        now_playing_label = QLabel("Now Playing: Nothing loaded")
        now_playing_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(now_playing_label)


def main():
    app = QApplication(sys.argv)
    window = MusicPlayerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()