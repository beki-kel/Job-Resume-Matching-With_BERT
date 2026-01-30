"""Custom exceptions"""


class AppException(Exception):
    """Base application exception"""
    pass


class ModelNotLoadedException(AppException):
    """Model not loaded exception"""
    pass


class ScraperNotAvailableException(AppException):
    """Scraper not available exception"""
    pass


class NoJobsFoundException(AppException):
    """No jobs found exception"""
    pass


class CacheException(AppException):
    """Cache operation exception"""
    pass
