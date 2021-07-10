import unittest
from discord_exchange import Order


class OrderTest(unittest.TestCase):
    def test_order_types(self):
        self.assertNotEqual(Order.TYPE_BID, Order.TYPE_ASK)

    def test_update_volume_default(self):
        order = Order(Order.TYPE_BID, 0, 5, 10)
        self.assertEqual(order.type, Order.TYPE_BID)
        self.assertEqual(order.issuer, 0)
        self.assertEqual(order.price, 5)
        self.assertEqual(order.volume, 10)

        order.update_volume(5)
        self.assertEqual(order.volume, 5)

    def test_reduce_volume_default(self):
        order = Order(Order.TYPE_BID, 0, 5, 10)
        self.assertEqual(order.type, Order.TYPE_BID)
        self.assertEqual(order.issuer, 0)
        self.assertEqual(order.price, 5)
        self.assertEqual(order.volume, 10)

        order.reduce_volume(3)
        self.assertEqual(order.volume, 7)
