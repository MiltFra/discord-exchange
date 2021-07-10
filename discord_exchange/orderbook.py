from queue import PriorityQueue
from collections import deque
from typing import Deque
from discord_exchange import trade
from discord_exchange.trade import Trade
from discord_exchange.order import Order


class Orderbook:
    def __init__(self) -> None:
        self.bid_prices = PriorityQueue()
        self.ask_prices = PriorityQueue()
        self.bids = dict()
        self.asks = dict()
        self.total_bid_volume = 0
        self.total_ask_volume = 0

    def insert_bid(self, buyer: int, price: float, volume: int) -> list[Trade]:
        assert price >= 0
        assert volume > 0
        bid = Order(Order.TYPE_BID, buyer, price, volume)
        if self.bids.get(bid.price, None):
            self._insert_bid_no_trade(bid)
            return []
        trades = []
        while bid.volume and self.total_ask_volume:
            ask = self.best_ask()
            assert ask is not None
            if ask.price > bid.price:
                break
            trade_volume = min(ask.volume, bid.volume)
            trades.append(
                Trade(bid.issued_by, ask.issued_by, ask.price, trade_volume))
            self.total_ask_volume -= trade_volume
            bid.reduce_volume(trade_volume)
            ask.reduce_volume(trade_volume)
            asks_at_price = self.asks.get(ask.price, deque())
            if ask.volume == 0:
                asks_at_price.popleft()
        if bid.volume:
            self._insert_bid_no_trade(bid)
        return trades

    def _insert_bid_no_trade(self, bid: Order) -> None:
        bids_at_price = self.bids.get(bid.price, deque())
        bids_at_price.append(bid)
        self.total_bid_volume += bid.volume
        self.bids[bid.price] = bids_at_price
        # We want to sort bid prices in descending order so we need
        # to store their additive inverses
        self.bid_prices.put(-bid.price)

    def insert_ask(self, seller: int, price: float,
                   volume: int) -> list[Trade]:
        assert price >= 0
        assert volume > 0
        ask = Order(Order.TYPE_ASK, seller, price, volume)
        if self.asks.get(ask.price, None):
            self._insert_ask_no_trade(ask)
            return []
        trades = []
        while ask.volume and self.total_bid_volume:
            bid = self.best_bid()
            assert bid is not None
            if ask.price > bid.price:
                break
            trade_volume = min(ask.volume, bid.volume)
            trades.append(
                Trade(bid.issued_by, ask.issued_by, bid.price, trade_volume))
            self.total_bid_volume -= trade_volume
            bid.reduce_volume(trade_volume)
            ask.reduce_volume(trade_volume)
            bids_at_price = self.bids.get(bid.price, deque())
            if bid.volume == 0:
                bids_at_price.popleft()
        if ask.volume:
            self._insert_ask_no_trade(ask)
        return trades

    def _insert_ask_no_trade(self, ask: Order) -> None:
        asks_at_price = self.asks.get(ask.price, deque())
        asks_at_price.append(ask)
        self.total_ask_volume += ask.volume
        self.asks[ask.price] = asks_at_price
        self.ask_prices.put(ask.price)

    def best_ask(self) -> Order:
        while (price := self._peek_ask_prices()) is not None:
            asks_at_price = self.asks.get(price, deque())
            while asks_at_price and not asks_at_price[0].volume:
                self.ask_prices.popleft()
            if asks_at_price:
                return asks_at_price[0]
            else:
                self.ask_prices.get()
        return None

    def _peek_ask_prices(self) -> float:
        try:
            with self.ask_prices.mutex:
                return self.ask_prices.queue[0]
        except IndexError:
            return None

    def best_bid(self) -> Order:
        while (price := self._peek_bid_prices()) is not None:
            bids_at_price = self.bids.get(price, deque())
            while bids_at_price and not bids_at_price[0].volume:
                bids_at_price.popleft()
            if bids_at_price:
                return bids_at_price[0]
            else:
                self.bid_prices.get()
        return None

    def _peek_bid_prices(self) -> float:
        try:
            with self.bid_prices.mutex:
                return -self.bid_prices.queue[0]
        except IndexError:
            return None

    def find_orders_per_price(self, orders: dict) -> list[tuple]:
        prices = orders.keys()
        raw_orders = map(lambda x: orders.get(x, deque()), prices)
        raw_volumes = []
        for order_list in raw_orders:
            raw_volumes.append(sum(map(lambda x: x[2], order_list)))
        return list(filter(lambda x: x[1], zip(prices, raw_volumes)))

    def __str__(self) -> str:
        bids_per_price = sorted(self.find_orders_per_price(self.bids),
                                reverse=True)
        asks_per_price = sorted(self.find_orders_per_price(self.asks))
        price_volume_to_string = lambda x: f"{x[1]}@{x[0]}"
        return f"ASK: {', '.join(map(price_volume_to_string, asks_per_price))}\nBID: {', '.join(map(price_volume_to_string, bids_per_price))}"