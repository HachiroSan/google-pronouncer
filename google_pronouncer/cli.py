"""Command-line interface for Google Pronouncer."""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List

from .downloader import GooglePronunciationDownloader, DownloadConfig, AccentType, DownloadError, CacheError

def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Download pronunciation MP3 files from Google's dictionary service"
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download pronunciations')
    download_parser.add_argument(
        "words",
        nargs="+",
        help="One or more words to download pronunciations for"
    )
    download_parser.add_argument(
        "-a", "--accent",
        choices=["gb", "us", "all"],
        default="all",
        help="Accent to download (default: all)"
    )
    
    # Cache info command
    cache_info_parser = subparsers.add_parser('cache-info', help='Show cache information')
    cache_info_parser.add_argument(
        "words",
        nargs="*",
        help="Optional words to show cache info for. If none provided, shows all."
    )
    
    # Clear cache command
    clear_cache_parser = subparsers.add_parser('clear-cache', help='Clear cached files')
    clear_cache_parser.add_argument(
        "words",
        nargs="*",
        help="Optional words to clear cache for. If none provided, clears all."
    )
    
    # Global options
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=Path("pronunciations"),
        help="Directory to save pronunciations (default: ./pronunciations)"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable cache usage"
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Force download even if cached"
    )
    
    return parser.parse_args()

def process_words(words: List[str], config: DownloadConfig, accent: str = "all") -> int:
    """Process words and return exit code."""
    downloader = GooglePronunciationDownloader(config)
    success = True

    for word in words:
        try:
            if accent == "all":
                paths = downloader.download_all_accents(word)
            else:
                path = downloader.download_pronunciation(word, AccentType(accent))
                paths = [path] if path else []

            if not paths:
                logging.error(f"No pronunciations downloaded for '{word}'")
                success = False

        except (DownloadError, CacheError) as e:
            logging.error(f"Error processing '{word}': {e}")
            success = False
        except Exception as e:
            logging.error(f"Unexpected error processing '{word}': {e}")
            success = False

    return 0 if success else 1

def show_cache_info(downloader: GooglePronunciationDownloader, words: List[str] = None) -> int:
    """Show cache information."""
    try:
        if words:
            for word in words:
                info = downloader.get_cache_info(word)
                if info:
                    print(f"\nCache info for '{word}':")
                    print(json.dumps(info[word], indent=2))
                else:
                    print(f"No cache info found for '{word}'")
        else:
            info = downloader.get_cache_info()
            if info:
                print("\nCache information:")
                print(json.dumps(info, indent=2))
            else:
                print("No cached files found")
        return 0
    except Exception as e:
        logging.error(f"Error getting cache info: {e}")
        return 1

def clear_cache(downloader: GooglePronunciationDownloader, words: List[str] = None) -> int:
    """Clear cache files."""
    try:
        if words:
            for word in words:
                downloader.clear_cache(word)
        else:
            downloader.clear_cache()
        return 0
    except Exception as e:
        logging.error(f"Error clearing cache: {e}")
        return 1

def main():
    """Main entry point for the CLI."""
    args = parse_args()
    setup_logging(args.verbose)

    config = DownloadConfig(
        output_dir=args.output_dir,
        timeout=args.timeout,
        use_cache=not args.no_cache,
        force_download=args.force_download
    )
    
    downloader = GooglePronunciationDownloader(config)

    try:
        if args.command == 'download':
            return process_words(args.words, config, args.accent)
        elif args.command == 'cache-info':
            return show_cache_info(downloader, args.words)
        elif args.command == 'clear-cache':
            return clear_cache(downloader, args.words)
        else:
            logging.error("No command specified. Use --help for usage information.")
            return 1
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 