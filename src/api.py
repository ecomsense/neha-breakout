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
        exchange,
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
                exchange=exchange,
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
    import pendulum as plum

    Helper.api()
    resp = Helper.orders()
    if resp and any(resp):
        print(resp)
        pd.DataFrame(resp).to_csv(S_DATA + "orders.csv")

    resp = Helper.positions()
    if resp and any(resp):
        print(resp)
        pd.DataFrame(resp).to_csv(S_DATA + "positions.csv")

    def unixtime(timee):
        return plum.from_format(timee, "DDMMYYYY HH:mm:ss").timestamp()

    st = unixtime("01091983 09:15:00")
    et = unixtime("23032025 15:30:00")

    re = Helper._api.broker.get_daily_price_series(
        exchange="NSE",
        tradingsymbol="PARADEEP-EQ",
        startdate=st,
        enddate=et,
    )

    print(len(re))
