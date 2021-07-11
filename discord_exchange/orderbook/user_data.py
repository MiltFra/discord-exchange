from collections import deque
from discord_exchange.orderbook.trade import Trade


class UserData:
    def __init__(self, identifier, position_limit=10) -> None:
        self.identifier = identifier
        self.bids = deque()
        self.asks = deque()
        self.bid_volume = 0
        self.ask_volume = 0
        self.position = 0
        self.position_limit = position_limit

    def bid_limit(self) -> int:
        return self.position_limit - self.position

    def ask_limit(self) -> int:
        return self.position_limit + self.position

    def bid_volume_delta(self):
        return self.bid_volume - self.bid_limit()

    def ask_volume_delta(self):
        return self.ask_volume - self.ask_limit()

    def remove_excess_bids(self):
        assert self.bids
        while self.bid_volume > self.bid_limit():
            volume_delta = min(self.bids[0].volume, self.bid_volume_delta())
            self.bid_volume -= volume_delta
            self.bids[0].reduce_volume(volume_delta)
            if self.bids[0].volume == 0:
                self.bids.popleft()

    def remove_excess_asks(self):
        assert self.asks
        while self.ask_volume > self.ask_limit():
            volume_delta = min(self.asks[0].volume, self.ask_volume_delta())
            self.ask_volume -= volume_delta
            self.asks[0].reduce_volume(volume_delta)
            if self.asks[0].volume == 0:
                self.asks.popleft()

    def register_trade(self, trade: Trade):
        if trade.seller == self.identifier:
            self.position -= trade.volume
            self.ask_volume -= trade.volume
        if trade.buyer == self.identifier:
            self.position += trade.volume
            self.bid_volume -= trade.volume