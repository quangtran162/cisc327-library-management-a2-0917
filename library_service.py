"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrow_records
)


def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13 or not isbn.isdigit():
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."


def get_catalog_books() -> List[Dict]:
    """
    Retrieve all books for catalog display.
    Implements R2: Book Catalog Display
    
    Returns:
        List of dicts with book info including availability and total copies.
    """
    books = get_all_books()  # Retrieve all book records from database
    # Format each book as needed
    catalog = []
    for book in books:
        catalog.append({
            'id': book['id'],
            'title': book['title'],
            'author': book['author'],
            'isbn': book['isbn'],
            'available_copies': book['available_copies'],
            'total_copies': book['total_copies'],
            'borrowable': book['available_copies'] > 0
        })
    return catalog


def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    # Borrowing limit is max 5 books
    if current_borrowed >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

  
def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    Implements R4 as per requirements
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to return
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    # Find the active borrow record for this patron and book
    borrow_records = get_patron_borrow_records(patron_id)
    active_record = None
    
    for record in borrow_records:
        if record['book_id'] == book_id and record['return_date'] is None:
            active_record = record
            break
    
    if not active_record:
        return False, "No active borrow record found for this book and patron."
    
    # Update the borrow record with return date
    return_date = datetime.now()
    update_success = update_borrow_record_return_date(active_record['id'], return_date)
    
    if not update_success:
        return False, "Database error occurred while updating return record."
    
    # Update book availability
    availability_success = update_book_availability(book_id, 1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    # Calculate if there are any late fees
    due_date = datetime.fromisoformat(active_record['due_date'])

    days_late = max(0, (return_date - due_date).days)
    
    if days_late > 0:
        late_fee = days_late * 0.50  # $0.50 per day late
        return True, f'Book "{book["title"]}" returned successfully. Late fee: ${late_fee:.2f} ({days_late} days late).'
    else:
        return True, f'Book "{book["title"]}" returned successfully on time.'


def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    Implements R5 as per requirements
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to check late fees for
        
    Returns:
        Dict with fee information or None if no record found
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return None
    
    # Check if book exists
    book = get_book_by_id(book_id)
    if not book:
        return None
    
    # Find the borrow record for this patron and book
    borrow_records = get_patron_borrow_records(patron_id)
    target_record = None
    
    for record in borrow_records:
        if record['book_id'] == book_id and record['return_date'] is None:
            target_record = record
            break
    
    if not target_record:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'No active borrow record found'
        }
    
    # Calculate late fee
    due_date = datetime.fromisoformat(active_record['due_date'])

    current_date = datetime.now()
    days_overdue = max(0, (current_date - due_date).days)
    
    fee_amount = days_overdue * 0.50  # $0.50 per day late
    
    return {
        'fee_amount': round(fee_amount, 2),
        'days_overdue': days_overdue,
        'status': 'Current' if days_overdue == 0 else 'Overdue'
    }


def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    Implements R6 as per requirements
    
    Args:
        search_term: Term to search for
        search_type: Type of search ('title', 'author', 'isbn')
        
    Returns:
        List of matching books
    """
    if not search_term or not search_term.strip():
        return []

    if not search_type:
        return []

    search_term = search_term.strip().lower()
    search_type = search_type.lower()

    # Get all books from the database
    all_books = get_all_books()
    matching_books = []

    for book in all_books:
        if search_type == 'title':
            if search_term in book['title'].lower():
                matching_books.append(book)
        elif search_type == 'author':
            if search_term in book['author'].lower():
                matching_books.append(book)
        elif search_type == 'isbn':
            if search_term in book['isbn']:
                matching_books.append(book)

    return matching_books


def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    Implements R7 as per requirements

    Args:
        patron_id: 6-digit library card ID

    Returns:
        Dict with patron status information
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            'error': 'Invalid patron ID. Must be exactly 6 digits.',
            'patron_id': patron_id
        }

    # Get patron's borrow records
    borrow_records = get_patron_borrow_records(patron_id)

    # Separate active and returned books
    active_borrows = []
    returned_books = []
    total_late_fees = 0.00

    for record in borrow_records:
        book = get_book_by_id(record['book_id'])
        record_info = {
            'book_id': record['book_id'],
            'book_title': book['title'] if book else 'Unknown',
            'borrow_date': record['borrow_date'],
            'due_date': record['due_date']
        }

        if record['return_date'] is None:
            # Active borrow - check for late fees
            due_date = datetime.fromisoformat(record['due_date'])
            return_date = datetime.now()
            days_late = max(0, (return_date - due_date).days)
            late_fee = days_late * 0.50  # $0.50 per day late
            record_info['days_late'] = days_late
            record_info['late_fee'] = late_fee
            active_borrows.append(record_info)
            total_late_fees += late_fee
        else:
            returned_books.append(record_info)

    return {
        'patron_id': patron_id,
        'active_borrows': active_borrows,
        'returned_books': returned_books,
        'total_late_fees': total_late_fees
    }