from queue import PriorityQueue
from collections import deque
from typing import Deque
from discord_exchange import trade
from discord_exchange.trade import Trade
from discord_exchange.order import Order


class Orderbook:
    def __init__(self, volume_limit=10) -> None:
        self.bid_prices = PriorityQueue()
        self.ask_prices = PriorityQueue()
        self.bids = dict()
        self.asks = dict()
        self.total_bid_volume = 0
        self.total_ask_volume = 0
        self.bids_per_issuer = dict()
        self.asks_per_issuer = dict()
        self.bid_volume_per_issuer = dict()
        self.ask_volume_per_issuer = dict()
        self.volume_limit = volume_limit

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
                Trade(bid.issuer, ask.issuer, ask.price, trade_volume))
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
        bids_by_issuer = self.bids_per_issuer.get(bid.issuer, deque())
        bids_by_issuer.append(bid)
        self.bids_per_issuer[bid.issuer] = bids_by_issuer
        self.total_bid_volume += bid.volume
        self.bids[bid.price] = bids_at_price
        # We want to sort bid prices in descending order so we need
        # to store their additive inverses
        self.bid_prices.put(-bid.price)

        self.bid_volume_per_issuer[
            bid.issuer] = bid.volume + self.bid_volume_per_issuer.get(
                bid.issuer, 0)
        if self.bid_volume_per_issuer[bid.issuer] > self.volume_limit:
            self._remove_excess_bids(bid.issuer)

    def _remove_excess_bids(self, issuer: int) -> None:
        while (bid_volume_by_issuer :=
               self.bid_volume_per_issuer[issuer]) > self.volume_limit:
            bids_by_issuer = self.bids_per_issuer.get(issuer, deque())
            assert bids_by_issuer
            volume_delta = min(bids_by_issuer[0].volume,
                               bid_volume_by_issuer - self.volume_limit)
            self.bid_volume_per_issuer[issuer] -= volume_delta
            bids_by_issuer[0].reduce_volume(volume_delta)
            if bids_by_issuer[0].volume == 0:
                bids_by_issuer.popleft()

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
                Trade(bid.issuer, ask.issuer, bid.price, trade_volume))
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
        asks_by_issuer = self.asks_per_issuer.get(ask.issuer, deque())
        asks_by_issuer.append(ask)
        self.asks_per_issuer[ask.issuer] = asks_by_issuer
        self.total_ask_volume += ask.volume
        self.asks[ask.price] = asks_at_price
        self.ask_prices.put(ask.price)

        self.ask_volume_per_issuer[
            ask.issuer] = ask.volume + self.ask_volume_per_issuer.get(
                ask.issuer, 0)
        if self.ask_volume_per_issuer[ask.issuer] > self.volume_limit:
            self._remove_excess_asks(ask.issuer)

    def _remove_excess_asks(self, issuer: int):
        while (ask_volume_by_issuer :=
               self.ask_volume_per_issuer[issuer]) > self.volume_limit:
            asks_by_issuer = self.asks_per_issuer.get(issuer, deque())
            assert asks_by_issuer
            volume_delta = min(asks_by_issuer[0].volume,
                               ask_volume_by_issuer - self.volume_limit)
            self.ask_volume_per_issuer[issuer] -= volume_delta
            asks_by_issuer[0].reduce_volume(volume_delta)
            if asks_by_issuer[0].volume == 0:
                asks_by_issuer.popleft()

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
            raw_volumes.append(sum(map(lambda ord: ord.volume, order_list)))
        return list(filter(lambda x: x[1], zip(prices, raw_volumes)))

    def __str__(self) -> str:
        bids_per_price = sorted(self.find_orders_per_price(self.bids),
                                reverse=True)
        asks_per_price = sorted(self.find_orders_per_price(self.asks))
        price_volume_to_string = lambda x: f"{x[1]}@{x[0]}"
        return f"ASK: {', '.join(map(price_volume_to_string, asks_per_price))}\n" \
            f"BID: {', '.join(map(price_volume_to_string, bids_per_price))}"