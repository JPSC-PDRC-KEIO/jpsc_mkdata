import pandas as pd
from pathlib import Path


class TapeFormats:
    """
    固定長データの情報を記載したテープフォーマットから、変数名とアドレスを取得
    """

    def __init__(self, path: Path, panel: Path, num_sheets: int):
        """[summary]

        :param path: テープフォーマットのディレクトリ
        :type path: Path
        :param panel: データ格納ディレクトリ e.g. p27
        :type panel: Path
        :param num_sheets: フォーマットのエクセルブックのシート数，5
        :type num_sheets: int
        """
        tape_formats_dir = path
        filename = f"formatn{panel}.xls*"  # p22以前がxls形式，p23以降がxlsx形式
        tape_formats: list[Path] = list(tape_formats_dir.glob(filename))
        self.format_book = tape_formats

        # シートの枚数
        self.num_sheets = num_sheets

    @property
    def format_book(self) -> pd.ExcelFile:
        return self._format_book

    @format_book.setter
    def format_book(self, tape_formats: list[Path]):
        if (n := len(tape_formats)) > 1:
            raise Exception("該当するテープフォーマットが2つ以上含まれています")
        elif n == 0:
            raise Exception("該当テープフォーマットが含まれていません")
        else:  # n==1
            pass
        self._format_book = pd.ExcelFile(tape_formats[0])

    @property
    def sheet_list(self) -> list[pd.DataFrame]:
        """
        中調のテープフォーマットの5枚のシートをPandasのデータフレームに変換
        各シートの情報を要素としたリストを返す
        :return: テープフォーマットについて，[sheet1のデータフレーム, ..., sheet5のデータフレーム]
        :rtype: list[pd.DataFrame]
        """

        sheet_names = [
            "Sheet{n}".format(n=i) for i in range(1, self.num_sheets + 1)
        ]  # [Sheet1,Sheet2,...,Sheet5]

        # 中調テープフォーマットのヘッダー
        org_headers = ["変数名", "アドレス", "桁数"]

        # 中調テープフォーマットのヘッダーをアルファベットに変換
        # プログラム中で日本語を使うのを避けたいだけの理由
        rename_header_map = {
            "変数名": "var_names",
            "アドレス": "address_starts",
            "桁数": "address_widths",
        }
        fbook = self.format_book

        # 中調ファイルをそのままデータフレームにしたリスト(ヘッダーそのまま)
        org_dfs = [
            pd.DataFrame(fbook.parse(sn), columns=org_headers) for sn in sheet_names
        ]

        # 変数名の付け替え
        dfs = []
        for df in org_dfs:
            df_renamed = df.rename(columns=rename_header_map)
            df_renamed["address_ends"] = (
                df_renamed.address_starts + df_renamed.address_widths
            )
            dfs.append(df_renamed)

        self._fmtfile_data_frames = dfs
        return self._fmtfile_data_frames

    @property
    def addresses(self):
        """
        テープフォーマットから、各変数についてアドレス情報、(始点、終点)の組を作成
        """
        addresses = []
        for f in self.sheet_list:  # [sheet1, ..., sheet5] f はDataFrame
            d = f[["var_names", "address_starts", "address_ends"]]
            d2 = d[d.var_names.notnull()]

            # (始点、終点)の組
            # アドレスの開始位置をずらす pythonは0が起点
            # address_ends は address_starts + address_width
            # なので,こちらも-1
            # [from,to[ 半開区間
            s = (d2.address_starts - 1).astype(int)
            e = (d2.address_ends - 1).astype(int)
            address = list(zip(s, e))
            addresses.append(address)

        self._addresses = addresses
        return self._addresses

    @property
    def headers(self):
        """
        テープフォーマットからヘッダー情報（変数名）を抽出
        """
        fmts = self.sheet_list

        # 家計研側でふった変数名がない場合はスキップ
        headers = [f.var_names[f.var_names.notnull()] for f in fmts]

        # DataFrameからリストへ
        self._headers = [h.tolist() for h in headers]
        return self._headers
