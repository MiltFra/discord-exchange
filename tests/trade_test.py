import unittest
from discord_exchange import Trade


class TradeTest(unittest.TestCase):

    def test_trade_sequence(self):
        trade1 = Trade(0, 1, 5, 10)
        self.assertEqual(trade1.buyer, 0)
        self.assertEqual(trade1.seller, 1)
        self.assertEqual(trade1.price, 5)
        self.assertEqual(trade1.volume, 10)

        trade2 = Trade(0, 1, 5, 10)
        self.assertEqual(trade2.buyer, 0)
        self.assertEqual(trade2.seller, 1)
        self.assertEqual(trade2.price, 5)
        self.assertEqual(trade2.volume, 10)

        self.assertLess(trade1.id, trade2.id)
        self.assertLess(trade2.id, Trade.num_trades)

    def test_binary_value(self):
        t = Trade(0, 1, 5, 10)
        self.assertEqual(t.buyer, 0)
        self.assertEqual(t.seller, 1)
        self.assertEqual(t.price, 5)
        self.assertEqual(t.volume, 10)

        self.assertEqual(t.binary_value(5), 0)
        self.assertEqual(t.binary_value(7), 10)
        self.assertEqual(t.binary_value(3), -10)

    def test_true_value(self):
        t = Trade(0, 1, 5, 10)
        self.assertEqual(t.buyer, 0)
        self.assertEqual(t.seller, 1)
        self.assertEqual(t.price, 5)
        self.assertEqual(t.volume, 10)

        self.assertEqual(t.true_value(5), 0)
        self.assertEqual(t.true_value(7), 20)
        self.assertEqual(t.true_value(3), -20)

    @unittest.expectedFailure
    def test_zero_volume(self):
        t = Trade(0, 1, 5, 0)
    
    @unittest.expectedFailure
    def test_negative_volume(self):
        t = Trade(0, 1, 5, -10)
