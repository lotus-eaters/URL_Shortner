"""
URL Utilities
Handles URL shortening, validation, and alias generation
"""

import logging
import hashlib
import string
import random
from urllib.parse import urlparse
from typing import Tuple

logger = logging.getLogger(__name__)


class URLUtils:
    """Utility class for URL operations"""
    
    # Available characters for short codes (alphanumeric)
    CHARSET = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate if URL is a valid HTTP/HTTPS URL
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Example:
            >>> URLUtils.validate_url("https://www.example.com")
            True
            >>> URLUtils.validate_url("not a url")
            False
        """
        try:
            # Convert Pydantic URL to string if needed
            url_str = str(url)
            result = urlparse(url_str)
            # Check if scheme is http/https and netloc exists
            is_valid = all([
                result.scheme in ['http', 'https'],
                result.netloc
            ])
            return is_valid
        except Exception as e:
            logger.warning(f"URL validation error: {str(e)}")
            return False
    
    @staticmethod
    def generate_short_code_md5(original_url: str, custom_alias: str = None) -> str:
        """
        Generate a short code using MD5 hashing
        
        Args:
            original_url (str): Original URL to shorten
            custom_alias (str): Optional custom alias (takes precedence)
            
        Returns:
            str: Generated short code (6-8 characters)
            
        Example:
            >>> code = URLUtils.generate_short_code_md5("https://www.example.com")
            >>> len(code) >= 6
            True
            
            >>> custom = URLUtils.generate_short_code_md5("https://...", "mycode")
            >>> custom
            'mycode'
        """
        try:
            # Convert Pydantic URL to string if needed
            url_str = str(original_url)
            
            # If custom alias provided, use it
            if custom_alias:
                logger.debug(f"Using custom alias: {custom_alias}")
                return custom_alias
            
            # MD5 hash the URL
            md5_hash = hashlib.md5(url_str.encode()).hexdigest()
            
            # Convert hex to base62-like (using our charset)
            # Take first 8 characters of hash and map to charset
            short_code = URLUtils._hex_to_short_code(md5_hash[:8])
            
            logger.debug(f"Generated short code: {short_code} from {original_url}")
            return short_code
            
        except Exception as e:
            logger.error(f"Error generating short code: {str(e)}")
            raise
    
    @staticmethod
    def _hex_to_short_code(hex_string: str, length: int = 6) -> str:
        """
        Convert hex string to short code using charset
        
        Args:
            hex_string (str): Hex string (usually MD5 hash)
            length (int): Desired length of short code
            
        Returns:
            str: Short code
            
        Example:
            >>> code = URLUtils._hex_to_short_code("abc123def456")
            >>> len(code) == 6
            True
        """
        # Convert hex to integer
        num = int(hex_string, 16)
        charset = URLUtils.CHARSET
        short_code = ""
        
        for _ in range(length):
            short_code = charset[num % len(charset)] + short_code
            num //= len(charset)
        
        return short_code
    
    @staticmethod
    def generate_fallback_short_code(length: int = 6) -> str:
        """
        Generate random short code as fallback for collisions
        
        Args:
            length (int): Length of short code to generate (default 6)
            
        Returns:
            str: Random short code
            
        Example:
            >>> code = URLUtils.generate_fallback_short_code()
            >>> len(code) == 6
            True
        """
        charset = URLUtils.CHARSET
        return ''.join(random.choice(charset) for _ in range(length))
    
    @staticmethod
    def get_domain(url: str) -> str:
        """
        Extract domain from URL
        
        Args:
            url (str): URL to extract domain from
            
        Returns:
            str: Domain name
            
        Example:
            >>> URLUtils.get_domain("https://www.example.com/path")
            'www.example.com'
        """
        try:
            result = urlparse(url)
            return result.netloc
        except Exception as e:
            logger.error(f"Error extracting domain: {str(e)}")
            return ""
    
    @staticmethod
    def is_url_expired(expires_at) -> bool:
        """
        Check if URL expiration date has passed
        
        Args:
            expires_at: Expiration datetime
            
        Returns:
            bool: True if expired, False otherwise
            
        Example:
            >>> from datetime import datetime, timedelta
            >>> past = datetime.utcnow() - timedelta(days=1)
            >>> URLUtils.is_url_expired(past)
            True
        """
        from datetime import datetime
        
        if expires_at is None:
            return False
        
        # Handle both timezone-aware and naive datetimes
        try:
            if expires_at.tzinfo is not None:
                # Timezone-aware datetime
                from datetime import timezone
                now = datetime.now(timezone.utc)
            else:
                # Naive datetime
                now = datetime.utcnow()
            
            return expires_at < now
        except Exception as e:
            logger.error(f"Error checking expiration: {str(e)}")
            return False
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalize URL for consistency
        (Remove trailing slash, lowercase scheme and domain)
        
        Args:
            url (str): URL to normalize
            
        Returns:
            str: Normalized URL
            
        Example:
            >>> URLUtils.normalize_url("HTTPS://EXAMPLE.COM/PATH/")
            'https://example.com/PATH/'
        """
        try:
            # Convert Pydantic URL to string if needed
            url_str = str(url)
            result = urlparse(url_str)
            
            # Lowercase scheme and netloc, keep path as-is
            normalized = f"{result.scheme.lower()}://{result.netloc.lower()}{result.path}"
            
            # Add query and fragment if present
            if result.query:
                normalized += f"?{result.query}"
            if result.fragment:
                normalized += f"#{result.fragment}"
            
            return normalized
        except Exception as e:
            logger.error(f"Error normalizing URL: {str(e)}")
            return url
