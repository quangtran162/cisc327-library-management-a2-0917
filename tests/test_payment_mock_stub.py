import unittest
from unittest.mock import Mock, patch
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway

class TestPaymentFunctions(unittest.TestCase):

    @patch('services.library_service.calculate_late_fee_for_book')
    @patch('services.library_service.get_book_by_id')
    def test_pay_late_fees_success(self, mock_get_book, mock_calc_fee):
        mock_calc_fee.return_value = {"fee_amount": 10.0}
        mock_get_book.return_value = {"title": "Example Book"}
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = (True, "txn_123", "Success")

        success, message, txn_id = pay_late_fees("123456", 1, mock_gateway)

        self.assertTrue(success)
        self.assertIn("Payment successful", message)
        self.assertEqual(txn_id, "txn_123")
        mock_gateway.process_payment.assert_called_once_with(
            patron_id="123456",
            amount=10.0,
            description="Late fees for 'Example Book'"
        )

    def test_pay_late_fees_invalid_patron(self):
        mock_gateway = Mock(spec=PaymentGateway)

        success, message, txn_id = pay_late_fees("12345a", 1, mock_gateway)

        self.assertFalse(success)
        self.assertIn("Invalid patron ID", message)
        self.assertIsNone(txn_id)
        mock_gateway.process_payment.assert_not_called()

    @patch('services.library_service.calculate_late_fee_for_book')
    def test_pay_late_fees_no_fee(self, mock_calc_fee):
        mock_calc_fee.return_value = {"fee_amount": 0}
        mock_gateway = Mock(spec=PaymentGateway)

        success, message, txn_id = pay_late_fees("123456", 1, mock_gateway)

        self.assertFalse(success)
        self.assertIn("No late fees to pay", message)
        self.assertIsNone(txn_id)
        mock_gateway.process_payment.assert_not_called()

    def test_refund_late_fee_payment_success(self):
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.refund_payment.return_value = (True, "Refund succeeded")

        success, message = refund_late_fee_payment("txn_123", 5.00, mock_gateway)

        self.assertTrue(success)
        self.assertIn("Refund succeeded", message)
        mock_gateway.refund_payment.assert_called_once_with("txn_123", 5.00)

    def test_refund_late_fee_payment_invalid_transactionid(self):
        mock_gateway = Mock(spec=PaymentGateway)

        success, message = refund_late_fee_payment("1234", 5.00, mock_gateway)

        self.assertFalse(success)
        self.assertIn("Invalid transaction ID", message)
        mock_gateway.refund_payment.assert_not_called()

    def test_refund_late_fee_payment_amount_exceeds(self):
        mock_gateway = Mock(spec=PaymentGateway)

        success, message = refund_late_fee_payment("txn_123", 20.00, mock_gateway)

        self.assertFalse(success)
        self.assertIn("Refund amount exceeds maximum late fee", message)
        mock_gateway.refund_payment.assert_not_called()

if __name__ == "__main__":
    unittest.main()
