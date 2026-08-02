import os
import sys
import random
from PySide6.QtCore import Qt, QUrl, QSettings, QSize
from PySide6.QtGui import QAction, QShortcut, QKeySequence
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
        self.resize(1020, 650)

        # Step 18: persistent settings
        self.settings = QSettings("ArkodeepApps", "PythonMusicPlayer")

        # Audio engine setup
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        # Seek handling flags
        self.is_user_seeking = False
        self.seek_supported_for_current_track = False

        # Playlist state
        self.loaded_file_paths = set()

        # Playback modes
        self.shuffle_enabled = False
        self.repeat_mode = "off"  # one of: off, one, all

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
        self.playlist_widget.setSelectionMode(QListWidget.ExtendedSelection)
        self.playlist_widget.setAcceptDrops(True)
        self.playlist_widget.setDragDropMode(QListWidget.DropOnly)
        self.playlist_widget.viewport().setAcceptDrops(True)
        self.playlist_widget.setDefaultDropAction(Qt.CopyAction)
        main_layout.addWidget(self.playlist_widget)
        self.playlist_widget.itemDoubleClicked.connect(self.play_item_from_double_click)

        # Allow main window drop events too
        self.setAcceptDrops(True)

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

        self.seek_row_widget.hide()

        # Controls row
        controls_layout = QHBoxLayout()
        self.prev_button = QPushButton("⏮ Previous")
        self.play_button = QPushButton("▶ Play")
        self.pause_button = QPushButton("⏸ Pause")
        self.stop_button = QPushButton("⏹ Stop")
        self.next_button = QPushButton("Next ⏭")
        self.remove_button = QPushButton("🗑 Remove Selected")

        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.pause_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.next_button)
        controls_layout.addWidget(self.remove_button)
        main_layout.addLayout(controls_layout)

        # Mode controls row
        mode_layout = QHBoxLayout()
        self.shuffle_button = QPushButton("Shuffle: Off")
        self.repeat_button = QPushButton("Repeat: Off")
        mode_layout.addWidget(self.shuffle_button)
        mode_layout.addWidget(self.repeat_button)
        main_layout.addLayout(mode_layout)

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

        # Wire playback controls
        self.play_button.clicked.connect(self.play_selected_song)
        self.pause_button.clicked.connect(self.toggle_pause_resume)
        self.stop_button.clicked.connect(self.stop_song)
        self.next_button.clicked.connect(self.play_next_song)
        self.prev_button.clicked.connect(self.play_previous_song)
        self.remove_button.clicked.connect(self.remove_selected_tracks)

        # Wire mode controls
        self.shuffle_button.clicked.connect(self.toggle_shuffle)
        self.repeat_button.clicked.connect(self.cycle_repeat_mode)

        # Volume
        self.volume_slider.valueChanged.connect(self.change_volume)

        # Player signals
        self.player.positionChanged.connect(self.on_position_changed)
        self.player.durationChanged.connect(self.on_duration_changed)
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)

        # Seek slider interactions
        self.seek_slider.sliderPressed.connect(self.on_seek_pressed)
        self.seek_slider.sliderReleased.connect(self.on_seek_released)
        self.seek_slider.sliderMoved.connect(self.on_seek_moved)

        # Keyboard shortcuts
        self._setup_shortcuts()

        # Apply persisted settings now that UI exists
        self.load_settings()

    def _create_menu(self):
        file_menu = self.menuBar().addMenu("File")

        open_action = QAction("Open Music Files...", self)
        open_action.triggered.connect(self.open_files)
        file_menu.addAction(open_action)

        clear_action = QAction("Clear Playlist", self)
        clear_action.triggered.connect(self.clear_playlist)
        file_menu.addAction(clear_action)

        remove_selected_action = QAction("Remove Selected", self)
        remove_selected_action.triggered.connect(self.remove_selected_tracks)
        file_menu.addAction(remove_selected_action)

        file_menu.addSeparator()

        save_playlist_action = QAction("Save Playlist (.m3u)...", self)
        save_playlist_action.triggered.connect(self.save_playlist_m3u)
        file_menu.addAction(save_playlist_action)

        load_playlist_action = QAction("Load Playlist (.m3u)...", self)
        load_playlist_action.triggered.connect(self.load_playlist_m3u)
        file_menu.addAction(load_playlist_action)

    def _setup_shortcuts(self):
        # Space = play/pause toggle
        self.shortcut_space = QShortcut(QKeySequence(Qt.Key_Space), self)
        self.shortcut_space.activated.connect(self.play_pause_shortcut_action)

        # Ctrl+Right = next
        self.shortcut_next = QShortcut(QKeySequence("Ctrl+Right"), self)
        self.shortcut_next.activated.connect(self.play_next_song)

        # Ctrl+Left = previous
        self.shortcut_prev = QShortcut(QKeySequence("Ctrl+Left"), self)
        self.shortcut_prev.activated.connect(self.play_previous_song)

        # Delete = remove selected
        self.shortcut_delete = QShortcut(QKeySequence(Qt.Key_Delete), self)
        self.shortcut_delete.activated.connect(self.remove_selected_tracks)

    # ---------- Step 18: settings persistence ----------

    def load_settings(self):
        """Load persisted settings and apply them to UI/state."""
        # Window size
        saved_size = self.settings.value("window/size")
        if isinstance(saved_size, QSize):
            self.resize(saved_size)

        # Volume (0-100)
        saved_volume = self.settings.value("audio/volume", 50, type=int)
        saved_volume = max(0, min(100, saved_volume))
        self.volume_slider.setValue(saved_volume)
        self.audio_output.setVolume(saved_volume / 100.0)

        # Shuffle
        self.shuffle_enabled = self.settings.value("playback/shuffle", False, type=bool)
        self.shuffle_button.setText("Shuffle: On" if self.shuffle_enabled else "Shuffle: Off")

        # Repeat mode
        saved_repeat = self.settings.value("playback/repeat_mode", "off", type=str)
        if saved_repeat not in {"off", "all", "one"}:
            saved_repeat = "off"
        self.repeat_mode = saved_repeat
        self._refresh_repeat_button_text()

    def save_settings(self):
        """Persist settings."""
        self.settings.setValue("window/size", self.size())
        self.settings.setValue("audio/volume", self.volume_slider.value())
        self.settings.setValue("playback/shuffle", self.shuffle_enabled)
        self.settings.setValue("playback/repeat_mode", self.repeat_mode)

    def _refresh_repeat_button_text(self):
        if self.repeat_mode == "off":
            self.repeat_button.setText("Repeat: Off")
        elif self.repeat_mode == "all":
            self.repeat_button.setText("Repeat: All")
        else:
            self.repeat_button.setText("Repeat: One")

    def closeEvent(self, event):
        """Save settings on app close."""
        self.save_settings()
        super().closeEvent(event)

    # ---------- Drag & drop support ----------

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        file_paths = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_paths.append(url.toLocalFile())

        self.add_files_from_paths(file_paths)
        event.acceptProposedAction()

    # ---------- Playlist helpers ----------

    def is_supported_audio_file(self, path):
        supported_exts = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}
        ext = os.path.splitext(path)[1].lower()
        return ext in supported_exts

    def add_song_path_to_playlist(self, path):
        if not path:
            return False

        if not self.is_supported_audio_file(path):
            return False

        normalized_path = os.path.normpath(path)
        if normalized_path in self.loaded_file_paths:
            return False

        filename = os.path.basename(path)
        item = QListWidgetItem(filename)
        item.setData(Qt.UserRole, path)
        self.playlist_widget.addItem(item)

        self.loaded_file_paths.add(normalized_path)
        return True

    def add_files_from_paths(self, file_paths):
        if not file_paths:
            return

        added_count = 0
        skipped_count = 0

        for path in file_paths:
            if self.add_song_path_to_playlist(path):
                added_count += 1
            else:
                skipped_count += 1

        if added_count > 0 and skipped_count == 0:
            self.now_playing_label.setText(f"Now Playing: Added {added_count} song(s)")
        elif added_count > 0 and skipped_count > 0:
            self.now_playing_label.setText(
                f"Now Playing: Added {added_count}, skipped {skipped_count} unsupported/duplicate file(s)"
            )
        else:
            self.now_playing_label.setText("Now Playing: No new supported files were added")

    def open_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Music Files",
            "",
            "Audio Files (*.mp3 *.wav *.flac *.ogg *.m4a);;All Files (*)",
        )
        self.add_files_from_paths(file_paths)

    def clear_playlist(self):
        self.player.stop()
        self.playlist_widget.clear()
        self.loaded_file_paths.clear()

        self.seek_supported_for_current_track = False
        self.seek_row_widget.hide()
        self.seek_slider.setRange(0, 0)
        self.seek_slider.setValue(0)
        self.current_time_label.setText("00:00")
        self.total_time_label.setText("00:00")

        self.now_playing_label.setText("Now Playing: Playlist cleared")

    def remove_selected_tracks(self):
        selected_items = self.playlist_widget.selectedItems()
        if not selected_items:
            self.now_playing_label.setText("Now Playing: No tracks selected to remove")
            return

        removed_count = 0

        for item in selected_items:
            song_path = item.data(Qt.UserRole)
            if song_path:
                normalized_path = os.path.normpath(song_path)
                self.loaded_file_paths.discard(normalized_path)

            row = self.playlist_widget.row(item)
            self.playlist_widget.takeItem(row)
            removed_count += 1

        if self.playlist_widget.count() == 0:
            self.player.stop()
            self.seek_supported_for_current_track = False
            self.seek_row_widget.hide()
            self.seek_slider.setRange(0, 0)
            self.seek_slider.setValue(0)
            self.current_time_label.setText("00:00")
            self.total_time_label.setText("00:00")
            self.now_playing_label.setText("Now Playing: Playlist is empty after removal")
        else:
            self.now_playing_label.setText(f"Now Playing: Removed {removed_count} track(s)")

    # ---------- Save / Load .m3u ----------

    def save_playlist_m3u(self):
        total_items = self.playlist_widget.count()
        if total_items == 0:
            self.now_playing_label.setText("Now Playing: Playlist is empty, nothing to save")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Playlist",
            "",
            "M3U Playlist (*.m3u);;All Files (*)",
        )
        if not file_path:
            return

        if not file_path.lower().endswith(".m3u"):
            file_path += ".m3u"

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for i in range(total_items):
                    item = self.playlist_widget.item(i)
                    song_path = item.data(Qt.UserRole)
                    if song_path:
                        f.write(f"{song_path}\n")

            self.now_playing_label.setText(
                f"Now Playing: Playlist saved to {os.path.basename(file_path)}"
            )
        except Exception as e:
            self.now_playing_label.setText(f"Now Playing: Failed to save playlist ({e})")

    def load_playlist_m3u(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Playlist",
            "",
            "M3U Playlist (*.m3u);;All Files (*)",
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.now_playing_label.setText(f"Now Playing: Failed to load playlist ({e})")
            return

        self.clear_playlist()

        base_dir = os.path.dirname(file_path)
        added_count = 0
        missing_count = 0

        for line in lines:
            if line.startswith("#"):
                continue

            candidate_path = line
            if not os.path.isabs(candidate_path):
                candidate_path = os.path.normpath(os.path.join(base_dir, candidate_path))

            if os.path.exists(candidate_path):
                if self.add_song_path_to_playlist(candidate_path):
                    added_count += 1
            else:
                missing_count += 1

        if added_count > 0 and missing_count == 0:
            self.now_playing_label.setText(f"Now Playing: Loaded {added_count} song(s) from playlist")
        elif added_count > 0 and missing_count > 0:
            self.now_playing_label.setText(
                f"Now Playing: Loaded {added_count}, missing {missing_count} file(s)"
            )
        else:
            self.now_playing_label.setText("Now Playing: No valid songs found in playlist")

    # ---------- Playback controls ----------

    def play_item_from_double_click(self, item):
        row = self.playlist_widget.row(item)
        self.playlist_widget.setCurrentRow(row)
        self.play_selected_song()

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

        # Reset seek UI before loading media
        self.seek_supported_for_current_track = False
        self.seek_row_widget.hide()
        self.seek_slider.setRange(0, 0)
        self.seek_slider.setValue(0)
        self.current_time_label.setText("00:00")
        self.total_time_label.setText("00:00")

        self.player.setSource(QUrl.fromLocalFile(song_path))
        self.player.play()
        self.now_playing_label.setText(f"Now Playing: {song_name}")

    def play_pause_shortcut_action(self):
        """Space shortcut: if playing -> pause, else -> play/resume."""
        state = self.player.playbackState()
        if state == QMediaPlayer.PlayingState:
            self.toggle_pause_resume()
        elif state == QMediaPlayer.PausedState:
            self.toggle_pause_resume()
        else:
            current_item = self.playlist_widget.currentItem()
            if current_item is None and self.playlist_widget.count() > 0:
                self.playlist_widget.setCurrentRow(0)
            self.play_selected_song()

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

        if self.shuffle_enabled:
            next_row = self.get_random_row(exclude_row=current_row)
            if next_row is None:
                next_row = 0
        else:
            if current_row == -1:
                next_row = 0
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

        if self.shuffle_enabled:
            prev_row = self.get_random_row(exclude_row=current_row)
            if prev_row is None:
                prev_row = 0
        else:
            if current_row == -1:
                prev_row = 0
            else:
                prev_row = max(current_row - 1, 0)

        self.playlist_widget.setCurrentRow(prev_row)
        self.play_selected_song()

    def change_volume(self, value):
        self.audio_output.setVolume(value / 100.0)

    # ---------- Shuffle + Repeat ----------

    def toggle_shuffle(self):
        self.shuffle_enabled = not self.shuffle_enabled
        self.shuffle_button.setText("Shuffle: On" if self.shuffle_enabled else "Shuffle: Off")

    def cycle_repeat_mode(self):
        # Cycle: off -> all -> one -> off
        if self.repeat_mode == "off":
            self.repeat_mode = "all"
        elif self.repeat_mode == "all":
            self.repeat_mode = "one"
        else:
            self.repeat_mode = "off"

        self._refresh_repeat_button_text()

    def get_random_row(self, exclude_row):
        total_items = self.playlist_widget.count()
        if total_items <= 1:
            return None

        choices = [i for i in range(total_items) if i != exclude_row]
        if not choices:
            return None
        return random.choice(choices)

    # ---------- Seek logic (safe fallback) ----------

    def on_duration_changed(self, duration_ms):
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

    # ---------- End-of-track handling with repeat/shuffle ----------

    def on_media_status_changed(self, status):
        if status != QMediaPlayer.EndOfMedia:
            return

        total_items = self.playlist_widget.count()
        if total_items == 0:
            self.now_playing_label.setText("Now Playing: Playlist is empty")
            return

        current_row = self.playlist_widget.currentRow()

        # Repeat One: restart same track WITHOUT reloading source
        if self.repeat_mode == "one":
            if current_row < 0:
                current_row = 0
                self.playlist_widget.setCurrentRow(current_row)

            self.player.setPosition(0)
            self.player.play()

            current_item = self.playlist_widget.currentItem()
            if current_item:
                self.now_playing_label.setText(f"Now Playing: {current_item.text()}")
            else:
                self.now_playing_label.setText("Now Playing")
            return

        # Shuffle behavior
        if self.shuffle_enabled:
            next_row = self.get_random_row(exclude_row=current_row)
            if next_row is None:
                # only one song
                if self.repeat_mode == "all":
                    self.playlist_widget.setCurrentRow(0)
                    self.play_selected_song()
                else:
                    self.stop_song()
                    self.now_playing_label.setText("Now Playing: End of playlist")
                return

            self.playlist_widget.setCurrentRow(next_row)
            self.play_selected_song()
            return

        # Non-shuffle sequential behavior
        if current_row < 0:
            self.stop_song()
            return

        next_row = current_row + 1
        if next_row < total_items:
            self.playlist_widget.setCurrentRow(next_row)
            self.play_selected_song()
        else:
            # End reached
            if self.repeat_mode == "all":
                self.playlist_widget.setCurrentRow(0)
                self.play_selected_song()
            else:
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