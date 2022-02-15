# -*- coding: utf-8 -*-

import os
import re
import numpy as np
import pandas as pd
import zenhan
import glob


class EditingLists:
    """
    エディティングの修正リストを扱うクラス
    属性としてファイル名(パス)
    修正指示表をpandasのDataFrameに変換したものを保持

    パラメーター
    wave:調査年
    """

    def __init__(self, conf, wave):
        self.conf = conf
        self.wave = wave
        # d = dconf.Settings()
        self.editing_lists_path = self.conf.editing_dir
        self.list_name_base = self.conf.editing_file
        self.header = {
            "trgt_file": "該当ファイル",
            "var_name": "変数名",
            "original": "変更前",
            "update": "変更後",
            "ID": "ID",
            "year": "調査年",
            "cntnt": "内容",
        }

    @property
    def editing_list(self):
        """
        self.wave年実施のエディティングリストのPATHを取得
        """
        basename = self.list_name_base
        filename = basename.format(wave=self.wave)
        elist = os.path.join(self.editing_lists_path, filename)
        self._editing_list = elist
        return self._editing_list

    # 未実装
    @property
    def editing_lists_all(self):
        elists = glob.glob(self.editing_lists_path)
        # TODO: 全年のファイルの修正を実行できるようにする
        # 変更前と変更後の値をチェックするため
        # 今のところ修正後のファイルに上書きはできない

        elists = sorted(elists)
        # 文字の値でソートしているだけなので,p10 以上が前提
        self._editing_lists = elists
        return self._editing_lists

    @property
    def all_sheets(self):
        """
        修正指示ファイル（Excel Book）に含まれるすべてのシートを結合
        pandasのDataFrameで保持
        """
        e = pd.ExcelFile(self.editing_list, engine="openpyxl")
        sheet_names = e.sheet_names
        usheets = [e.parse(n) for n in sheet_names]

        # 各シートのヘッダーが要件を満たしているか
        [self._validate_header(list(u.columns)) for u in usheets]

        # シートの結合、空白行は削除
        all_sheets = pd.concat(usheets).dropna(how="all")
        all_sheets.replace("SYSMIS", np.nan, inplace=True)

        # 全角での入力があった場合、半角に統一
        all_sheets["変数名"] = all_sheets["変数名"].map(
            lambda x: zenhan.z2h(x) if isinstance(x, str) else x
        )
        all_sheets["該当ファイル"] = all_sheets["該当ファイル"].map(
            lambda x: zenhan.z2h(x) if isinstance(x, str) else x
        )

        # 変数名は大文字で、シート名は小文字で統一
        all_sheets["変数名"] = all_sheets["変数名"].map(
            lambda x: x if type(x) != str else x.upper()
        )
        all_sheets["該当ファイル"] = all_sheets["該当ファイル"].map(
            lambda x: x if type(x) != str else x.lower()
        )
        self._all_sheets = all_sheets
        return self._all_sheets

    def _validate_header(self, sheet_header):
        """
        修正指示ファイル、各シートのヘッダーが要件を満たしているか判断
        """
        # 重複要素がないか
        # pandas の DataFrame を使う場合は重複名を自動的に.数字に修正する
        ovrlp = [x for x in sheet_header if re.search("\.[1-9]", x)]

        assert len(ovrlp) == 0, "修正シートのヘッダーに重複があります. {0}".format(str(ovrlp))

        # 必要な要素が入っているか
        sh_set = set(sheet_header)  # シートのヘッダー
        header_set = set(self.header.values())  # 必要とする要素
        not_fnd = header_set.difference(sh_set)
        assert header_set.issubset(sh_set), "修正シートのヘッダーに次の要素がありません. {0}".format(
            str(not_fnd)
        )

        return True
