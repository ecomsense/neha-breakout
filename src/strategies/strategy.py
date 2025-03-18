from constants import STOCKS_IN_PLAY, DELIVERED, HISTORY, logging
import pandas as pd
from api import Helper
from toolkit.kokoo import timer
import pendulum as pdlm


def df_fm_file(file, columns=[], index_col="Symbol"):
    df = (
        pd.read_csv(file, index_col=index_col)
        if file.endswith("csv")
        else pd.read_excel(file, index_col=index_col)
    )
    df = df[columns] if any(columns) else df
    return df


class Strategy:

    def __init__(self):
        stocks_columns = ["Bandh", "Capital", "Abv", "Risk", "Reward", "Qty"]
        df = df_fm_file(STOCKS_IN_PLAY, stocks_columns)
        df = df[df["Bandh"].isna()]
        df.index = df.index.astype(str)
        self.df_stocks_in_play = df.drop(columns=["Bandh"], axis=1)
        self.df_stocks_in_play["Ltp"] = 0
        print("\n" + "FROM EXCEL")
        print(self.df_stocks_in_play)

        self.df_delivered = df_fm_file(DELIVERED)
        print("\n HOLDINGS")
        print(self.df_delivered)

        lst_pos = self.df_delivered.index.to_list()
        # drop self.df_stocks_in_play index  if it is in lst_pos
        self.df_stocks_in_play = self.df_stocks_in_play[
            ~self.df_stocks_in_play.index.isin(lst_pos)
        ]
        print("\n FINAL LIST")
        print(self.df_stocks_in_play)
        timer(2)

        self.fn = self.exit_beyond_band

    def enter_on_breakout(self):
        self.fn = self.exit_beyond_band
        try:
            symbols_to_remove = []
            for idx, row in self.df_stocks_in_play.iterrows():
                if row["Ltp"] > row["Abv"]:
                    resp = Helper.place_order(
                        symbol=idx,
                        quantity=row["Qty"],
                        side="B",
                        price=0,
                        order_type="MKT",
                    )
                    if resp:
                        print("enter")
                        amount_in_risk = (
                            round((row["Risk"] * row["Abv"] / 100) / 0.05) * 0.05
                        )
                        expected_reward = (
                            round((row["Reward"] * row["Abv"] / 100) / 0.05) * 0.05
                        )
                        self.df_delivered.loc[idx] = [
                            row["Abv"],
                            row["Abv"] - amount_in_risk,
                            row["Abv"] + expected_reward,
                            int(row["Qty"]),
                            pdlm.now("Asia/Kolkata"),
                            row["Ltp"],
                        ]
                        symbols_to_remove.append(idx)
            self.df_stocks_in_play.drop(index=symbols_to_remove, inplace=True)
        except Exception as e:
            print(f"{e} enter on breakout")

    def exit_beyond_band(self):
        self.fn = self.enter_on_breakout
        try:
            symbols_to_remove = []
            for idx, row in self.df_delivered.iterrows():
                if row["Ltp"] > row["Reward"] or row["Ltp"] < row["Risk"]:
                    resp = Helper.place_order(
                        symbol=idx,
                        quantity=row["Qty"],
                        side="S",
                        price=0,
                        order_type="MKT",
                    )
                    if resp:
                        print("squared off")
                        dct = {
                            "Symbol": idx,
                            "Abv": row["Abv"],
                            "Risk": row["Risk"],
                            "Reward": row["Reward"],
                            "Qty": row["Qty"],
                            "Ltp": row["Ltp"],
                            "BDate": row["BDate"],
                            "SDate": pdlm.now("Asia/Kolkata"),
                        }
                        df_new = pd.DataFrame([dct])
                        df_new.to_csv(HISTORY, mode="a", index=False, header=False)
                        symbols_to_remove.append(idx)
            self.df_delivered.drop(index=symbols_to_remove, inplace=True)
        except Exception as e:
            logging.error(f"{e} exit beyond band")

    def save_dfs(self):
        self.df_delivered.to_csv(DELIVERED)

    def run(self, prices):
        # update df stocks in play and df_delivered with prices
        # update dataframe with price from dictionary with df.index as key
        try:
            self.df_stocks_in_play["Ltp"] = self.df_stocks_in_play.index.map(prices)
            self.df_delivered["Ltp"] = self.df_delivered.index.map(prices)
            print("STOCKS IN PLAY")
            print(self.df_stocks_in_play)
            print("\n DELIVERED")
            print(self.df_delivered)
            timer(3)
            self.fn()
        except Exception as e:
            logging.error(f"{e} in run")
