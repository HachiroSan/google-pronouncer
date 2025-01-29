# Google Pronouncer

A Python library for downloading pronunciation MP3 files from Google's dictionary service.

## Installation

```bash
pip install google-pronouncer
```

## Command Line Usage

The package provides a simple command-line interface:

### Download Pronunciations

```bash
# Download US pronunciation (default) - saves in current directory
google-pronouncer -d hello world

# Download British pronunciation
google-pronouncer -d hello -a gb

# Download both accents (automatically uses subdirectories)
google-pronouncer -d hello -a all

# Save files in a specific directory
google-pronouncer -d hello -o ./pronunciations

# Force using subdirectories even for single accent
google-pronouncer -d hello --use-subdirs

# Download from a file (one word per line)
google-pronouncer -f words.txt

# Force fresh download (ignore cache)
google-pronouncer -d hello --force-download

# Disable cache usage
google-pronouncer -d hello --no-cache

# Download with verbose logging
google-pronouncer -v -d hello world
```

### File Organization

By default:
- Files are saved in the current directory
- Single accent downloads: Saved as `word_accent.mp3`
- Multiple accent downloads: Organized in subdirectories as `word/word_accent.mp3`
- Use `-o` to specify a different output directory
- Use `--use-subdirs` to force subdirectory organization even for single accent downloads

### Cache Management

```bash
# Show cache information for all words
google-pronouncer cache-info

# Show cache info for specific words
google-pronouncer cache-info hello world

# Clear all cache
google-pronouncer clear-cache

# Clear cache for specific words
google-pronouncer clear-cache hello world
```

### Global Options

```bash
  -d, --download WORD   Download pronunciations for one or more words
  -f, --file FILE      File containing words to download (one word per line)
  -a, --accent {gb,us,all}  Accent to download (us=American, gb=British, all=both) (default: us)
  -j, --jobs N         Number of parallel downloads (default: 4)
  -o, --output-dir PATH  Directory to save pronunciations (default: ./pronunciations)
  -t, --timeout SECONDS  Request timeout in seconds (default: 10)
  -v, --verbose        Enable verbose logging
  --no-cache          Disable cache usage
  --force-download    Force download even if cached
  --use-subdirs       Use subdirectories for each word (default: only when downloading multiple accents)
```

## Python Library Usage

### Basic Usage

```python
from google_pronouncer import GooglePronunciationDownloader, DownloadConfig, AccentType

# Create configuration (files will be saved in current directory)
config = DownloadConfig(
    output_dir=".",  # Current directory
    use_cache=True,  # Enable caching (default: True)
    force_download=False  # Force fresh download (default: False)
)

# Or specify a different output directory
config = DownloadConfig(
    output_dir="./pronunciations",
    use_cache=True,
    force_download=False
)

# Initialize downloader
downloader = GooglePronunciationDownloader(config)

# Download US pronunciation (default)
path = downloader.download_pronunciation("hello", AccentType.AMERICAN)
print(f"Downloaded to: {path}")

# Download British pronunciation
path = downloader.download_pronunciation("hello", AccentType.BRITISH)
print(f"Downloaded to: {path}")

# Download both accents for a word
paths = downloader.download_all_accents("world")
print(f"Downloaded files: {paths}")

# Download multiple words (US accent by default)
words = ["hello", "world", "python"]
paths = downloader.download_words(words)
print(f"Downloaded files: {paths}")
```

### Cache Management

```python
# Get cache information
info = downloader.get_cache_info()  # All words
info = downloader.get_cache_info("hello")  # Specific word

# Clear cache
downloader.clear_cache()  # All words
downloader.clear_cache("hello")  # Specific word
```

### Configuration Options

```python
config = DownloadConfig(
    output_dir="pronunciations",    # Directory to save files
    timeout=10,                     # Request timeout in seconds
    user_agent="Custom User Agent", # Optional custom user agent
    use_cache=True,                # Whether to use cached files
    min_file_size=1024,           # Minimum valid file size in bytes
    force_download=False          # Force fresh download
)
```

### Available Accents

- `AccentType.BRITISH` - British English pronunciation (`gb`)
- `AccentType.AMERICAN` - American English pronunciation (`us`)

### Error Handling

```python
from google_pronouncer import DownloadError, CacheError

try:
    path = downloader.download_pronunciation("word", AccentType.BRITISH)
except DownloadError as e:
    print(f"Download failed: {e}")
except CacheError as e:
    print(f"Cache error: {e}")
```

## Features

- Download pronunciations in British and American English
- Configurable output directory and request settings
- Smart caching system with validation
- Cache management tools (info, clear)
- Command-line interface
- Proper error handling and logging
- Type hints for better IDE support
- Support for downloading multiple words and accents
- Clean and simple API

## Cache System

The library includes a smart caching system that:
- Automatically caches downloaded files
- Validates cached files before use
- Provides cache information and management
- Supports forced fresh downloads
- Includes file size validation
- Maintains cache metadata

## Requirements

- Python 3.7+
- requests library (>=2.31.0)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 