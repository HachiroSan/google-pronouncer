# Google Pronouncer

A Python library for downloading pronunciation MP3 files from Google's dictionary service.

## Installation

```bash
pip install google-pronouncer
```

## Command Line Usage

The package provides a command-line interface with several commands:

### Download Pronunciations

```bash
# Download all accents for words
google-pronouncer download hello world

# Download specific accent (gb/us)
google-pronouncer download hello -a gb

# Force fresh download (ignore cache)
google-pronouncer download hello --force-download

# Disable cache usage
google-pronouncer download hello --no-cache

# Specify output directory
google-pronouncer download hello -o ./my-pronunciations
```

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
  -o, --output-dir PATH  Directory to save pronunciations (default: ./pronunciations)
  -t, --timeout SECONDS  Request timeout in seconds (default: 10)
  -v, --verbose         Enable verbose logging
  --no-cache           Disable cache usage
  --force-download     Force download even if cached
```

## Python Library Usage

### Basic Usage

```python
from google_pronouncer import GooglePronunciationDownloader, DownloadConfig, AccentType

# Create configuration
config = DownloadConfig(
    output_dir="pronunciations",
    use_cache=True,           # Enable caching (default: True)
    force_download=False      # Force fresh download (default: False)
)

# Initialize downloader
downloader = GooglePronunciationDownloader(config)

# Download single word with specific accent
path = downloader.download_pronunciation("hello", AccentType.BRITISH)
print(f"Downloaded to: {path}")

# Download all accents for a word
paths = downloader.download_all_accents("world")
print(f"Downloaded files: {paths}")

# Download multiple words
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