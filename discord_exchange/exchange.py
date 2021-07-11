from discord_exchange.orderbook import Orderbook
from multiprocessing import Lock


class Exchange:
    """
    An exchange allows users to register and trade while 
    it's open. Each time the exchange closes, all orders 
    are deleted and the profits and losses caused by all 
    the trades are summed up.
    """
    def __init__(self) -> None:
        self.orderbook = Orderbook()
        self.trades = []
        self.user_to_id = dict()
        self.user_from_id = dict()
        self.num_users = 0
        self.open = False
        self.mutex = Lock()
        self.score = dict()

    def _get_user_id(self, name: str) -> int:
        """
        Returns a unique and permanent ID for a given user name.
        """
        if name not in self.user_to_id.keys():
            self._register_user()
        return self.user_from_id[name]

    def _register_user(self, name: str) -> None:
        """
        Assigns a new, unique ID to a given user name.
        """
        self.user_to_id[name] = self.num_users
        self.user_from_id[self.num_users] = name
        self.num_users += 1

    def open(self, position_limit=5):
        """
        Opens the exchange with a new orderbook and a given position limit.
        """
        with self.mutex:
            self.open = True
            self.orderbook = Orderbook(position_limit)
            self.trades = []

    def _update_score(self, user_id, delta):
        """
        Safely updates a user's score with a given delta.

        If the user does not yet have a score, 0 is implied.
        """
        if user_id not in self.score.keys():
            self.score[user_id] = 0
        self.score[user_id] += delta

    def _calculate_binary_score(self, price):
        """
        Updates all users' scores by using the binary scoring system.
        """
        for trade in self.trades:
            value = trade.binary_value(price)
            self._update_score(trade.buyer, value)
            self._update_score(trade.seller, -value)

    def _calculate_proportional_score(self, price):
        """
        Updates all users' scores by using the proportional scoring system.
        """
        for trade in self.trades:
            value = trade.binary_value(price)
            self._update_score(trade.buyer, value)
            self._update_score(trade.seller, -value)

    def close_at(self, price, binary=True):
        """
        Closes the market and updates the scores accordingly.
        """
        with self.mutex:
            self.close = True
        if binary:
            self._calculate_binary_score(price)
        else:
            self._calculate_proportional_score(price)

    def bid(self, name, price, volume):
        """
        If the exchange is open, inserts the given order and 
        updates the list of trades.
        """
        if not self.open:
            raise MarketClosedError(name)
        with self.mutex:
            user_id = self._get_user_id(name)
            self.trades.append(
                self.orderbook.insert_bid(user_id, price, volume))

    def ask(self, name, price, volume):
        """
        If the exchange is open, inserts the given order and 
        updates the list of trades.
        """
        if not self.open:
            raise MarketClosedError(name)
        with self.mutex:
            user_id = self._get_user_id(name)
            self.trades.append(
                self.orderbook.insert_ask(user_id, price, volume))


class MarketClosedError(Exception):
    def __init__(self, name, *args: object) -> None:
        super().__init__(*args)
        self.name = name

    def __str__(self) -> str:
        return f"{self.name} tried to insert order while market was closed"