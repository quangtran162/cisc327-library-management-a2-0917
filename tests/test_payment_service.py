import unittest
from services.payment_service import PaymentGateway

class TestPaymentGateway(unittest.TestCase):
    def setUp(self):
        self.gateway = PaymentGateway()

    def test_process_payment_success(self):
        success, txn_id, msg = self.gateway.process_payment("123456", 20.0, "Test payment")
        self.assertTrue(success)
        self.assertTrue(txn_id.startswith("txn_"))
        self.assertIn("processed successfully", msg)

    def test_process_payment_invalid_amount(self):
        success, txn_id, msg = self.gateway.process_payment("123456", -10, "Invalid amount")
        self.assertFalse(success)

    def test_process_payment_invalid_patron_id(self):
        success, txn_id, msg = self.gateway.process_payment("123", 10, "Invalid patron")
        self.assertFalse(success)

    def test_refund_payment_success(self):
        success, msg = self.gateway.refund_payment("txn_123456_1234567890", 10)
        self.assertTrue(success)
        self.assertIn("Refund of $10.00 processed successfully", msg)

    def test_refund_payment_invalid_transaction_id(self):
        success, msg = self.gateway.refund_payment("invalid_txn", 10)
        self.assertFalse(success)

    def test_refund_payment_invalid_amount(self):
        success, msg = self.gateway.refund_payment("txn_123456_1234567890", -5)
        self.assertFalse(success)
        
    def test_process_payment_invalid_amount_and_patron(self):
        gateway = PaymentGateway()

        # Amount zero - should fail
        success, txn_id, msg = gateway.process_payment("123456", 0, "desc")
        self.assertFalse(success)

        # Amount negative - should fail
        success, txn_id, msg = gateway.process_payment("123456", -10, "desc")
        self.assertFalse(success)

        # Invalid patron ID length - valid amount but patron_id length != 6
        success, txn_id, msg = gateway.process_payment("12345", 10, "desc")
        self.assertFalse(success)


if __name__ == '__main__':
    unittest.main()
