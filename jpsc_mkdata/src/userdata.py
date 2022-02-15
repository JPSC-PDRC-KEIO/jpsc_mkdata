# -*- coding: utf-8 -*-
"""
ユーザーリリース用データの作成
"""
import csv
import os
import re
import shutil
import sys

import numpy as np
import pandas as pd

import src.dirstruct as dirstruct  # 設定全般ファイル
import src.dirconfig as dconf  # ディレクトリ設定ファイル

sys.path.append(os.getcwd())
sys.path.append("../")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class MakeDir:
    def __init__(self):
        self.cwd = os.getcwd()
        self._org_dir = None
        self._recode_dir = None
        self._pref_dir = None

    @property
    def org_dir(self):
        if not (self._org_dir):
            print("ディレクトリ名が入力されていません")
        else:
            return self._org_dir

    @org_dir.setter
    def org_dir(self, value):
        self._org_dir = os.path.abspath(value)

    @org_dir.deleter
    def org_dir(self):
        del self._org_dir

    @property
    def recode_dir(self):
        if not (self._recode_dir):
            print("ディレクトリ名が入力されていません")
        else:
            return self._recode_dir

    @recode_dir.setter
    def recode_dir(self, value):
        self._recode_dir = os.path.abspath(value)

    @recode_dir.deleter
    def recode_dir(self):
        del self._recode_dir

    @property
    def pref_dir(self):
        if not (self._pref_dir):
            print("ディレクトリ名が入力されていません")
        else:
            return self._pref_dir

    @pref_dir.setter
    def pref_dir(self, value):
        self._pref_dir = os.path.abspath(value)

    @pref_dir.deleter
    def pref_dir(self):
        del self._pref_dir

    def make_wave_sheets(self):

        odir = self.org_dir
        rdir = self.recode_dir
        pdir = self.pref_dir

        for root, dirs, files in os.walk(odir):
            if len(files) > 0:
                # Q2, Q4は、シート1だけに含まれる。
                fnames = [i for i in files if "_1.csv" in i]
                # p*_1.csv が複数個ある場合、ファイルを開いている場合は例外を発生
                if not len(fnames) == 1:
                    raise IndexError
                fname = fnames[0]

                # p*フォルダ
                waves = os.path.split(root)[1]
                recode_dir_waves = os.path.join(rdir, waves)
                data = pd.read_csv(os.path.join(root, fname))

                if fname in [
                    "p1_1.csv",
                    "p5b_1.csv",
                    "p11c_1.csv",
                    "p16d_1.csv",
                    "p21e_1.csv",
                ]:
                    data_pref = pd.DataFrame(
                        data,
                        columns=[
                            "ID",
                            "PANEL",
                            "Q4",
                            "P33C",
                            "P34C",
                            "P35C",
                            "P36C",
                            "P37C",
                        ],
                    )
                    var_pref = {
                        "Q4": "KEN",
                        "P33C": "KEN1",
                        "P34C": "KEN2",
                        "P35C": "KEN3",
                        "P36C": "KEN4",
                        "P37C": "KEN5",
                    }

                    data_pref.rename(columns=var_pref, inplace=True)
                    data["P33C"] = 99999
                    data["P34C"] = 99999
                    data["P35C"] = 99999
                    data["P36C"] = 99999
                    data["P37C"] = 99999

                    prefs = ["KEN", "KEN1", "KEN2", "KEN3", "KEN4", "KEN5"]
                    for p in prefs:
                        data_pref[p] = data_pref[p].map(
                            lambda x: "{0:.0f}".format(
                                x)[:-3] if pd.notnull(x) else x
                        )
                    data["Q4"] = data["Q4"].map(
                        lambda x: "{0:.0f}".format(x)[:-3])

                else:
                    data_pref = pd.DataFrame(
                        data, columns=["ID", "PANEL", "Q4"])
                    data_pref["Q4"] = data_pref["Q4"].map(
                        lambda x: "{0:.0f}".format(x)[:-3]
                    )
                    data_pref.rename(columns={"Q4": "KEN"}, inplace=True)

                # Q2, Q4の置き換え
                #data["Q2"] = 9
                data["Q4"] = 99999

                # ユーザーリリース用データ（地域情報を含まない）の保存
                data.to_csv(
                    os.path.join(recode_dir_waves, fname),
                    index=False,
                    quoting=csv.QUOTE_NONE,
                    float_format="%.0f",
                )

                # 都道府県データの保存＝>"prefecture"ディレクトリに作成
                fname = os.path.splitext(fname)
                fname_pref = fname[0][:-2] + "pref" + fname[1]
                data_pref.to_csv(
                    os.path.join(pdir, fname_pref),
                    index=False,
                    quoting=csv.QUOTE_NONE,
                    float_format="%.0f",
                )


class DataFactory:
    def __init__(self, conf):
        self.d = conf
        print(self.d)

    def make(self):
        m = MakeDir()
        user_data_dir = os.path.join(self.d.user_data, self.d.release_user_dir)
        org_dir = os.path.join(user_data_dir, "original")
        recode_dir = os.path.join(user_data_dir, "recode")
        pref_dir = os.path.join(user_data_dir, "prefecture")
        m.org_dir = org_dir
        m.recode_dir = recode_dir
        m.pref_dir = pref_dir
        m.make_wave_sheets()
