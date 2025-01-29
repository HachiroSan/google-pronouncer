"""
Google Pronouncer Library
A library for downloading pronunciation MP3 files from Google's dictionary service.
"""

from .downloader import GooglePronunciationDownloader, DownloadConfig, AccentType, DownloadError

__version__ = "0.1.0"
__all__ = ['GooglePronunciationDownloader', 'DownloadConfig', 'AccentType', 'DownloadError'] 