from discord_exchange.orderbook import Orderbook


class BinaryExchange:
    def __init__(self, limit=5) -> None:
        self.orderbook = Orderbook()
        self.trades = []
        self.positions = dict()
        self.position_limit = limit

    def insert_ask(self, buyer, bid_price, bid_volume):
        pass