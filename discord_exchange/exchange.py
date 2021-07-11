from discord_exchange.orderbook import Orderbook
from multiprocessing import Lock


class Exchange:
    def __init__(self) -> None:
        self.orderbook = Orderbook()
        self.trades = []
        self.user_to_id = dict()
        self.user_from_id = dict()
        self.num_users = 0
        self.open = False
        self.mutex = Lock()
        self.score = dict()

    def register_user(self, name: str) -> None:
        with self.mutex:
            self.user_to_id[name] = self.num_users
            self.user_from_id[self.num_users] = name
            self.num_users += 1

    def open(self, position_limit=5):
        with self.mutex:
            self.open = True
            self.orderbook = Orderbook(position_limit)
            self.trades = []

    def _update_score(self, user_id, delta):
        if user_id not in self.score.keys():
            self.score[user_id] = 0
        self.score[user_id] += delta

    def _calculate_binary_score(self, price):
        for trade in self.trades:
            value = trade.binary_value(price)
            self._update_score(trade.buyer, value)
            self._update_score(trade.seller, -value)

    def _calculate_proportional_score(self, price):
        for trade in self.trades:
            value = trade.binary_value(price)
            self._update_score(trade.buyer, value)
            self._update_score(trade.seller, -value)

    def close_at(self, price, binary=True):
        with self.mutex:
            self.close = True
        if binary:
            self._calculate_binary_score(price)
        else:
            self._calculate_proportional_score(price)

    def bid(self, name, price, volume):
        if not self.open:
            raise MarketClosedError(name)
        with self.mutex:
            if name not in self.user_to_id.keys():
                self.register_user(name)
            user_id = self.user_to_id(name)
            self.trades.append(
                self.orderbook.insert_bid(user_id, price, volume))

    def ask(self, name, price, volume):
        if not self.open:
            raise MarketClosedError(name)
        with self.mutex:
            if name not in self.user_to_id.keys():
                self.register_user(name)
            user_id = self.user_to_id(name)
            self.trades.append(
                self.orderbook.insert_ask(user_id, price, volume))


class MarketClosedError(Exception):
    def __init__(self, name, *args: object) -> None:
        super().__init__(*args)
        self.name = name

    def __str__(self) -> str:
        return f"{self.name} tried to insert order while market was closed"