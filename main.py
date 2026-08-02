import os
import sys
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
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

        # Audio engine setup
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

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
        self.pause_button.clicked.connect(self.toggle_pause_resume)
        self.stop_button.clicked.connect(self.stop_song)
        self.next_button.clicked.connect(self.play_next_song)
        self.prev_button.clicked.connect(self.play_previous_song)

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
            item = QListWidgetItem(filename)
            item.setData(Qt.UserRole, path)
            self.playlist_widget.addItem(item)

    def play_selected_song(self):
        """Load selected song into media player and play it."""
        current_item = self.playlist_widget.currentItem()

        if current_item is None:
            self.now_playing_label.setText("Now Playing: Please select a song first")
            return

        song_name = current_item.text()
        song_path = current_item.data(Qt.UserRole)

        if not song_path:
            self.now_playing_label.setText("Now Playing: Invalid file path")
            return

        self.player.setSource(QUrl.fromLocalFile(song_path))
        self.player.play()
        self.now_playing_label.setText(f"Now Playing: {song_name}")

    def toggle_pause_resume(self):
        """
        Pause if currently playing.
        Resume if currently paused.
        If stopped, start selected song.
        """
        state = self.player.playbackState()

        if state == QMediaPlayer.PlayingState:
            self.player.pause()

            current_item = self.playlist_widget.currentItem()
            if current_item is None:
                self.now_playing_label.setText("Paused")
            else:
                self.now_playing_label.setText(f"Paused: {current_item.text()}")

        elif state == QMediaPlayer.PausedState:
            self.player.play()

            current_item = self.playlist_widget.currentItem()
            if current_item is None:
                self.now_playing_label.setText("Now Playing")
            else:
                self.now_playing_label.setText(f"Now Playing: {current_item.text()}")

        else:
            # Stopped state: try starting selected song
            self.play_selected_song()

    def stop_song(self):
        """Stop real playback and update label."""
        self.player.stop()
        self.now_playing_label.setText("Now Playing: Stopped")

    def play_next_song(self):
        """Move selection to next playlist item and play it."""
        total_items = self.playlist_widget.count()
        if total_items == 0:
            self.now_playing_label.setText("Now Playing: Playlist is empty")
            return

        current_row = self.playlist_widget.currentRow()

        if current_row == -1:
            self.playlist_widget.setCurrentRow(0)
        else:
            next_row = min(current_row + 1, total_items - 1)
            self.playlist_widget.setCurrentRow(next_row)

        self.play_selected_song()

    def play_previous_song(self):
        """Move selection to previous playlist item and play it."""
        total_items = self.playlist_widget.count()
        if total_items == 0:
            self.now_playing_label.setText("Now Playing: Playlist is empty")
            return

        current_row = self.playlist_widget.currentRow()

        if current_row == -1:
            self.playlist_widget.setCurrentRow(0)
        else:
            previous_row = max(current_row - 1, 0)
            self.playlist_widget.setCurrentRow(previous_row)

        self.play_selected_song()


def main():
    app = QApplication(sys.argv)
    window = MusicPlayerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()