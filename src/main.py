from constants import logging, O_SETG
from api import Helper
from strategies.strategy import Strategy
from toolkit.kokoo import is_time_past, kill_tmux, timer
from traceback import print_exc
from symbols import Symbols
from typing import Any, Dict, List
from wserver import Wserver
import pandas as pd


def wait_until_start(start):
    is_start = is_time_past(start)
    while not is_start:
        print(f"waiting for {start}")
    else:
        logging.info("program started")


def get_tokens_from_symbols(obj: Strategy) -> List[Dict[Any, Any]]:
    """
    returns tradingsymbols alongwith the tokens
    """
    tokens_and_tradingsymbols = [{}]
    df1 = obj.df_stocks_in_play
    df2 = obj.df_delivered
    df = pd.concat([df1, df2])
    if len(df.index) > 0:
        df = df.reset_index(names="Symbol")
        exch_sym = df.groupby("Exch")["Symbol"].apply(list).to_dict()
        for exchange, tsym in exch_sym.items():
            sym_obj = Symbols(exchange)
            sym_obj.download_master()
            lst = sym_obj.get_equity_tokens(tsym)
            if any(tokens_and_tradingsymbols):
                tokens_and_tradingsymbols += lst
            else:
                tokens_and_tradingsymbols = lst
        return tokens_and_tradingsymbols


def change_key(ltps):
    info = Helper.symbol_info
    changed = {info[k]: float(v) for k, v in ltps.items()}
    return changed


def subscribe(lst_of_symbols):
    Helper.symbol_info = {
        dct["Exchange"] + "|" + str(dct["Token"]): dct["TradingSymbol"]
        for dct in lst_of_symbols
    }
    tokens = list(Helper.symbol_info.keys())
    ws = Wserver(Helper.api(), tokens)
    prices = {}
    while not any(prices):
        prices = ws.ltp
        timer(1)
        print("waiting for websocket")
    return ws


def test():
    Helper.api()
    obj = Strategy()
    lst_of_symbols = get_tokens_from_symbols(obj)
    print(lst_of_symbols)


def main():
    try:
        start = O_SETG["program"].pop("start")
        wait_until_start(start)
        Helper.api()
        obj = Strategy()
        if obj is None:
            print("object is none")
            timer(2)
        lst_of_symbols = get_tokens_from_symbols(obj)
        ws = subscribe(lst_of_symbols)
        stop = O_SETG["program"].pop("stop")
        while not is_time_past(stop):
            new_ltps = change_key(ws.ltp)
            obj.run(new_ltps)
        else:
            obj.save_dfs()
            kill_tmux()
    except KeyboardInterrupt:
        print("saving")
        obj.save_dfs()
        timer(5)
    except Exception as e:
        print_exc()
        logging.error(f"{e} while running strategy")


if __name__ == "__main__":
    main()
