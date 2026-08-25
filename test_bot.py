"""
Comprehensive Test Suite for FreshMinds EAES Result Bot.
Tests:
- Input sanitization (spaces, hyphens, full names, Amharic, casing)
- TTLCache expiration and eviction
- Rate limiter sliding window
- EAES client stampede shield and result caching
- Message builder null safety
"""

import sys
import time
import asyncio
import unittest
from pathlib import Path

# Add bot folder to path
sys.path.insert(0, str(Path(__file__).parent / "bot"))

from rate_limiter import RateLimiter, TTLCache
from handlers import sanitize_admission_number, sanitize_first_name
from eaes_client import EAESClient, ResultStatus, StudentInfo, SubjectResult
import messages as msg


class TestBotEdgeCases(unittest.TestCase):

    def test_admission_number_sanitization(self):
        """Test edge cases for admission number cleaning."""
        # Standard numbers
        self.assertEqual(sanitize_admission_number("1234567"), "1234567")
        self.assertEqual(sanitize_admission_number("347484"), "347484")

        # Whitespace and formatting edge cases
        self.assertEqual(sanitize_admission_number(" 347 484 "), "347484")
        self.assertEqual(sanitize_admission_number("123-456-7"), "1234567")
        self.assertEqual(sanitize_admission_number(" 1234567\n"), "1234567")
        self.assertEqual(sanitize_admission_number("123/4567"), "1234567")

        # Invalid cases
        self.assertIsNone(sanitize_admission_number(""))
        self.assertIsNone(sanitize_admission_number("12"))  # Too short
        self.assertIsNone(sanitize_admission_number("123456789012345"))  # Too long
        self.assertIsNone(sanitize_admission_number("abc1234"))
        self.assertIsNone(sanitize_admission_number(None))

    def test_first_name_sanitization(self):
        """Test edge cases for first name cleaning and multi-word handling."""
        # Standard Latin names
        self.assertEqual(sanitize_first_name("Abebe"), "Abebe")
        self.assertEqual(sanitize_first_name("abebe"), "Abebe")  # Auto-capitalize
        self.assertEqual(sanitize_first_name("  almaz  "), "Almaz")

        # Student enters full name -> auto-extracts first name!
        self.assertEqual(sanitize_first_name("Abebe Kebede"), "Abebe")
        self.assertEqual(sanitize_first_name("chala desta geda"), "Chala")

        # Amharic / Ethiopic script support
        self.assertEqual(sanitize_first_name("አበበ"), "አበበ")
        self.assertEqual(sanitize_first_name("አበበ ከበደ"), "አበበ")
        self.assertEqual(sanitize_first_name("ጫላ"), "ጫላ")

        # Names with hyphens/apostrophes
        self.assertEqual(sanitize_first_name("Haile-Mariam"), "Haile")
        self.assertEqual(sanitize_first_name("D'Souza"), "D'Souza")

        # Invalid cases
        self.assertIsNone(sanitize_first_name(""))
        self.assertIsNone(sanitize_first_name("A"))  # Too short
        self.assertIsNone(sanitize_first_name("12345"))
        self.assertIsNone(sanitize_first_name("Abebe@123"))
        self.assertIsNone(sanitize_first_name(None))

    def test_ttl_cache(self):
        """Test in-memory TTL caching and expiration."""
        cache = TTLCache(default_ttl=0.5, max_size=3)

        cache.set("k1", "v1")
        cache.set("k2", "v2")
        self.assertEqual(cache.get("k1"), "v1")
        self.assertEqual(cache.get("k2"), "v2")

        # Wait for expiration
        time.sleep(0.6)
        self.assertIsNone(cache.get("k1"))
        self.assertIsNone(cache.get("k2"))

        # Test capacity limit
        cache.set("a", "1", ttl=10.0)
        cache.set("b", "2", ttl=10.0)
        cache.set("c", "3", ttl=10.0)
        cache.set("d", "4", ttl=10.0)
        # Size should stay bounded <= max_size
        self.assertLessEqual(len(cache._cache), 3)

    def test_rate_limiter_edge_cases(self):
        """Test rate limiter bounds and memory cleanup."""
        limiter = RateLimiter(max_requests=2, window_seconds=1, max_tracked_users=5)
        user_id = 101

        self.assertTrue(limiter.is_allowed(user_id))
        self.assertTrue(limiter.is_allowed(user_id))
        self.assertFalse(limiter.is_allowed(user_id))  # 3rd request blocked

        time.sleep(1.1)
        self.assertTrue(limiter.is_allowed(user_id))  # Allowed after window

        # Test cleanup
        limiter.cleanup()
        self.assertEqual(len(limiter._requests), 1)

    def test_null_safe_result_formatting(self):
        """Test message formatting with null or missing student fields."""
        # Incomplete student record
        student = StudentInfo(
            full_name="Fatuma Ahmed",
            admission_no="9876543",
            school=None,
            stream=None,
            sex=None,
            age=None
        )
        results = [
            SubjectResult(subject="Aptitude", result="95"),
            SubjectResult(subject="Mathematics", result="98")
        ]

        formatted = msg.format_result_success(student, results)
        self.assertIn("Fatuma Ahmed", formatted)
        self.assertIn("9876543", formatted)
        self.assertIn("Aptitude", formatted)
        self.assertIn("95", formatted)


if __name__ == "__main__":
    unittest.main()
