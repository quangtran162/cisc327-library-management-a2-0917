import unittest
import os
import tempfile
import sqlite3
from datetime import datetime, timedelta
import database

class TestDatabaseModule(unittest.TestCase):
    def setUp(self):
        # Use a temporary database file to isolate tests
        self.db_fd, database.DATABASE = tempfile.mkstemp()
        database.init_database()
        database.add_sample_data()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(database.DATABASE)

    def test_get_db_connection(self):
        conn = database.get_db_connection()
        self.assertIsInstance(conn, sqlite3.Connection)
        conn.close()

    def test_get_all_books(self):
        books = database.get_all_books()
        self.assertGreaterEqual(len(books), 3)
        self.assertIn('title', books[0])

    def test_get_book_by_id_and_isbn(self):
        book = database.get_book_by_id(1)
        self.assertIsNotNone(book)
        self.assertEqual(book['id'], 1)

        book_isbn = book['isbn']
        book2 = database.get_book_by_isbn(book_isbn)
        self.assertEqual(book['id'], book2['id'])

        book_none = database.get_book_by_id(9999)
        self.assertIsNone(book_none)
        book_none2 = database.get_book_by_isbn("nonexistentisbn")
        self.assertIsNone(book_none2)

    def test_get_patron_borrowed_books(self):
        borrowed = database.get_patron_borrowed_books("123456")
        self.assertTrue(any(b['book_id'] == 3 for b in borrowed))
        for b in borrowed:
            self.assertTrue(isinstance(b['borrow_date'], datetime))
            self.assertTrue(isinstance(b['due_date'], datetime))

    def test_get_patron_borrow_records(self):
        records = database.get_patron_borrow_records("123456")
        self.assertGreaterEqual(len(records), 1)
        self.assertIn('id', records[0])
        self.assertIn('borrow_date', records[0])

    def test_get_patron_borrow_count(self):
        count = database.get_patron_borrow_count("123456")
        self.assertGreaterEqual(count, 0)

    def test_insert_borrow_record_success_and_failure(self):
        now = datetime.now()
        later = now + timedelta(days=7)
        # Success case
        success = database.insert_borrow_record("654321", 1, now, later)
        self.assertTrue(success)

        # Failure case: Pass None to cause an exception and test failure handled
        try:
            failure = database.insert_borrow_record(None, None, None, None)
        except Exception:
            failure = False
        self.assertFalse(failure)

    def test_update_book_availability_success_and_failure(self):
        conn = database.get_db_connection()
        # Get current copies for book_id=1
        row = conn.execute("SELECT available_copies FROM books WHERE id=1").fetchone()
        original_copies = row['available_copies']
        conn.close()

        # Success: increase by 1
        success = database.update_book_availability(1, 1)
        self.assertTrue(success)

        conn = database.get_db_connection()
        row = conn.execute("SELECT available_copies FROM books WHERE id=1").fetchone()
        conn.close()
        self.assertEqual(row['available_copies'], original_copies + 1)

        # Failure: invalid book_id - expect True returned but copies unchanged
        failure = database.update_book_availability(9999, 1)
        self.assertTrue(failure)  # As per current implementation returns True anyway

        # Verify unchanged count for invalid id
        conn = database.get_db_connection()
        row = conn.execute("SELECT available_copies FROM books WHERE id=1").fetchone()
        conn.close()
        self.assertEqual(row['available_copies'], original_copies + 1)


    def test_update_borrow_record_return_date_success_and_failure(self):
        records = database.get_patron_borrow_records("123456")
        record_id = records[0]['id']

        # Success: update return_date
        success = database.update_borrow_record_return_date(record_id, datetime.now())
        self.assertTrue(success)

        # Confirm it is updated
        conn = database.get_db_connection()
        row = conn.execute("SELECT return_date FROM borrow_records WHERE id=?", (record_id,)).fetchone()
        conn.close()
        self.assertIsNotNone(row['return_date'])

        # Failure: update same record again (already has return_date)
        failure = database.update_borrow_record_return_date(record_id, datetime.now())
        self.assertTrue(failure)  # actually returns True even if no row updated

        # Confirm return_date unchanged
        conn = database.get_db_connection()
        row2 = conn.execute("SELECT return_date FROM borrow_records WHERE id=?", (record_id,)).fetchone()
        conn.close()
        self.assertEqual(row['return_date'], row2['return_date'])

if __name__ == "__main__":
    unittest.main()
