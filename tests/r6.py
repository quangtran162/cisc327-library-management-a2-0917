import pytest
import sys, os
from unittest.mock import patch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from library_service import (
    search_books_in_catalog
)


def test_search_books_not_implemented():
    """Test that search books returns empty list."""
    result = search_books_in_catalog("Python", "title")
    assert result == []
    assert isinstance(result, list)


def test_search_books_by_title():
    """Test searching books by title."""
    result = search_books_in_catalog("Python", "title")
    assert isinstance(result, list)
    assert result == []


def test_search_books_by_author():
    """Test searching books by author."""
    result = search_books_in_catalog("John Doe", "author")
    assert isinstance(result, list)
    assert result == []


def test_search_books_by_isbn():
    result = search_books_in_catalog("1234567890123", "isbn")
    assert isinstance(result, list)
    # Expects at least one matching book
    assert len(result) > 0
    assert all(book['isbn'] == "1234567890123" for book in result)



def test_search_books_empty_query():
    """Test search with empty search term."""
    result = search_books_in_catalog("", "title")
    assert isinstance(result, list)
    assert result == []


def test_search_books_invalid_search_type():
    """Test search with invalid search type."""
    result = search_books_in_catalog("Python", "invalid")
    assert isinstance(result, list)
    assert result == []


def test_search_books_none_query():
    """Test search with None search term."""
    result = search_books_in_catalog(None, "title")
    assert isinstance(result, list)
    assert result == []


def test_search_books_none_search_type():
    """Test search with None search type."""
    result = search_books_in_catalog("Python", None)
    assert isinstance(result, list)
    assert result == []

