from . import Orderbook

if __name__ == "__main__":
    ob = Orderbook()
    trades = []
    trades.extend(ob.insert_bid(0, 100, 2))
    trades.extend(ob.insert_bid(1, 100, 98))
    trades.extend(ob.insert_bid(2, 101, 3))
    trades.extend(ob.insert_ask(0, 103, 3))
    trades.extend(ob.insert_ask(1, 103, 4))
    trades.extend(ob.insert_ask(2, 102, 100))
    trades.extend(ob.insert_ask(3, 101, 5))
    print(ob)
    for trade in trades:
        print("TRADE:", trade)
