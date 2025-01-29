"""
Core functionality for downloading pronunciations from Google's dictionary service.
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Union, List, Dict

import requests
from requests.exceptions import RequestException

# Configure logging
logger = logging.getLogger(__name__)

class AccentType(Enum):
    """Supported accent types for pronunciation."""
    BRITISH = 'gb'
    AMERICAN = 'us'

@dataclass
class DownloadConfig:
    """Configuration for the downloader.
    
    Args:
        output_dir: Directory where pronunciations will be saved
        timeout: Request timeout in seconds
        user_agent: User agent string for requests
        use_cache: Whether to use cached files (default: True)
        min_file_size: Minimum valid file size in bytes (default: 1024)
        force_download: Force download even if file exists (default: False)
    """
    output_dir: Union[str, Path]
    timeout: int = 10
    user_agent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    use_cache: bool = True
    min_file_size: int = 1024  # 1KB minimum file size
    force_download: bool = False

    def __post_init__(self):
        """Convert output_dir to Path and ensure it exists."""
        self.output_dir = Path(self.output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Using output directory: {self.output_dir}")

class DownloadError(Exception):
    """Raised when a download operation fails."""
    pass

class CacheError(Exception):
    """Raised when a cached file is invalid."""
    pass

class GooglePronunciationDownloader:
    """Downloads pronunciation MP3 files from Google's dictionary service.
    
    Example:
        >>> config = DownloadConfig(output_dir="pronunciations")
        >>> downloader = GooglePronunciationDownloader(config)
        >>> path = downloader.download_pronunciation("hello", AccentType.BRITISH)
        >>> print(f"Downloaded to: {path}")
    """
    
    BASE_URL = "https://ssl.gstatic.com/dictionary/static/sounds/oxford/{word}--_{accent}_1.mp3"
    _cache_info: Dict[str, Dict] = {}  # Cache metadata

    def __init__(self, config: DownloadConfig):
        """Initialize the downloader with configuration."""
        self.config = config
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create and configure a requests session."""
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.config.user_agent
        })
        return session

    def _ensure_output_dir(self, word: str) -> Path:
        """Ensure the output directory exists for a word."""
        word_dir = self.config.output_dir / word
        word_dir.mkdir(parents=True, exist_ok=True)
        return word_dir

    def _get_cache_path(self, word: str, accent: AccentType) -> Path:
        """Get the path where the file would be cached."""
        word_dir = self._ensure_output_dir(word)
        return word_dir / f"{word}_{accent.value}.mp3"

    def _is_valid_cache(self, cache_path: Path) -> bool:
        """Check if cached file is valid."""
        if not cache_path.exists():
            return False
        
        try:
            file_size = cache_path.stat().st_size
            if file_size < self.config.min_file_size:
                logger.warning(f"Cached file {cache_path} is too small ({file_size} bytes)")
                return False
                
            # Add file to cache info
            self._cache_info[str(cache_path)] = {
                'size': file_size,
                'last_checked': os.path.getmtime(cache_path)
            }
            return True
            
        except OSError as e:
            logger.error(f"Error checking cache file {cache_path}: {e}")
            return False

    def download_pronunciation(self, word: str, accent: AccentType) -> Optional[Path]:
        """Download pronunciation MP3 for a word with specific accent.
        
        Args:
            word: The word to get pronunciation for
            accent: AccentType enum specifying the accent
            
        Returns:
            Path to the downloaded file if successful
            
        Raises:
            DownloadError: If download fails
            CacheError: If cached file is invalid
        """
        word = word.lower()
        cache_path = self._get_cache_path(word, accent)

        # Check cache first
        if self.config.use_cache and not self.config.force_download:
            if self._is_valid_cache(cache_path):
                logger.info(f"Using cached file: {cache_path}")
                return cache_path

        # Download if not cached or cache is invalid
        url = self.BASE_URL.format(word=word, accent=accent.value)

        try:
            logger.info(f"Downloading {accent.value} pronunciation for '{word}'...")
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()

            # Save the file
            cache_path.write_bytes(response.content)
            
            # Validate downloaded file
            if not self._is_valid_cache(cache_path):
                cache_path.unlink(missing_ok=True)  # Delete invalid file
                raise CacheError(f"Downloaded file for {word} is invalid")

            logger.info(f"Successfully downloaded: {cache_path}")
            return cache_path

        except RequestException as e:
            logger.error(f"Error downloading {url}: {str(e)}")
            raise DownloadError(f"Failed to download pronunciation for {word}") from e

    def clear_cache(self, word: str = None) -> None:
        """Clear cached files.
        
        Args:
            word: Optional specific word to clear cache for. If None, clears all cache.
        """
        try:
            if word:
                word_dir = self._ensure_output_dir(word.lower())
                if word_dir.exists():
                    for file in word_dir.glob("*.mp3"):
                        file.unlink()
                    word_dir.rmdir()
                    logger.info(f"Cleared cache for word: {word}")
            else:
                for word_dir in self.config.output_dir.iterdir():
                    if word_dir.is_dir():
                        for file in word_dir.glob("*.mp3"):
                            file.unlink()
                        word_dir.rmdir()
                logger.info("Cleared all cache")
        except OSError as e:
            logger.error(f"Error clearing cache: {e}")

    def get_cache_info(self, word: str = None) -> Dict:
        """Get information about cached files.
        
        Args:
            word: Optional specific word to get cache info for
            
        Returns:
            Dictionary with cache information
        """
        info = {}
        try:
            if word:
                word = word.lower()
                word_dir = self._ensure_output_dir(word)
                if word_dir.exists():
                    info[word] = {
                        accent.value: self._is_valid_cache(self._get_cache_path(word, accent))
                        for accent in AccentType
                    }
            else:
                for word_dir in self.config.output_dir.iterdir():
                    if word_dir.is_dir():
                        word = word_dir.name
                        info[word] = {
                            accent.value: self._is_valid_cache(self._get_cache_path(word, accent))
                            for accent in AccentType
                        }
        except OSError as e:
            logger.error(f"Error getting cache info: {e}")
        
        return info

    def download_all_accents(self, word: str) -> List[Path]:
        """Download pronunciations for a word in all available accents.
        
        Args:
            word: The word to get pronunciations for
            
        Returns:
            List of paths to downloaded files
            
        Raises:
            DownloadError: If any download fails
        """
        paths = []
        for accent in AccentType:
            path = self.download_pronunciation(word, accent)
            if path:
                paths.append(path)
        return paths

    def download_words(self, words: List[str], accent: AccentType = None) -> List[Path]:
        """Download pronunciations for multiple words.
        
        Args:
            words: List of words to process
            accent: Optional specific accent, if None downloads all accents
            
        Returns:
            List of paths to downloaded files
        """
        paths = []
        for word in words:
            try:
                if accent:
                    path = self.download_pronunciation(word, accent)
                    if path:
                        paths.append(path)
                else:
                    paths.extend(self.download_all_accents(word))
            except DownloadError as e:
                logger.error(f"Failed to process {word}: {str(e)}")
                continue
        return paths 
