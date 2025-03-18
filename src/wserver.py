import time
from constants import logging


class Wserver:
    # flag to tell us if the websocket is open
    socket_opened = False
    ltp = {}

    def __init__(self, api, tokens):
        self.api = api.broker
        self.tokens = tokens
        ret = self.api.start_websocket(
            order_update_callback=self.event_handler_order_update,
            subscribe_callback=self.event_handler_quote_update,
            socket_open_callback=self.open_callback,
        )
        if ret:
            logging.info(f"{ret} ws started")

    def open_callback(self):
        self.socket_opened = True
        self.api.subscribe(self.tokens, feed_type="d")
        logging.info("wsocket opened")
        # api.subscribe(['NSE|22', 'BSE|522032'])

    # application callbacks
    def event_handler_order_update(self, message):
        logging.debug("ws order update")

    def event_handler_quote_update(self, message):
        val = message.get("lp", False)
        if val:
            self.ltp[message["e"] + "|" + message["tk"]] = val


if __name__ == "__main__":
    from api import Helper

    token = ["NSE|22", "NSE|34"]
    wserver = Wserver(Helper.api, token)
    while True:
        print(wserver.ltp)
        time.sleep(1)
        # wserver.tokens = ["NSE:25"]
