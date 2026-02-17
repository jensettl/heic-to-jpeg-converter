# 🔄 File Converter

Local file type conversion — no uploads, no cloud, no privacy concerns.

## Why?

Many online conversion services require uploading personal files to a remote server.
This tool runs entirely on your machine using battle-tested open-source libraries.

---

## Getting Started

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Clone the repository
git clone <your-repo-url>
cd file-converter

# Install dependencies
uv sync

# Run the application
uv run file-converter
```

### System Requirements

Two system-level dependencies are required for video and audio conversion.
Everything else installs automatically via `uv sync`.

| Tool | Required for | Install |
|------|-------------|---------|
| [ffmpeg](https://ffmpeg.org) | Video + Audio | `winget install ffmpeg` / `brew install ffmpeg` |

---

## Supported Conversions

### 🖼 Images
| From | To |
|------|----|
| HEIC | JPG, PNG |
| JPG  | PNG, WEBP |
| PNG  | JPG ⚠, WEBP, GIF |
| WEBP | JPG ⚠, PNG |
| GIF  | PNG |
| BMP  | JPG ⚠, PNG |
| TIFF | JPG ⚠, PNG |

### 🎬 Video
| From | To |
|------|----|
| MP4  | AVI, MKV, MOV |
| AVI  | MP4, MKV |
| MKV  | MP4, AVI |
| MOV  | MP4, AVI |

### 🎵 Audio
| From | To |
|------|----|
| MP3  | WAV, FLAC |
| WAV  | MP3 ⚠, FLAC |
| FLAC | MP3 ⚠, WAV |
| AAC  | MP3 ⚠, WAV |
| M4A  | MP3 ⚠, WAV |

### 📄 Documents
| From | To |
|------|----|
| PDF  | TXT |
| DOCX | TXT |

> ⚠ = lossy conversion — the app will warn you before proceeding.

---

## Project Structure

```
file-converter/
├── src/
│   ├── __init__.py
│   ├── __main__.py              # Entry point → launches TUI
│   ├── config.py                # App-wide settings (frozen dataclass)
│   ├── logger.py                # Structured session logging
│   ├── registry.py              # Conversion rules & validation
│   ├── converters/
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract BaseConverter
│   │   ├── image.py             # Pillow + pillow-heif
│   │   ├── video.py             # ffmpeg-python
│   │   └── document.py          # pypdf + python-docx
│   └── tui/
│       ├── __init__.py
│       ├── app.py               # Root Textual App
│       ├── screens/
│       │   ├── __init__.py
│       │   ├── main_screen.py   # File browser + format picker
│       │   └── progress_screen.py # Live progress + keep/delete prompt
│       └── widgets/
│           ├── __init__.py
│           └── format_selector.py  # Reactive format dropdown
├── tests/
│   ├── __init__.py
│   └── test_registry.py
├── logs/                        # Auto-created on first run
├── pyproject.toml
├── .gitignore
└── README.md
```

---

## Data Flow

```
1. User browses files via Textual DirectoryTree
         │
         ▼
2. MainScreen validates file against registry
   ├── Unknown extension?  → status warning, file rejected
   ├── Wrong media type?   → status warning, file rejected (one type per session)
   └── Valid → file staged in DataTable
         │
         ▼
3. FormatSelector reacts to source format
   └── Queries registry.get_valid_targets(ext)
       └── Populates dropdown with valid targets only
         │
         ▼
4. User picks target format → Convert button enables
         │
         ▼
5. ProgressScreen launched (files + target_format passed in)
         │
         ▼
6. Background worker thread iterates files
   ├── registry.get_route(src, target) → ConversionRoute
   ├── route.converter_class().convert(file, target) → output path
   ├── Lossy flag? → warning written to log panel
   └── Error? → logged, skipped, worker continues
         │
         ▼
7. After each file: keep/delete prompt shown to user
   ├── Keep  → original untouched, logger records it
   └── Delete → original unlinked, logger records it
         │
         ▼
8. Session summary written to logs/converter_YYYYMMDD_HHMMSS.log
```

---

## Module Responsibilities

### `config.py`
Holds app-wide constants (`APP_NAME`, `APP_VERSION`, `LOG_DIR`) as a frozen
dataclass. Single source of truth — no magic strings scattered across modules.

### `logger.py`
Writes a structured `.log` file per session. Handles four event types:
conversion success, skip, delete, and error. Also writes a summary at the end.
Initialised lazily — no log file is created unless a conversion actually starts.

### `registry.py`
The core of the validation layer. Owns two responsibilities:

- **`MediaType` enum + `EXTENSION_MEDIA_TYPE` dict** — maps every known
  extension to a domain (image, video, audio, document). Used by `MainScreen`
  to enforce one media type per session and block cross-domain nonsense like
  `mp4 → pdf` before it ever reaches a converter.

- **`ConversionRegistry`** — holds all registered `ConversionRoute` objects.
  Each route carries the source format, target format, converter class, and a
  `lossy` flag. Exposes `is_valid()`, `get_route()`, and `get_valid_targets()`
  so the TUI always shows only what is actually supported.

A module-level singleton (`registry = build_default_registry()`) is imported
everywhere so there is exactly one registry instance at runtime.

### `converters/base.py`
Abstract base class that all converters must implement. Provides the shared
`get_output_path()` helper which places the output file next to the source —
no converter needs to repeat that logic.

### `converters/image.py`
Pillow-based image converter. Registers HEIF/HEIC support once at import time
via `pillow-heif`. Handles the RGBA → RGB conversion required before saving
as JPEG.

### `converters/video.py`
Thin wrapper around `ffmpeg-python`. Delegates all codec and container logic
to ffmpeg — adding a new video format requires only a registry entry, not
code changes.

### `converters/audio.py`
ffmpeg-python-based audio converter. Delegates all codec and container logic
to ffmpeg, consistent with the video converter. Python 3.13 compatible — no
dependency on the removed `audioop` stdlib module.

### `converters/document.py`
Handles document extraction. Uses lazy imports (`pypdf`, `python-docx`) so
the heavy libraries are only loaded when a document conversion is actually
requested. Routes are dispatched internally via a dict of `(src, tgt)` tuples.

### `tui/app.py`
Minimal Textual `App` subclass. Sets the title and pushes `MainScreen` on
mount. Intentionally thin — all screen logic lives in the screens themselves.

### `tui/screens/main_screen.py`
The primary user-facing screen. Owns the file browser (`DirectoryTree`), the
staged file list (`DataTable`), and the convert button. Enforces one-media-type
per session by checking `registry.get_media_type()` on every added file.
Pushes `ProgressScreen` with the confirmed file list and target format.

### `tui/screens/progress_screen.py`
Runs conversions in a background worker thread to keep the UI responsive.
After each successful conversion, pauses the worker and shows a keep/delete
prompt on the main thread. The worker resumes once the user responds. Writes
the session summary to the log on completion.

### `tui/widgets/format_selector.py`
A reactive Textual widget wrapping a `Select` dropdown. Watches `source_format`
and rebuilds the options list automatically whenever it changes by querying
`registry.get_valid_targets()`. Exposes a `selected_format` property consumed
by `MainScreen`.

---

## Adding a New Conversion

Adding support for a new format requires changes in exactly two places:

**1. Register the route in `registry.py`:**
```python
# inside build_default_registry()
registry.register(ConversionRoute("png", "avif", ImageConverter, lossy=False))
```

**2. Make sure the converter handles the format.** For images, add the format
to `_PILLOW_FORMATS` in `converters/image.py` if Pillow supports it:
```python
_PILLOW_FORMATS: dict[str, str] = {
    ...
    "avif": "AVIF",
}
```

The TUI, validation, and logging pick it up automatically.

---

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run a specific file
uv run pytest tests/test_registry.py -v
```

---

## Logging

Each session writes a log to `logs/converter_YYYYMMDD_HHMMSS.log`:

```
2024-03-01 14:22:10 | INFO     | File Conversion Session Started
2024-03-01 14:22:11 | INFO     | SUCCESS | vacation.heic -> vacation.jpg | original deleted
2024-03-01 14:22:12 | INFO     | SUCCESS | photo.png -> photo.jpg | original kept
2024-03-01 14:22:12 | INFO     | Session Summary:
2024-03-01 14:22:12 | INFO     |   Success: 2
2024-03-01 14:22:12 | INFO     |   Skipped: 0
2024-03-01 14:22:12 | INFO     |   Errors: 0
```

---

## License

MIT License — free to use and modify.
