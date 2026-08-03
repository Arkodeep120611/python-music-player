# HarmonyPlayer
A modern offline music player built with Python and PySide6.

## Features

- Open local audio files (`.mp3`, `.wav`, `.flac`, `.ogg`, `.m4a`)
- Playlist with duplicate prevention
- Drag & drop files into playlist
- Double-click to play
- Play / Pause / Stop / Next / Previous
- Shuffle + Repeat (`Off`, `All`, `One`)
- Conditional seek bar (auto-hides when seek unsupported)
- Save/Load playlist as `.m3u`
- Remove selected tracks
- Volume + Mute + Playback Speed (0.5x to 2.0x)
- Keyboard shortcuts
- Light/Dark theme toggle
- Persistent settings via `QSettings`

## Keyboard Shortcuts

- `Space` → Play/Pause
- `Ctrl + Right` → Next track
- `Ctrl + Left` → Previous track
- `Delete` → Remove selected track(s)
- `Ctrl + M` → Mute/Unmute
- `Ctrl + T` → Toggle theme

## Install

```bash
pip install PySide6
```

## Run

```bash
python main.py
```

## Notes

- Seek bar is shown only when the current media backend reports valid duration/seek support.
- On some systems/codecs (commonly some FLAC setups), seeking may be unavailable; UI handles this gracefully.
