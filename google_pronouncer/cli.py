"""Command-line interface for Google Pronouncer."""

import argparse
import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Set
from tqdm import tqdm

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
    
    # Global options
    parser.add_argument(
        "-d", "--download",
        nargs="+",
        metavar="WORD",
        help="Download pronunciations for one or more words"
    )
    parser.add_argument(
        "-f", "--file",
        type=argparse.FileType('r'),
        help="File containing words to download (one word per line)"
    )
    parser.add_argument(
        "-a", "--accent",
        choices=["gb", "us", "all"],
        default="us",
        help="Accent to download (us=American, gb=British, all=both) (default: us)"
    )
    parser.add_argument(
        "-j", "--jobs",
        type=int,
        default=4,
        help="Number of parallel downloads (default: 4)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=Path("."),
        help="Directory to save pronunciations (default: current directory)"
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
    parser.add_argument(
        "--use-subdirs",
        action="store_true",
        help="Use subdirectories for each word (default: only when downloading multiple accents)"
    )
    
    # Subcommands for cache management
    subparsers = parser.add_subparsers(dest='command', help='Additional commands')
    
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
    
    return parser.parse_args()

def download_word(word: str, config: DownloadConfig, accent: str = "us") -> tuple[str, bool, List[Path]]:
    """Download pronunciations for a single word."""
    # Set use_subdirs based on whether we're downloading multiple accents
    config.use_subdirs = config.use_subdirs or accent == "all"
    downloader = GooglePronunciationDownloader(config)
    try:
        if accent == "all":
            paths = downloader.download_all_accents(word)
        else:
            path = downloader.download_pronunciation(word, AccentType(accent))
            paths = [path] if path else []

        success = bool(paths)
        return word, success, paths

    except (DownloadError, CacheError) as e:
        logging.error(f"Error processing '{word}': {e}")
        return word, False, []
    except Exception as e:
        logging.error(f"Unexpected error processing '{word}': {e}")
        return word, False, []

def process_words(words: List[str], config: DownloadConfig, accent: str = "us", jobs: int = 4) -> int:
    """Process words in parallel and return exit code."""
    # Remove duplicates while preserving order
    unique_words: List[str] = list(dict.fromkeys(word.strip().lower() for word in words if word.strip()))
    
    if not unique_words:
        logging.error("No valid words provided")
        return 1

    success_count = 0
    failed_words = []
    
    print(f"\nDownloading pronunciations for {len(unique_words)} words...")
    
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = {
            executor.submit(download_word, word, config, accent): word 
            for word in unique_words
        }
        
        with tqdm(total=len(unique_words), unit='word') as pbar:
            for future in as_completed(futures):
                word, success, paths = future.result()
                pbar.update(1)
                
                if success:
                    success_count += 1
                    if paths:
                        tqdm.write(f"✓ {word}: {', '.join(str(p) for p in paths)}")
                else:
                    failed_words.append(word)
                    tqdm.write(f"✗ {word}: Failed to download")

    # Print summary
    print(f"\nDownload Summary:")
    print(f"✓ Successfully downloaded: {success_count}/{len(unique_words)}")
    if failed_words:
        print(f"✗ Failed words: {', '.join(failed_words)}")

    return 0 if not failed_words else 1

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
                print(f"Cleared cache for '{word}'")
        else:
            downloader.clear_cache()
            print("Cleared all cache")
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
        force_download=args.force_download,
        use_subdirs=args.use_subdirs
    )
    
    downloader = GooglePronunciationDownloader(config)

    try:
        # Handle download command (both -d and legacy 'download' command)
        if args.download or (args.command == 'download' and args.words):
            words = []
            if args.file:
                words.extend(line.strip() for line in args.file)
                args.file.close()
            if args.download:
                words.extend(args.download)
            elif args.command == 'download':
                words.extend(args.words)
            return process_words(words, config, args.accent, args.jobs)
        elif args.command == 'cache-info':
            return show_cache_info(downloader, args.words)
        elif args.command == 'clear-cache':
            return clear_cache(downloader, args.words)
        else:
            if not any([args.download, args.file, args.command]):
                logging.error("No command specified. Use -d to download or --help for usage information.")
            return 1
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 