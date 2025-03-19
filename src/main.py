from constants import logging, O_SETG
from api import Helper
from strategies.strategy import Strategy
from toolkit.kokoo import is_time_past, kill_tmux, timer
from traceback import print_exc
from symbols import Symbols
from typing import Any, Dict, List
from wserver import Wserver


def wait_until_start(start):
    is_start = is_time_past(start)
    while not is_start:
        print(f"waiting for {start}")
    else:
        logging.info("program started")


def get_tokens_from_symbols(tsym: List) -> List[Dict[Any, Any]]:
    """
    returns tradingsymbols alongwith the tokens
    """
    exchanges = O_SETG["exchanges"]
    tokens_and_tradingsymbols = [{}]
    for exchange in exchanges:
        sym_obj = Symbols(exchange)
        sym_obj.download_master()
        lst = sym_obj.get_equity_tokens(tsym)
        if any(tokens_and_tradingsymbols) and any(lst):
            tokens_and_tradingsymbols + lst
        else:
            tokens_and_tradingsymbols = lst
    return tokens_and_tradingsymbols


def change_key(ltps):
    info = Helper.symbol_info
    changed = {info[k]: float(v) for k, v in ltps.items()}
    return changed


def initialize():
    Helper.api()
    obj = Strategy()
    if obj is None:
        print("object is none")
        timer(2)
    df = obj.df_stocks_in_play + obj.df_delivered
    tsym: List = df.index.to_list()
    logging.debug(f"tradingsymbols to enter and exit:{tsym=}")
    lst_of_symbols = get_tokens_from_symbols(tsym)

    Helper.symbol_info = {
        O_SETG["exchanges"][0] + "|" + str(dct["Token"]): dct["TradingSymbol"]
        for dct in lst_of_symbols
    }
    tokens = list(Helper.symbol_info.keys())
    ws = Wserver(Helper.api(), tokens)
    prices = {}
    while not any(prices):
        prices = ws.ltp
        timer(1)
        print("waiting for websocket")
    return obj, ws


def save_changes(strgy):
    strgy.save_dfs()


def main():
    try:
        start = O_SETG["program"].pop("start")
        wait_until_start(start)
        obj, ws = initialize()
        stop = O_SETG["trade"].pop("stop")
        while not is_time_past(stop):
            new_ltps = change_key(ws.ltp)
            obj.run(new_ltps)
        else:
            save_changes(obj)
            kill_tmux()
    except KeyboardInterrupt:
        print("saving")
        save_changes(obj)
        timer(5)
    except Exception as e:
        print_exc()
        logging.error(f"{e} while running strategy")


if __name__ == "__main__":
    main()
