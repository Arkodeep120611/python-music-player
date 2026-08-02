import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QHBoxLayout,
    QListWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MusicPlayerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Music Player")
        self.resize(900, 600)

        # Central container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Header
        self.now_playing_label = QLabel("Now Playing: Nothing loaded")
        self.now_playing_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.now_playing_label)

        # Playlist area
        self.playlist_widget = QListWidget()
        main_layout.addWidget(self.playlist_widget)

        # Control bar (horizontal)
        controls_layout = QHBoxLayout()

        self.prev_button = QPushButton("⏮ Previous")
        self.play_button = QPushButton("▶ Play")
        self.pause_button = QPushButton("⏸ Pause")
        self.stop_button = QPushButton("⏹ Stop")
        self.next_button = QPushButton("Next ⏭")

        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.pause_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.next_button)

        main_layout.addLayout(controls_layout)


def main():
    app = QApplication(sys.argv)
    window = MusicPlayerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()