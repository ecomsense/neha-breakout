from traceback import print_exc
from importlib import import_module
from constants import O_CNFG, S_DATA, logging


def login():
    broker_name = O_CNFG.pop("broker", None)
    if not broker_name:
        raise ValueError("broker not specified in credential file")

    # Dynamically import the broker module
    module_path = f"stock_brokers.{broker_name}.{broker_name}"
    broker_module = import_module(module_path)

    logging.info(f"BrokerClass: {broker_module}")
    # Get the broker class (assuming class name matches the broker name)
    BrokerClass = getattr(broker_module, broker_name.capitalize())

    # Initialize API with config
    broker_object = BrokerClass(**O_CNFG)
    if broker_object.authenticate():
        logging.info("api connected")
        return broker_object
    else:
        __import__("sys").exit(1)


def make_default_order():
    args = dict(
        product="C",
        exchange="NSE",
    )
    return args


class Helper:
    _api = None

    @classmethod
    def api(cls):
        if cls._api is None:
            cls._api = login()
        return cls._api

    @classmethod
    def orders(cls):
        return cls._api.orders

    @classmethod
    def positions(cls):
        return cls._api.positions

    @classmethod
    def holdings(cls):
        return cls._api.broker.get_holdings()

    @classmethod
    def ltp(cls, exchange, token):
        try:
            resp = cls._api.scriptinfo(exchange, token)
            if resp is not None:
                return float(resp["lp"])
            else:
                raise ValueError("ltp is none")
        except Exception as e:
            message = f"{e} while ltp"
            logging.error(message)
            print_exc()

    @classmethod
    def place_order(
        cls,
        symbol,
        quantity,
        side,
        price=0,
        trigger_price=0,
        order_type="MKT",
        tag="neha-breakout",
    ):

        try:
            kwargs = make_default_order()
            args = dict(
                symbol=symbol,
                quantity=quantity,
                disclosed_quantity=quantity,
                side=side,
                price=price,
                trigger_price=trigger_price,
                order_type=order_type,
                tag=tag,
            )
            kwargs.update(args)
            logging.debug(str(kwargs))
            resp = cls._api.order_place(**kwargs)
            return resp
        except Exception as e:
            message = f"helper error {e} while placing order"
            logging.error(message)
            print_exc()

    @classmethod
    def close_positions(cls, half=False):
        for pos in cls._api.positions:
            if pos["quantity"] == 0:
                continue
            else:
                quantity = abs(pos["quantity"])
                quantity = int(quantity / 2) if half else quantity

            logging.debug(f"trying to close {pos['symbol']}")
            if pos["quantity"] < 0:
                args = dict(
                    symbol=pos["symbol"],
                    quantity=quantity,
                    disclosed_quantity=quantity,
                    product="M",
                    side="B",
                    order_type="MKT",
                    exchange="NFO",
                    tag="close",
                )
                resp = cls._api.order_place(**args)
                logging.debug(f"api responded with {resp}")
            elif quantity > 0:
                args = dict(
                    symbol=pos["symbol"],
                    quantity=quantity,
                    disclosed_quantity=quantity,
                    product="M",
                    side="S",
                    order_type="MKT",
                    exchange="NFO",
                    tag="close",
                )
                resp = cls._api.order_place(**args)
                logging.debug(f"api responded with {resp}")

    @classmethod
    def mtm(cls):
        try:
            pnl = 0
            positions = [{}]
            positions = cls._api.positions
            """
            keys = [
                "symbol",
                "quantity",
                "last_price",
                "urmtom",
                "rpnl",
            ]
            """
            if any(positions):
                # calc value
                for pos in positions:
                    pnl += pos["urmtom"]
        except Exception as e:
            message = f"while calculating {e}"
            logging.error(f"api responded with {message}")
        finally:
            return pnl


if __name__ == "__main__":
    import pandas as pd

    Helper.api()
    resp = Helper.orders()
    if resp and any(resp):
        print(resp)
        pd.DataFrame(resp).to_csv(S_DATA + "orders.csv")

    resp = Helper.positions()
    if resp and any(resp):
        print(resp)
        pd.DataFrame(resp).to_csv(S_DATA + "positions.csv")

    resp = Helper.holdings()
    if resp and any(resp):
        print(resp)
        pd.DataFrame(resp).to_csv(S_DATA + "holdings.csv")
