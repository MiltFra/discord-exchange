import unittest
from discord_exchange import Orderbook, Order


class OrderbookTest(unittest.TestCase):
    def test_initial_status(self):
        ob = Orderbook()
        self.assertTrue(ob.bid_prices.empty())
        self.assertTrue(ob.ask_prices.empty())
        self.assertDictEqual(ob.bids, {})
        self.assertDictEqual(ob.asks, {})
        self.assertEqual(ob.total_bid_volume, 0)
        self.assertEqual(ob.total_ask_volume, 0)
        self.assertDictEqual(ob.users, {})

    def test_basic_bid_insertions(self):
        ob = Orderbook()

        ob.insert_bid(0, 5, 1)
        self.assertFalse(ob.bid_prices.empty())
        self.assertTrue(ob.ask_prices.empty())
        self.assertEqual(len(ob.bids[5]), 1)
        self.assertDictEqual(ob.asks, {})
        self.assertEqual(ob.total_bid_volume, 1)
        self.assertEqual(ob.total_ask_volume, 0)
        self.assertEqual(len(ob.users.keys()), 1)
        best_bid = ob.best_bid()
        self.assertEqual(best_bid.user_id, 0)
        self.assertEqual(best_bid.price, 5)
        self.assertEqual(best_bid.volume, 1)
        best_ask = ob.best_ask()
        self.assertIsNone(best_ask)

        ob.insert_bid(1, 5, 1)
        best_bid = ob.best_bid()
        self.assertEqual(best_bid.user_id, 0)
        self.assertEqual(best_bid.price, 5)
        self.assertEqual(best_bid.volume, 1)
        best_ask = ob.best_ask()
        self.assertIsNone(best_ask)

        ob.insert_bid(2, 6, 1)
        best_bid = ob.best_bid()
        self.assertEqual(best_bid.user_id, 2)
        self.assertEqual(best_bid.price, 6)
        self.assertEqual(best_bid.volume, 1)
        best_ask = ob.best_ask()
        self.assertIsNone(best_ask)

    def test_basic_insertions_best_bids(self):
        ob = Orderbook()

        ob.insert_bid(0, 5, 1)
        best_bid = ob.best_bid()
        best_ask = ob.best_ask()

        self.assertEqual(best_bid.user_id, 0)
        self.assertEqual(best_bid.price, 5)
        self.assertEqual(best_bid.volume, 1)
        self.assertIsNone(best_ask)

        ob.insert_bid(1, 5, 1)
        best_bid = ob.best_bid()
        best_ask = ob.best_ask()

        self.assertEqual(best_bid.user_id, 0)
        self.assertEqual(best_bid.price, 5)
        self.assertEqual(best_bid.volume, 1)
        self.assertIsNone(best_ask)

        ob.insert_bid(2, 6, 1)
        best_bid = ob.best_bid()
        best_ask = ob.best_ask()

        self.assertEqual(best_bid.user_id, 2)
        self.assertEqual(best_bid.price, 6)
        self.assertEqual(best_bid.volume, 1)
        self.assertIsNone(best_ask)

    def test_basic_insertions_internal_state(self):
        ob = Orderbook()
        ob.insert_bid(0, 5, 1)

        self.assertFalse(ob.bid_prices.empty())
        self.assertTrue(ob.ask_prices.empty())
        self.assertEqual(len(ob.bids[5]), 1)
        self.assertDictEqual(ob.asks, {})
        self.assertEqual(ob.total_bid_volume, 1)
        self.assertEqual(ob.total_ask_volume, 0)
        self.assertEqual(len(ob.get_user(0).bids), 1)
        self.assertEqual(len(ob.get_bids_at_price(5)), 1)
        self.assertEqual(len(ob.get_user(0).asks), 0)
        self.assertEqual(ob.get_user(0).bid_volume, 1)
        self.assertEqual(ob.get_user(0).ask_volume, 0)

        ob.insert_bid(1, 5, 1)

        self.assertFalse(ob.bid_prices.empty())
        self.assertTrue(ob.ask_prices.empty())
        self.assertEqual(ob.total_bid_volume, 2)
        self.assertEqual(ob.total_ask_volume, 0)
        self.assertEqual(len(ob.get_user(0).bids), 1)
        self.assertEqual(len(ob.get_user(1).bids), 1)
        self.assertEqual(len(ob.get_bids_at_price(5)), 2)
        self.assertEqual(len(ob.get_asks_at_price(5)), 0)
        self.assertEqual(len(ob.get_user(0).asks), 0)
        self.assertEqual(len(ob.get_user(1).asks), 0)
        self.assertEqual(ob.get_user(0).bid_volume, 1)
        self.assertEqual(ob.get_user(1).bid_volume, 1)
        self.assertEqual(ob.get_user(0).ask_volume, 0)
        self.assertEqual(ob.get_user(1).ask_volume, 0)

        ob.insert_bid(0, 5, 2)

        self.assertFalse(ob.bid_prices.empty())
        self.assertTrue(ob.ask_prices.empty())
        self.assertEqual(ob.total_bid_volume, 4)
        self.assertEqual(ob.total_ask_volume, 0)
        self.assertEqual(len(ob.get_user(0).bids), 2)
        self.assertEqual(len(ob.get_user(1).bids), 1)
        self.assertEqual(len(ob.get_bids_at_price(5)), 3)
        self.assertEqual(len(ob.get_asks_at_price(5)), 0)
        self.assertEqual(len(ob.get_user(0).asks), 0)
        self.assertEqual(len(ob.get_user(1).asks), 0)
        self.assertEqual(ob.get_user(0).bid_volume, 3)
        self.assertEqual(ob.get_user(1).bid_volume, 1)
        self.assertEqual(ob.get_user(0).ask_volume, 0)
        self.assertEqual(ob.get_user(1).ask_volume, 0)

    def test_full_matching_trades(self):
        """
        If there are orders with the same price and volume on both 
        the ask and bid sides, we expect a trade.
        """
        ob = Orderbook()
        t1 = ob.insert_bid(0, 5, 2)
        t2 = ob.insert_ask(1, 5, 2)

        self.assertListEqual(t1, [])
        self.assertEqual(len(t2), 1)
        self.assertEqual(t2[0].buyer, 0)
        self.assertEqual(t2[0].seller, 1)
        self.assertEqual(t2[0].price, 5)
        self.assertEqual(t2[0].volume, 2)

        ob = Orderbook()
        t1 = ob.insert_ask(1, 5, 2)
        t2 = ob.insert_bid(0, 5, 2)

        self.assertListEqual(t1, [])
        self.assertEqual(len(t2), 1)
        self.assertEqual(t2[0].buyer, 0)
        self.assertEqual(t2[0].seller, 1)
        self.assertEqual(t2[0].price, 5)
        self.assertEqual(t2[0].volume, 2)

    def test_partial_matching_trades(self):
        """
        If there are orders with the same price on both the ask
        and bid sides, we expect a trade of the smaller volume.
        """
        ob = Orderbook()
        t1 = ob.insert_bid(0, 5, 2)
        t2 = ob.insert_ask(1, 5, 1)

        self.assertListEqual(t1, [])
        self.assertEqual(len(t2), 1)
        self.assertEqual(t2[0].buyer, 0)
        self.assertEqual(t2[0].seller, 1)
        self.assertEqual(t2[0].price, 5)
        self.assertEqual(t2[0].volume, 1)

        ob = Orderbook()
        t1 = ob.insert_ask(1, 5, 2)
        t2 = ob.insert_bid(0, 5, 1)

        self.assertListEqual(t1, [])
        self.assertEqual(len(t2), 1)
        self.assertEqual(t2[0].buyer, 0)
        self.assertEqual(t2[0].seller, 1)
        self.assertEqual(t2[0].price, 5)
        self.assertEqual(t2[0].volume, 1)

    def test_full_crossing_trades(self):
        """
        If the best bid is higher than the best ask and volumes
        match, we expect a trade over the full volume at the price
        of the first order.
        """
        ob = Orderbook()
        t1 = ob.insert_bid(0, 5, 2)
        t2 = ob.insert_ask(1, 4, 2)

        self.assertListEqual(t1, [])
        self.assertEqual(len(t2), 1)
        self.assertEqual(t2[0].buyer, 0)
        self.assertEqual(t2[0].seller, 1)
        self.assertEqual(t2[0].price, 5)
        self.assertEqual(t2[0].volume, 2)

        ob = Orderbook()
        t1 = ob.insert_ask(1, 4, 2)
        t2 = ob.insert_bid(0, 5, 2)

        self.assertListEqual(t1, [])
        self.assertEqual(len(t2), 1)
        self.assertEqual(t2[0].buyer, 0)
        self.assertEqual(t2[0].seller, 1)
        self.assertEqual(t2[0].price, 4)
        self.assertEqual(t2[0].volume, 2)

    def test_partial_crossing_trades(self):
        """
        If the best bid is higher than the best ask, we
        expect a trade of the smaller volume at the price
        of the first order.
        """
        ob = Orderbook()
        t1 = ob.insert_bid(0, 5, 2)
        t2 = ob.insert_ask(1, 4, 1)

        self.assertListEqual(t1, [])
        self.assertEqual(len(t2), 1)
        self.assertEqual(t2[0].buyer, 0)
        self.assertEqual(t2[0].seller, 1)
        self.assertEqual(t2[0].price, 5)
        self.assertEqual(t2[0].volume, 1)
        self.assertEqual(ob.total_bid_volume, 1)
        self.assertEqual(ob.total_ask_volume, 0)

        ob = Orderbook()
        t1 = ob.insert_ask(1, 4, 2)
        t2 = ob.insert_bid(0, 5, 1)

        self.assertListEqual(t1, [])
        self.assertEqual(len(t2), 1)
        self.assertEqual(t2[0].buyer, 0)
        self.assertEqual(t2[0].seller, 1)
        self.assertEqual(t2[0].price, 4)
        self.assertEqual(t2[0].volume, 1)
        self.assertEqual(ob.total_bid_volume, 0)
        self.assertEqual(ob.total_ask_volume, 1)

    def test_full_multi_trade_orders(self):
        """
        If there is precisely as much volume that satisfies the price limit
        as ordered, then we expect all the orders to result in trades.
        """
        # Ask-initiated trades
        ob = Orderbook()
        t1 = ob.insert_bid(0, 5, 1)
        t2 = ob.insert_bid(1, 5, 1)
        t3 = ob.insert_bid(2, 6, 2)

        self.assertListEqual(t1, [])
        self.assertListEqual(t2, [])
        self.assertListEqual(t3, [])

        t4 = ob.insert_ask(3, 5, 4)

        self.assertEqual(len(t4), 3)
        self.assertEqual(t4[0].buyer, 2)
        self.assertEqual(t4[0].seller, 3)
        self.assertEqual(t4[0].price, 6)
        self.assertEqual(t4[0].volume, 2)
        self.assertEqual(t4[1].buyer, 0)
        self.assertEqual(t4[1].seller, 3)
        self.assertEqual(t4[1].price, 5)
        self.assertEqual(t4[1].volume, 1)
        self.assertEqual(t4[2].buyer, 1)
        self.assertEqual(t4[2].seller, 3)
        self.assertEqual(t4[2].price, 5)
        self.assertEqual(t4[2].volume, 1)
        self.assertEqual(ob.total_bid_volume, 0)
        self.assertEqual(ob.total_ask_volume, 0)

        # Bid-initiated trades
        ob = Orderbook()
        t1 = ob.insert_ask(0, 5, 1)
        t2 = ob.insert_ask(1, 5, 1)
        t3 = ob.insert_ask(2, 4, 2)

        self.assertListEqual(t1, [])
        self.assertListEqual(t2, [])
        self.assertListEqual(t3, [])

        t4 = ob.insert_bid(3, 5, 4)

        self.assertEqual(len(t4), 3)
        self.assertEqual(t4[0].buyer, 3)
        self.assertEqual(t4[0].seller, 2)
        self.assertEqual(t4[0].price, 4)
        self.assertEqual(t4[0].volume, 2)
        self.assertEqual(t4[1].buyer, 3)
        self.assertEqual(t4[1].seller, 0)
        self.assertEqual(t4[1].price, 5)
        self.assertEqual(t4[1].volume, 1)
        self.assertEqual(t4[2].buyer, 3)
        self.assertEqual(t4[2].seller, 1)
        self.assertEqual(t4[2].price, 5)
        self.assertEqual(t4[2].volume, 1)
        self.assertEqual(ob.total_bid_volume, 0)
        self.assertEqual(ob.total_ask_volume, 0)

    def test_partial_multi_trade_orders(self):
        """
        If there is some volume that satisfies an orders price limit,
        we expect trades to happen. In particular, if the best price volume
        is less than the order's, we expect multiple trades to occur.
        """
        # Ask-initiated trades
        ob = Orderbook()
        t1 = ob.insert_bid(0, 5, 1)
        t2 = ob.insert_bid(1, 5, 2)
        t3 = ob.insert_bid(2, 6, 1)

        self.assertListEqual(t1, [])
        self.assertListEqual(t2, [])
        self.assertListEqual(t3, [])

        t4 = ob.insert_ask(3, 5, 3)

        self.assertEqual(len(t4), 3)
        self.assertEqual(t4[0].buyer, 2)
        self.assertEqual(t4[0].seller, 3)
        self.assertEqual(t4[0].price, 6)
        self.assertEqual(t4[0].volume, 1)
        self.assertEqual(t4[1].buyer, 0)
        self.assertEqual(t4[1].seller, 3)
        self.assertEqual(t4[1].price, 5)
        self.assertEqual(t4[1].volume, 1)
        self.assertEqual(t4[2].buyer, 1)
        self.assertEqual(t4[2].seller, 3)
        self.assertEqual(t4[2].price, 5)
        self.assertEqual(t4[2].volume, 1)
        self.assertEqual(ob.total_bid_volume, 1)
        self.assertEqual(ob.total_ask_volume, 0)

        # Bid-initiated trades
        ob = Orderbook()
        t1 = ob.insert_ask(0, 5, 1)
        t2 = ob.insert_ask(1, 5, 2)
        t3 = ob.insert_ask(2, 4, 1)

        self.assertListEqual(t1, [])
        self.assertListEqual(t2, [])
        self.assertListEqual(t3, [])

        t4 = ob.insert_bid(3, 5, 3)

        self.assertEqual(len(t4), 3)
        self.assertEqual(t4[0].buyer, 3)
        self.assertEqual(t4[0].seller, 2)
        self.assertEqual(t4[0].price, 4)
        self.assertEqual(t4[0].volume, 1)
        self.assertEqual(t4[1].buyer, 3)
        self.assertEqual(t4[1].seller, 0)
        self.assertEqual(t4[1].price, 5)
        self.assertEqual(t4[1].volume, 1)
        self.assertEqual(t4[2].buyer, 3)
        self.assertEqual(t4[2].seller, 1)
        self.assertEqual(t4[2].price, 5)
        self.assertEqual(t4[2].volume, 1)
        self.assertEqual(ob.total_bid_volume, 0)
        self.assertEqual(ob.total_ask_volume, 1)

    def test_basic_volume_limit(self):
        """
        Trades should affect the positions and volume limits of
        both parties.
        """
        ob = Orderbook(position_limit=10)
        u1 = ob.get_user(0)
        u2 = ob.get_user(1)
        self.assertEqual(u1.bid_limit(), 10)
        self.assertEqual(u1.ask_limit(), 10)
        self.assertEqual(u2.bid_limit(), 10)
        self.assertEqual(u2.ask_limit(), 10)

        ob.insert_bid(0, 5, 2)
        self.assertEqual(u1.bid_limit(), 10)
        self.assertEqual(u1.bid_limit(), 10)
        self.assertEqual(u2.bid_limit(), 10)
        self.assertEqual(u2.ask_limit(), 10)

        ob.insert_ask(1, 5, 2)
        self.assertEqual(u1.bid_limit(), 8)
        self.assertEqual(u1.ask_limit(), 12)
        self.assertEqual(u2.bid_limit(), 12)
        self.assertEqual(u2.ask_limit(), 8)

    def test_exceeding_bid_limit(self):
        ob = Orderbook(position_limit=10)
        u = ob.get_user(0)
        ob.insert_bid(u.identifier, 5, 2)
        ob.insert_bid(u.identifier, 6, 7)
        ob.insert_bid(u.identifier, 5, 5)

        self.assertEqual(ob.total_bid_volume, 10)
        self.assertEqual(u.bid_volume, 10)
        self.assertEqual(len(ob.get_bids_at_price(5)), 2)
        self.assertEqual(len(ob.get_bids_at_price(6)), 1)
