from collections import deque


class UserData:
    def __init__(self, identifier) -> None:
        self.identifier = identifier
        self.bids = deque()
        self.asks = deque()
        self.bid_volume = 0
        self.ask_volume = 0
        self.bid_volume_limit = 10
        self.ask_volume_limit = 10

    def bid_volume_delta(self):
        return self.bid_volume - self.bid_volume_limit

    def ask_volume_delta(self):
        return self.ask_volume - self.ask_volume_limit

    def remove_excess_bids(self):
        assert self.bids
        while self.bid_volume > self.bid_volume_limit:
            volume_delta = min(self.bids[0].volume, self.bid_volume_delta())
            self.bid_volume -= volume_delta
            self.bids[0].reduce_volume(volume_delta)
            if self.bids[0].volume == 0:
                self.bids.popleft()

    def remove_excess_asks(self):
        assert self.asks
        while self.ask_volume > self.ask_volume_limit:
            volume_delta = min(self.asks[0].volume, self.ask_volume_delta())
            self.ask_volume -= volume_delta
            self.asks[0].reduce_volume(volume_delta)
            if self.asks[0].volume == 0:
                self.asks.popleft()
