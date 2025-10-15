import pytest
import sys, os
from unittest.mock import patch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from library_service import (
    add_book_to_catalog
)


@patch('library_service.get_book_by_isbn', return_value=None)
@patch('library_service.insert_book', return_value=True)
def test_add_book_valid_input(mock_insert, mock_get_isbn):
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    assert success is True
    assert "successfully added" in message.lower()

@patch('library_service.get_book_by_isbn', return_value=None)
@patch('library_service.insert_book', return_value=True)
def test_add_book_title_with_special_chars(mock_insert, mock_get_isbn):
    """Test adding book with special characters in title."""
    success, message = add_book_to_catalog("Python! @# $%", "Author", "1234567890124", 5)
    assert success is True
    assert "successfully added" in message.lower()

@patch('library_service.get_book_by_isbn', return_value=None)
@patch('library_service.insert_book', return_value=True)
def test_add_book_author_with_unicode(mock_insert, mock_get_isbn):
    """Test adding book with Unicode characters in author name."""
    success, message = add_book_to_catalog("Test Book", "作者", "1234567890125", 5)
    assert success is True
    assert "successfully added" in message.lower()

def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    assert success is False
    assert "13 digits" in message

def test_add_book_empty_title():
    """Test adding book with empty title."""
    success, message = add_book_to_catalog("", "Test Author", "1234567890126", 5)
    assert success is False
    assert "required" in message.lower()

@patch('library_service.get_book_by_isbn', return_value=None)
@patch('library_service.insert_book', return_value=True)
def test_add_book_large_total_copies(mock_insert, mock_get_isbn):
    """Test adding book with a very large number of copies."""
    success, message = add_book_to_catalog("Big Book", "Big Author", "1234567890127", 10000)
    assert success is True
    assert "successfully added" in message.lower()

def test_add_book_negative_copies():
    """Test adding book with negative copies."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890128", -1)
    assert success is False
    assert "positive" in message.lower()

def test_add_book_long_title():
    """Test adding book with title over 200 characters."""
    long_title = "A" * 201
    success, message = add_book_to_catalog(long_title, "Test Author", "1234567890129", 5)
    assert success is False
    assert "200 characters" in message

def test_add_book_empty_author():
    """Test adding book with empty author."""
    success, message = add_book_to_catalog("Test Book", "", "1234567890130", 5)
    assert success is False
    assert "author is required" in message.lower()

def test_add_book_long_author():
    """Test adding book with author name over 100 characters."""
    long_author = "A" * 101
    success, message = add_book_to_catalog("Test Book", long_author, "1234567890131", 5)
    assert success is False
    assert "100 characters" in message

def test_add_book_invalid_isbn_too_long():
    """Test adding a book with ISBN too long."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789012345", 5)
    assert success is False
    assert "13 digits" in message

def test_add_book_zero_copies():
    """Test adding book with zero copies."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890132", 0)
    assert success is False
    assert "positive" in message

@patch('library_service.get_book_by_isbn', return_value=None)
@patch('library_service.insert_book', return_value=True)
def test_add_book_isbn_with_leading_zeros(mock_insert, mock_get_isbn):
    """Test adding book with ISBN that has leading zeros."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "0000123456789", 5)
    assert success is True
    assert "successfully added" in message.lower()