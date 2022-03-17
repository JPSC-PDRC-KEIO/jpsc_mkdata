# -*- coding: utf-8 -*-
"""
エディティングの修正指示と、実際のデータでとった差分が一致するかをチェック
ルートディレクトリで実行すること
"""

import os
import sys

import pandas as pd

import src.dirconfig as dconf
import src.editing as editing

sys.path.append(os.getcwd())
sys.path.append("../")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


d = dconf.Settings()
lw = d.latest_wave  # 最新年度（=当該リリース年度）

# 下記3点で比較する値が一意に決まる
indx = ["ID", "変数名", "シート"]

# 欠測用の埋め草、差をとって比較するため適当な値を挿入
pad_nan = 9999999


# エディティング修正指示のファイル
e = editing.EditingLists(lw)
editing_table = e.all_sheets
# 22リリースのみ、パネル20時の修正かけ忘れへの対応
if lw == 22:
    e20 = editing.EditingLists(20)
    editing_table20 = e20.all_sheets
    editing_table = pd.concat([editing_table, editing_table20])

editing_table = editing_table[["ID", "変数名", "該当ファイル", "変更前", "変更後"]]
editing_table.rename(columns={"該当ファイル": "シート"}, inplace=True)
editing_table = editing_table.reset_index(drop=True).set_index(indx)
editing_table.sort_index(inplace=True)
editing_table.fillna(pad_nan, inplace=True)
# editing_table.to_csv("edit.csv")


# 継続データ（直近2年以前実施データ）の前年リリースとの差分
keizoku_path = "diffs/p{w}_release/diffs_keizoku.csv".format(w=lw)
keizoku_diffs = pd.read_csv(keizoku_path, skipinitialspace=True)
keizoku_diffs.rename(columns={"変更シート": "シート"}, inplace=True)
keizoku_diffs.fillna(pad_nan, inplace=True)
keizoku_diffs = keizoku_diffs.reset_index(drop=True).set_index(indx)
keizoku_diffs.sort_index(inplace=True)
# keizoku_diffs.to_csv("keizoku.csv")

ne = keizoku_diffs - editing_table


def test_before(ne=ne):
    print("変更があった変数について、変更前の値は一致しているか")
    assert all(ne["変更前"] == 0)


def test_after(ne=ne):
    print("変更があった変数について、変更前の値は一致しているか")
    assert all(ne["変更前"] == 0)
