import pytest
import sys, os
from unittest.mock import patch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from library_service import (
    return_book_by_patron
)


def test_return_book_not_implemented():
    """Test that return book function is implemented and responds properly."""
    # Should not raise TypeError and return tuple
    success, message = return_book_by_patron("123456", 1)
    assert isinstance(success, bool)
    assert isinstance(message, str)

def test_return_book_with_valid_patron():
    """Test valid patron trying to return book."""
    success, message = return_book_by_patron("123456", 1)
    # We expect the function to handle it without errors and provide a meaningful message
    assert isinstance(success, bool)
    assert isinstance(message, str)

def test_return_book_with_invalid_patron():
    """Test invalid patron ID should be rejected."""
    success, message = return_book_by_patron("12345", 1)
    assert success is False
    assert "invalid patron id" in message.lower()

def test_return_book_with_invalid_book():
    """Test invalid book ID should be rejected."""
    success, message = return_book_by_patron("123456", -1)
    assert success is False
    assert "book not found" in message.lower()

def test_return_book_returns_tuple():
    """Test return_book_by_patron returns a tuple."""
    result = return_book_by_patron("123456", 1)
    assert isinstance(result, tuple)
    assert len(result) == 2

def test_return_book_with_none_patron():
    """Test None patron ID should be rejected."""
    success, message = return_book_by_patron(None, 1)
    assert success is False
    assert "invalid patron id" in message.lower()

def test_return_book_with_string_book_id():
    """Test non-integer book_id should be rejected."""
    success, message = return_book_by_patron("123456", "abc")
    assert success is False
    assert "book not found" in message.lower()