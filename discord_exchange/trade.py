class Trade:
    num_trades = 0

    def __init__(self, buyer, seller, price, volume) -> None:
        assert volume > 0
        self.buyer = buyer
        self.seller = seller
        self.price = price
        self.volume = volume
        self.id = Trade.num_trades
        Trade.num_trades += 1

    def binary_value(self, theo):
        if self.price > theo:
            return -self.volume
        elif self.price < theo:
            return self.volume
        return 0

    def true_value(self, theo):
        return self.volume * (theo - self.price)

    def __str__(self) -> str:
        return f"#{self.id} {self.seller}->{self.buyer},{self.volume}@{self.price}"