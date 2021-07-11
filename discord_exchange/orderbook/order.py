class Order:

    # Each order has a sequence number
    num_order_updates = 0

    # We may add more order types in the future
    TYPE_BID = 0
    TYPE_ASK = 1

    def __init__(self, order_type, user, price, volume) -> None:
        self.type = order_type
        self.user_id = user
        self.price = price
        self.volume = volume
        self._register_update()

    def update_volume(self, new_volume) -> None:
        assert 0 <= new_volume < self.volume
        self.volume = new_volume
        self._register_update()

    def reduce_volume(self, volume_delta) -> None:
        assert 0 < volume_delta <= self.volume
        self.volume -= volume_delta
        self._register_update()

    def _register_update(self) -> None:
        self.updated_at = Order.num_order_updates
        Order.num_order_updates += 1
