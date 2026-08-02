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
    QSlider,
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

        # Set default volume (0.0 to 1.0 for QAudioOutput)
        self.audio_output.setVolume(0.5)

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

        # Controls row
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

        # Volume row
        volume_layout = QHBoxLayout()
        volume_label = QLabel("Volume")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)  # match 0.5 default volume

        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        main_layout.addLayout(volume_layout)

        # Build menu
        self._create_menu()

        # Wire button actions
        self.play_button.clicked.connect(self.play_selected_song)
        self.pause_button.clicked.connect(self.toggle_pause_resume)
        self.stop_button.clicked.connect(self.stop_song)
        self.next_button.clicked.connect(self.play_next_song)
        self.prev_button.clicked.connect(self.play_previous_song)

        # Wire volume slider
        self.volume_slider.valueChanged.connect(self.change_volume)

    def _create_menu(self):
        file_menu = self.menuBar().addMenu("File")

        open_action = QAction("Open Music Files...", self)
        open_action.triggered.connect(self.open_files)
        file_menu.addAction(open_action)

    def open_files(self):
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
            self.play_selected_song()

    def stop_song(self):
        self.player.stop()
        self.now_playing_label.setText("Now Playing: Stopped")

    def play_next_song(self):
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

    def change_volume(self, value):
        """Slider value 0-100 -> QAudioOutput volume 0.0-1.0"""
        self.audio_output.setVolume(value / 100.0)


def main():
    app = QApplication(sys.argv)
    window = MusicPlayerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()