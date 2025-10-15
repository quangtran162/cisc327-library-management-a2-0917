import pytest
import sys, os
from unittest.mock import patch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from library_service import (
    get_catalog_books
)


@patch('library_service.get_all_books')
def test_get_catalog_books_returns_list(mock_get_all_books):
    mock_get_all_books.return_value = []
    result = get_catalog_books()
    assert isinstance(result, list)

@patch('library_service.get_all_books')
def test_get_catalog_books_not_none(mock_get_all_books):
    mock_get_all_books.return_value = []
    result = get_catalog_books()
    assert result is not None

@patch('library_service.get_all_books')
def test_get_catalog_books_empty_catalog(mock_get_all_books):
    mock_get_all_books.return_value = []
    result = get_catalog_books()
    assert isinstance(result, list)
    assert len(result) == 0

@patch('library_service.get_all_books')
def test_get_catalog_books_with_data(mock_get_all_books):
    mock_get_all_books.return_value = [
        {
            'id': 1,
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '1234567890123',
            'available_copies': 3,
            'total_copies': 5
        },
        {
            'id': 2,
            'title': 'Another Book',
            'author': 'Another Author',
            'isbn': '1234567890124',
            'available_copies': 0,
            'total_copies': 2
        }
    ]
    result = get_catalog_books()
    assert isinstance(result, list)
    assert len(result) == 2
    assert all('id' in book for book in result)
    assert all('borrowable' in book for book in result)
    # Check borrowable boolean matches availability
    assert result[0]['borrowable'] is True
    assert result[1]['borrowable'] is False

@patch('library_service.get_all_books')
def test_get_catalog_books_single_book(mock_get_all_books):
    """Test catalog retrieval when there is exactly one book."""
    mock_get_all_books.return_value = [
        {
            'id': 1,
            'title': 'Solo Book',
            'author': 'Unique Author',
            'isbn': '1111111111111',
            'available_copies': 1,
            'total_copies': 1
        }
    ]
    result = get_catalog_books()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]['title'] == 'Solo Book'

@patch('library_service.get_all_books')
def test_get_catalog_books_no_available_copies(mock_get_all_books):
    """Test catalog where books have zero available copies (not borrowable)."""
    mock_get_all_books.return_value = [
        {
            'id': 2,
            'title': 'Unavailable Book',
            'author': 'No Copies',
            'isbn': '2222222222222',
            'available_copies': 0,
            'total_copies': 3
        }
    ]
    result = get_catalog_books()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]['borrowable'] is False