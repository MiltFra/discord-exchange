from queue import PriorityQueue
from collections import deque
from typing import Deque
from discord_exchange.trade import Trade


class Orderbook:
    def __init__(self) -> None:
        self.bid_prices = PriorityQueue()
        self.ask_prices = PriorityQueue()
        self.bids = dict()
        self.asks = dict()
        self.total_bid_volume = 0
        self.total_ask_volume = 0

    def insert_bid(self, buyer, bid_price, bid_volume) -> list[Trade]:
        if self.bids.get(bid_price, None):
            self._insert_bid_no_trade(buyer, bid_price, bid_volume)
            return []
        trades = []
        while bid_volume and self.total_ask_volume:
            seller, ask_price, ask_volume = self.best_ask()
            if ask_price > bid_price:
                break
            trade_volume = min(ask_volume, bid_volume)
            trades.append(Trade(buyer, seller, ask_price, trade_volume))
            self.total_ask_volume -= trade_volume
            bid_volume -= trade_volume
            ask_volume -= trade_volume
            asks = self.asks.get(ask_price, deque())
            asks.popleft()
            if ask_volume:
                asks.appendleft((seller, ask_price, ask_volume))
        if bid_volume:
            self._insert_bid_no_trade(buyer, bid_price, bid_volume)
        return trades

    def _insert_bid_no_trade(self, buyer, bid_price, bid_volume) -> None:
        bids_at_price = self.bids.get(bid_price, deque())
        bids_at_price.append((buyer, bid_price, bid_volume))
        self.total_bid_volume += bid_volume
        self.bids[bid_price] = bids_at_price
        self.bid_prices.put(-bid_price)

    def insert_ask(self, seller, ask_price, ask_volume) -> list[Trade]:
        if self.asks.get(ask_price, None):
            self._insert_ask_no_trade(seller, ask_price, ask_volume)
            return []
        trades = []
        while ask_volume and self.total_bid_volume:
            buyer, bid_price, bid_volume = self.best_bid()
            if ask_price > bid_price:
                break
            trade_volume = min(ask_volume, bid_volume)
            trades.append(Trade(buyer, seller, bid_price, trade_volume))
            self.total_bid_volume -= trade_volume
            bid_volume -= trade_volume
            ask_volume -= trade_volume
            bids = self.bids.get(bid_price, deque())
            bids.popleft()
            if bid_volume:
                bids.appendleft((buyer, bid_price, bid_volume))
        if ask_volume:
            self._insert_ask_no_trade(seller, ask_price, ask_volume)
        return trades

    def _insert_ask_no_trade(self, seller, ask_price, ask_volume) -> None:
        asks_at_price = self.asks.get(ask_price, deque())
        asks_at_price.append((seller, ask_price, ask_volume))
        self.total_ask_volume += ask_volume
        self.asks[ask_price] = asks_at_price
        self.ask_prices.put(ask_price)

    def best_ask(self) -> tuple:
        while (price := self.best_ask_price()) is not None:
            asks_at_price = self.asks.get(price, deque())
            if asks_at_price:
                return asks_at_price[0]
            else:
                self.ask_prices.get()
        return None

    def best_ask_price(self) -> float:
        try:
            with self.ask_prices.mutex:
                return self.ask_prices.queue[0]
        except IndexError:
            return None

    def best_bid(self) -> tuple:
        while (price := self.best_bid_price()) is not None:
            bids_at_price = self.bids.get(price, deque())
            if bids_at_price:
                return bids_at_price[0]
            else:
                self.bid_prices.get()
        return None

    def best_bid_price(self) -> float:
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