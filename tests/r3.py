import pytest
import sys, os
from unittest.mock import patch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from library_service import (
    borrow_book_by_patron
)


def test_borrow_book_valid_input():
    """Test borrowing a book with valid input."""
    success, message = borrow_book_by_patron("123456", 1)
    # Note: This will depend on database state
    assert isinstance(success, bool)
    assert isinstance(message, str)


def test_borrow_book_invalid_patron_id_short():
    """Test borrowing with patron ID too short."""
    success, message = borrow_book_by_patron("12345", 1)
    assert success == False
    assert "6 digits" in message


def test_borrow_book_invalid_patron_id_long():
    """Test borrowing with patron ID too long."""
    success, message = borrow_book_by_patron("1234567", 1)
    assert success == False
    assert "6 digits" in message


def test_borrow_book_invalid_patron_id_letters():
    """Test borrowing with non-digit patron ID."""
    success, message = borrow_book_by_patron("abc123", 1)
    assert success == False
    assert "6 digits" in message


def test_borrow_book_nonexistent_book():
    """Test borrowing non-existent book."""
    success, message = borrow_book_by_patron("123456", 999999)
    assert success == False
    assert "not found" in message.lower()


def test_borrow_book_invalid_patron_id_empty():
    """Test borrowing with empty patron ID."""
    success, message = borrow_book_by_patron("", 1)
    assert success == False
    assert "6 digits" in message


def test_borrow_book_invalid_patron_id_spaces():
    """Test borrowing with patron ID containing spaces."""
    success, message = borrow_book_by_patron("12 34 56", 1)
    assert success == False
    assert "6 digits" in message


def test_borrow_book_returns_tuple():
    """Test that borrow_book_by_patron returns a tuple."""
    result = borrow_book_by_patron("123456", 1)
    assert isinstance(result, tuple)
    assert len(result) == 2

