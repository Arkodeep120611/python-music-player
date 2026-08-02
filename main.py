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
        self.audio_output.setVolume(0.5)

        # Seek handling flags
        self.is_user_seeking = False
        self.seek_supported_for_current_track = False

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

        # Seek row container (shown only when supported)
        self.seek_row_widget = QWidget()
        seek_layout = QHBoxLayout()
        seek_layout.setContentsMargins(0, 0, 0, 0)
        self.seek_row_widget.setLayout(seek_layout)

        self.current_time_label = QLabel("00:00")
        self.seek_slider = QSlider(Qt.Horizontal)
        self.seek_slider.setRange(0, 0)
        self.total_time_label = QLabel("00:00")

        seek_layout.addWidget(self.current_time_label)
        seek_layout.addWidget(self.seek_slider)
        seek_layout.addWidget(self.total_time_label)
        main_layout.addWidget(self.seek_row_widget)

        # Hide by default; show only when duration is valid
        self.seek_row_widget.hide()

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
        self.volume_slider.setValue(50)

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

        # Wire player signals
        self.player.positionChanged.connect(self.on_position_changed)
        self.player.durationChanged.connect(self.on_duration_changed)
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)

        # Wire seek slider interactions
        self.seek_slider.sliderPressed.connect(self.on_seek_pressed)
        self.seek_slider.sliderReleased.connect(self.on_seek_released)
        self.seek_slider.sliderMoved.connect(self.on_seek_moved)

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

        # Reset seek UI state before loading new media
        self.seek_supported_for_current_track = False
        self.seek_row_widget.hide()
        self.seek_slider.setRange(0, 0)
        self.seek_slider.setValue(0)
        self.current_time_label.setText("00:00")
        self.total_time_label.setText("00:00")

        self.player.setSource(QUrl.fromLocalFile(song_path))
        self.player.play()
        self.now_playing_label.setText(f"Now Playing: {song_name}")

    def toggle_pause_resume(self):
        state = self.player.playbackState()

        if state == QMediaPlayer.PlayingState:
            self.player.pause()
            current_item = self.playlist_widget.currentItem()
            self.now_playing_label.setText(
                "Paused" if current_item is None else f"Paused: {current_item.text()}"
            )

        elif state == QMediaPlayer.PausedState:
            self.player.play()
            current_item = self.playlist_widget.currentItem()
            self.now_playing_label.setText(
                "Now Playing" if current_item is None else f"Now Playing: {current_item.text()}"
            )

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
            self.playlist_widget.setCurrentRow(min(current_row + 1, total_items - 1))

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
            self.playlist_widget.setCurrentRow(max(current_row - 1, 0))

        self.play_selected_song()

    def change_volume(self, value):
        self.audio_output.setVolume(value / 100.0)

    # ---------- Seek logic with safe fallback ----------

    def on_duration_changed(self, duration_ms):
        """
        If duration is valid (>0), show seek row and enable seeking.
        If duration is invalid (<=0), hide seek row (unsupported/unknown seek case).
        """
        if duration_ms and duration_ms > 0:
            self.seek_supported_for_current_track = True
            self.seek_row_widget.show()
            self.seek_slider.setRange(0, duration_ms)
            self.total_time_label.setText(self.format_ms(duration_ms))
        else:
            self.seek_supported_for_current_track = False
            self.seek_row_widget.hide()
            self.seek_slider.setRange(0, 0)
            self.seek_slider.setValue(0)
            self.current_time_label.setText("00:00")
            self.total_time_label.setText("00:00")

    def on_position_changed(self, position_ms):
        if not self.seek_supported_for_current_track:
            return

        if not self.is_user_seeking:
            self.seek_slider.setValue(position_ms)
        self.current_time_label.setText(self.format_ms(position_ms))

    def on_seek_pressed(self):
        if self.seek_supported_for_current_track:
            self.is_user_seeking = True

    def on_seek_moved(self, position_ms):
        if self.seek_supported_for_current_track:
            self.current_time_label.setText(self.format_ms(position_ms))

    def on_seek_released(self):
        if not self.seek_supported_for_current_track:
            self.is_user_seeking = False
            return

        target_ms = self.seek_slider.value()
        self.player.setPosition(target_ms)
        self.is_user_seeking = False

    # ---------- Step 13: auto-next on end ----------

    def on_media_status_changed(self, status):
        """Auto-play next track when current one ends."""
        if status != QMediaPlayer.EndOfMedia:
            return

        total_items = self.playlist_widget.count()
        if total_items == 0:
            self.now_playing_label.setText("Now Playing: Playlist is empty")
            return

        current_row = self.playlist_widget.currentRow()

        # No valid selection -> stop safely
        if current_row < 0:
            self.stop_song()
            return

        next_row = current_row + 1
        if next_row < total_items:
            self.playlist_widget.setCurrentRow(next_row)
            self.play_selected_song()
        else:
            # End of playlist
            self.stop_song()
            self.now_playing_label.setText("Now Playing: End of playlist")

    @staticmethod
    def format_ms(ms):
        total_seconds = max(0, ms // 1000)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"


def main():
    app = QApplication(sys.argv)
    window = MusicPlayerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()