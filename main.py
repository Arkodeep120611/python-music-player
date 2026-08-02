import os
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
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

        # Build menu
        self._create_menu()

        # Wire button actions
        self.play_button.clicked.connect(self.play_selected_song)
        self.pause_button.clicked.connect(self.pause_song)
        self.stop_button.clicked.connect(self.stop_song)

    def _create_menu(self):
        """Create the menu bar and wire menu actions."""
        file_menu = self.menuBar().addMenu("File")

        open_action = QAction("Open Music Files...", self)
        open_action.triggered.connect(self.open_files)
        file_menu.addAction(open_action)

    def open_files(self):
        """Open file dialog, select audio files, and append to playlist."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Music Files",
            "",
            "Audio Files (*.mp3 *.wav *.flac *.ogg *.m4a);;All Files (*)",
        )

        if not file_paths:
            return

        for path in file_paths:
            filename = os.path.basename(path)
            self.playlist_widget.addItem(filename)

    def play_selected_song(self):
        """Update label based on currently selected playlist item."""
        current_item = self.playlist_widget.currentItem()

        if current_item is None:
            self.now_playing_label.setText("Now Playing: Please select a song first")
            return

        song_name = current_item.text()
        self.now_playing_label.setText(f"Now Playing: {song_name}")

    def pause_song(self):
        """Update label to show paused state for selected song."""
        current_item = self.playlist_widget.currentItem()

        if current_item is None:
            self.now_playing_label.setText("Paused: No song selected")
            return

        song_name = current_item.text()
        self.now_playing_label.setText(f"Paused: {song_name}")

    def stop_song(self):
        """Update label to show stopped state."""
        self.now_playing_label.setText("Now Playing: Stopped")


def main():
    app = QApplication(sys.argv)
    window = MusicPlayerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()