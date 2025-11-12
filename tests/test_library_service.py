import unittest
from unittest.mock import patch, Mock
from services.library_service import (
    add_book_to_catalog, borrow_book_by_patron, return_book_by_patron,
    calculate_late_fee_for_book, pay_late_fees, refund_late_fee_payment)

class TestLibraryService(unittest.TestCase):
    @patch('services.library_service.get_book_by_isbn')
    @patch('services.library_service.insert_book')
    def test_add_book_to_catalog_success(self, mock_insert, mock_get_isbn):
        mock_get_isbn.return_value = None
        mock_insert.return_value = True
        success, msg = add_book_to_catalog("Test Title", "Author", "1234567890123", 3)
        self.assertTrue(success)
        self.assertIn("successfully added", msg)

    @patch('services.library_service.get_book_by_isbn')
    def test_add_book_to_catalog_duplicate_isbn(self, mock_get_isbn):
        mock_get_isbn.return_value = {"isbn": "1234567890123"}
        success, msg = add_book_to_catalog("Title", "Author", "1234567890123", 1)
        self.assertFalse(success)
        self.assertIn("ISBN already exists", msg)

    @patch('services.library_service.get_book_by_id')
    @patch('services.library_service.get_patron_borrow_count')
    @patch('services.library_service.insert_borrow_record')
    @patch('services.library_service.update_book_availability')
    def test_borrow_book_by_patron_success(self, mock_update_avail, mock_insert_borrow,
                                          mock_borrow_count, mock_get_book):
        mock_get_book.return_value = {'id': 1, 'title': 'Book', 'available_copies': 1}
        mock_borrow_count.return_value = 0
        mock_insert_borrow.return_value = True
        mock_update_avail.return_value = True
        success, msg = borrow_book_by_patron("123456", 1)
        self.assertTrue(success)
        self.assertIn("Successfully borrowed", msg)

    @patch('services.library_service.get_patron_borrow_records')
    @patch('services.library_service.get_book_by_id')
    @patch('services.library_service.update_borrow_record_return_date')
    @patch('services.library_service.update_book_availability')
    def test_return_book_by_patron_on_time(self, mock_update_avail, mock_update_return,
                                           mock_get_book, mock_get_borrows):
        mock_get_book.return_value = {'id': 1, 'title': 'Test Book'}
        mock_get_borrows.return_value = [{
            'id': 123,                    # add this id field
            'book_id': 1,
            'return_date': None,
            'due_date': '2099-01-01T00:00:00'  # future date, no late fee
        }]
        mock_update_return.return_value = True
        mock_update_avail.return_value = True
        success, msg = return_book_by_patron("123456", 1)
        self.assertTrue(success)
        self.assertIn("returned successfully on time", msg)

    @patch('services.library_service.calculate_late_fee_for_book')
    @patch('services.library_service.get_book_by_id')
    @patch('services.library_service.PaymentGateway')
    def test_pay_late_fees_success(self, MockGateway, mock_get_book, mock_calc_fee):
        mock_calc_fee.return_value = {'fee_amount': 5.0}
        mock_get_book.return_value = {'title': 'Book'}
        mock_gateway_instance = MockGateway.return_value
        mock_gateway_instance.process_payment.return_value = (True, "txn_123", "Success")
        success, msg, txn_id = pay_late_fees("123456", 1, payment_gateway=mock_gateway_instance)
        self.assertTrue(success)
        self.assertEqual(txn_id, "txn_123")

    @patch('services.library_service.PaymentGateway')
    def test_refund_late_fee_payment_success(self, MockGateway):
        mock_gateway_instance = MockGateway.return_value
        mock_gateway_instance.refund_payment.return_value = (True, "Refund successful")
        from services.library_service import refund_late_fee_payment
        success, msg = refund_late_fee_payment("txn_123", 5.0, payment_gateway=mock_gateway_instance)
        self.assertTrue(success)
        self.assertIn("Refund successful", msg)


    @patch('services.library_service.get_book_by_isbn')
    @patch('services.library_service.insert_book') 
    def test_add_book_to_catalog_invalid_inputs(self, mock_get_isbn, mock_insert):
        mock_get_isbn.return_value = None
        mock_insert.return_value = True

        # Empty title
        success, msg = add_book_to_catalog("", "Author", "1234567890123", 1)
        self.assertFalse(success)

        # Title too long
        success, msg = add_book_to_catalog("T"*201, "Author", "1234567890123", 1)
        self.assertFalse(success)

        # Author too long
        success, msg = add_book_to_catalog("Title", "A"*101, "1234567890123", 1)
        self.assertFalse(success)

        # ISBN wrong length
        success, msg = add_book_to_catalog("Title", "Author", "12345", 1)
        self.assertFalse(success)

        # total_copies <= 0
        success, msg = add_book_to_catalog("Title", "Author", "1234567890123", 0)
        self.assertFalse(success)

    @patch('services.library_service.get_book_by_id')
    @patch('services.library_service.get_patron_borrow_count')
    def test_borrow_book_limit_and_invalid_cases(self, mock_borrow_count, mock_get_book):
        # Invalid patron ID
        success, msg = borrow_book_by_patron("abc", 1)
        self.assertFalse(success)

        # Book not found
        mock_get_book.return_value = None
        success, msg = borrow_book_by_patron("123456", 1)
        self.assertFalse(success)

        # Borrow limit reached
        mock_get_book.return_value = {'available_copies': 1}
        mock_borrow_count.return_value = 5
        success, msg = borrow_book_by_patron("123456", 1)
        self.assertFalse(success)

    @patch('services.library_service.get_patron_borrow_records')
    @patch('services.library_service.get_book_by_id')
    @patch('services.library_service.update_borrow_record_return_date')
    @patch('services.library_service.update_book_availability')
    def test_return_book_by_patron_edge_cases(self, mock_update_avail, mock_update_return, mock_get_book, mock_get_borrows):
        # No active borrow record found
        mock_get_book.return_value = {'id': 1, 'title': 'Test Book'}
        mock_get_borrows.return_value = []
        success, msg = return_book_by_patron("123456", 1)
        self.assertFalse(success)

        # Fail update borrow record return date
        mock_get_borrows.return_value = [{'id': 123, 'book_id': 1, 'return_date': None, 'duedate': '2099-01-01T00:00:00'}]
        mock_update_return.return_value = False
        mock_update_avail.return_value = True
        success, msg = return_book_by_patron("123456", 1)
        self.assertFalse(success)

    @patch('services.library_service.calculate_late_fee_for_book')
    def test_pay_late_fees_edge_cases(self, mock_calc_fee):
        # No late fee to pay
        mock_calc_fee.return_value = {'fee_amount': 0}
        success, msg, txn_id = pay_late_fees("123456", 1, payment_gateway=None)
        self.assertFalse(success)


if __name__ == '__main__':
    unittest.main()
