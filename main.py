import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QHBoxLayout,
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
        now_playing_label = QLabel("Now Playing: Nothing loaded")
        now_playing_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(now_playing_label)

        # Control bar (horizontal)
        controls_layout = QHBoxLayout()

        prev_button = QPushButton("⏮ Previous")
        play_button = QPushButton("▶ Play")
        pause_button = QPushButton("⏸ Pause")
        stop_button = QPushButton("⏹ Stop")
        next_button = QPushButton("Next ⏭")

        controls_layout.addWidget(prev_button)
        controls_layout.addWidget(play_button)
        controls_layout.addWidget(pause_button)
        controls_layout.addWidget(stop_button)
        controls_layout.addWidget(next_button)

        main_layout.addLayout(controls_layout)


def main():
    app = QApplication(sys.argv)
    window = MusicPlayerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()