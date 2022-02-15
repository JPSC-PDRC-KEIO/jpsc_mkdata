# -*- coding: utf-8 -*-
"""
縦断面での整合性をチェックするテスト
ルートディレクトリから実行のこと

TestAge:年齢の整合性（1歳刻み）をチェック
"""


import csv
import datetime
import functools as ft
import glob
import logging
import os
import sys

import pandas as pd

import src.dirconfig as dconf
from nose.tools import eq_, ok_, raises

sys.path.append(os.getcwd())


# logging.basicConfig(filename='example.log',level=logging.DEBUG)
# logging.debug('This message should go to the log file')
# logging.info('So should this')
# logging.warning('And this, too')


class TestAge:
    @classmethod
    def setup_class(cls):
        d = datetime.datetime.now()
        print(d.strftime("%Y-%m-%d %H:%M:%S"))
        dirs_ = dconf.Settings()
        pp = dirs_.update_data_prnt
        prnt_path = os.path.join(pp, "*")
        path = os.path.join(prnt_path, "p*_1.csv")

        p_1files = [pd.read_csv(f) for f in glob.glob(path)]
        p_1files_merge = pd.concat(p_1files)
        ages = p_1files_merge[["ID", "PANEL", "Q8"]]
        ages = ages.set_index(["ID", "PANEL"]).to_panel()

        shifted = ages.shift(periods=1, axis=2)
        ages_diff = ages.ix["Q8", :, :] - shifted.ix["Q8", :, :]
        ages_diff = ages_diff.fillna(1)
        """
        ages_diff: ID × PANEL 値はQ8の前年差分
        """
        cls.ages = ages
        cls.ages_diff = ages_diff

        # 1となるのは、前年から1歳増えていたとき、当年が欠測(脱落)
        # 前年が欠測（新規、復活）***復活の場合の処理
        cls.consistency = ages_diff == 1

    def test_age_consistency(self):
        cnst = TestAge.consistency
        print("年齢が1歳刻みになっているかのテスト")
        assert cnst.all().all()

    def get_inconsistent_ID(self):
        """
        どのIDと調査年が不整合となっているかのCSV形式で表を作成、
        テストが失敗したときに走らせる
        結果は　tests/inconsistent/年齢不整合PANEL_ID.csv に保存
        """
        cnst = TestAge.consistency
        cnst_us = cnst.unstack()  # long形式で年齢の真偽を記述した'Series' object
        incnst_us = cnst_us.apply(lambda x: not (x))  # 不整合を基準にするため反転

        if incnst_us.any().any():
            # 年齢不整合が発生している調査年とID
            panel_id = cnst_us[incnst_us].index.tolist()
            if not os.path.exists("tests/inconsistent"):
                os.mkdir("tests/inconsistent")
            with open("tests/inconsistent/年齢不整合PANEL_ID.csv", "w") as out:
                csv_out = csv.writer(out)
                csv_out.writerow(["PANEL", "ID"])
                for row in panel_id:
                    csv_out.writerow(row)

            # 年齢不整合があるIDの全調査期間の年齢
            wrong_id = cnst.apply(lambda x: x[x == False]).index
            wrong_id_ages = TestAge.ages.loc["Q8", wrong_id, :]
            wrong_id_ages.to_csv("tests/inconsistent/年齢不整合ID_全年.csv", encoding="utf-8")


if __name__ == "__main__":
    TestAge.setup_class()
    t = TestAge()
    t.get_inconsistent_ID()
