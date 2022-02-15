"""
新規リリースデータ作成用モジュール
中央調査社から納品された固定長ファイル(直近2年分)を変数名をつけてCSVファイルに変換
"""

import csv
import os
import numpy as np
import pandas as pd
from pathlib import Path

from src.dirstruct import DirStructure  # noqa
from src.tape_formats import TapeFormats  # noqa


class DataFactory:
    """
    csvに変換する固定長ファイル（今年度分と昨年度分、各5枚）の一覧を取得し
    すべてをcsvに変換、update ディレクトリに書き込み
    """

    def __init__(self, dir_struct: DirStructure):
        self.dir_struct = dir_struct

    def execute(self):
        """
        CSVファイルの作成、保存の実行
        """
        # e.g. [p27, p28]
        shinki_dirs: list[Path] = self.dir_struct.shinki_data_dirs
        release_dir_name: Path = self.dir_struct.release_dir  # p*_release

        print("固定長データをCSVに変換します")
        for pnl in shinki_dirs:
            fwf_pnl_dir: Path = (
                self.dir_struct.fixed_width_data / release_dir_name / pnl
            )
            updated_pnl_dir: Path = (
                self.dir_struct.updated_data / release_dir_name / pnl
            )
            tf = TapeFormats(
                path=self.dir_struct.tape_formats,
                panel=pnl,
                num_sheets=self.dir_struct.num_sheets,
            )
            FixedToCsv(fwf_pnl_dir, updated_pnl_dir, tape_formats=tf).execute()


class FixedToCsv:
    """
    固定長データの格納ディレクトリ（p21bcd, p21e, p22, ..., etc）単位で
    テープフォーマットの情報を反映させたcsvファイルを作成、
    該当ディレクトリに書き込みを行う
    """

    def __init__(
        self, fwf_pnl_dir: Path, updated_pnl_dir: Path, tape_formats: TapeFormats
    ):
        """

        :param fwf_pnl_dir: 固定長データの格納ディレクトリ
        e.g. data/fixed_width_data/p27_release/p7
        :type fwf_pnl_dir: Path
        :param updated_pnl_dir: 変換したCSVデータの書き込み先ディレクトリ
        e.g. data/released_data/p27_release/p27
        :type updated_pnl_dir: Path
        :param tape_formats: 該当年のテープフォーマット情報を記載したオブジェクト
        :type tape_formats: TapeFormats
        """

        self.updated_pnl_dir = updated_pnl_dir
        self.tf = tape_formats  # TapeFormats(fixed_data_path)
        self.fwf_names = FixedWidthFiles(
            fwf_pnl_dir, num_sheets=self.tf.num_sheets
        ).file_names

    def _mkdir(self):
        """
        csvの書き込み先ディレクトリ（update_data以下）の作成
        該当ファイルが既にあった場合はエラーを出して処理が止まるようにしている
        既存フォルダの中身を確認してから、手動で除去すること
        """
        try:
            print(f"{self.updated_pnl_dir}を作成しています")
            os.mkdir(self.updated_pnl_dir)
        except FileExistsError:
            print(f"{self.updated_pnl_dir.parent.name}が存在します")
            print("中身を確認した上で、ディレクトリを取り除いてください")

    def execute(self):
        """
        csvファイルへの書き込み
        """
        self._mkdir()
        csv_path_prnt = self.updated_pnl_dir
        fnames = self.fwf_names  # 読み込む固定長ファイル名のリスト
        addresses = self.tf.addresses  # 各シートのアドレス情報をリストで格納
        headers = self.tf.headers  # 各シートのヘッダー情報をリストで格納
        files = zip(fnames, addresses, headers)

        for f in files:  # [../p1_1.txt,..., ../p1_5.txt]
            df = pd.read_fwf(f[0], colspecs=f[1], names=f[2])
            rec = df["REC"][0]
            assert rec in range(1, 6), "固定長ファイルの読み込みが失敗しています"

            csvfile = self.updated_pnl_dir.name + "_" + str(rec) + ".csv"
            csvfile_path = os.path.join(csv_path_prnt, csvfile)
            print(csvfile_path)
            df.to_csv(
                csvfile_path, index=False, quoting=csv.QUOTE_MINIMAL, float_format="%d"
            )


class FixedWidthFiles:
    """
    今回，納品された固定長データについて，ファイルのパスをリストで取得する
    """

    def __init__(self, new_fwf_data_path: Path, num_sheets: int):
        """
        :param new_fwf_data_path: 固定長データの格納フォルダ
        e.g. 29回納品であれば data/fixed_width_data/p29_release/p28 かp29
        :type new_fwf_data_path: Path
        :param num_sheets: テープフォーマットのシート数 5
        :type num_sheets: int
        """
        self.num_sheets = num_sheets
        # ftmp = os.path.join(released_fwf_data_path, "*.txt")
        self.file_names: list[Path] = list(new_fwf_data_path.glob("*.txt"))

        # TODO: file名と中身（record）が一致しているかチェックが必要 testで対応

    @property
    def file_names(self) -> list[Path]:
        return self._file_names

    @file_names.setter
    def file_names(self, file_names: list[Path]):
        file_names_sorted = sorted(file_names)
        # e.g. p1_1, p1_2, p1_3, p1_4, p1_5 の添え字： 1, 2, 3, 4, 5
        fwf_nums: list[str] = [f.stem[-1] for f in file_names_sorted]

        if len(file_names_sorted) != self.num_sheets:
            raise Exception("固定長ファイルが足りないか、余分なtxtファイルが含まれています", file_names)

        if fwf_nums != [str(i + 1) for i in range(self.num_sheets)]:
            # 添え字の数字順にデータのファイルがそろっているかチェック or 命名規則に沿わないファイルがあるか
            raise Exception("固定長ファイルの形式が整っていません", file_names)

        self._file_names = file_names_sorted


class CSVModified:
    """
    固定長データから作成したCSV（新規データ）へさらに以下の修正を加える．
    - 1日の生活時間，夫婦の会話時間のデータの分割
       - 時間と分が1変数3桁として格納されている仕様（＿＿時間＿０分）をそれぞれ2桁，2桁に分離
    - 居住地の全国地方公共団体コードの処理
       - 整数値で格納されているデータについて，文字列で5桁の0埋めにする
       - 新規に追加したデータは過去の引越し履歴にも同様の処理を行う
    """

    def __init__(self, dir_struct: DirStructure) -> None:
        self.dir_struct = dir_struct

    def execute(self) -> None:
        """
        以下の2つの処理を実行
        * 時間変数の時間と分への分離
        * 地域情報（地方公共団体コード）の5桁ゼロ埋め
        """
        print("新規のCSVデータに変更を加えます")
        self.timeuse()
        self.modify_residence_code()

    @property
    def hm_ordinary(self) -> list[str]:
        """
        従来の生活時間の変数名（在宅勤務時の生活時間をp28で別途，追加したため）．ローデータと不整合を調整した2種の変数群がある．
        :return: 変数名のリスト
        :rtype: list[str]
        """
        qnum1 = range(3, 7)
        qnum2 = ["A", "B", "C", "D", "I", "M"]  # 変数名 Q493～496のA、B、C、D、I、M
        var_listA = ["Q49" + str(q1) + q2 for q1 in qnum1 for q2 in qnum2]

        # 生活時間の変数　24時間不整合の修正あり(以前，エディティングで施していた修正)
        # Q9001～9004（本人／夫、平日／休日）
        qnum3 = range(1, 5)
        var_listB = ["Q900" + str(q3) + q2 for q3 in qnum3 for q2 in qnum2]
        var_lists = var_listA + var_listB
        return var_lists

    @property
    def hm_zaitaku(self) -> list[str]:
        """
        在宅勤務時の生活時間．p28から．ローデータのみ．
        :return: 変数名のリスト
        :rtype: list[str]
        """
        # 10月の在宅勤務日 妻（Q1250）・夫(Q1253)
        qnum1 = [50, 53]
        qnum2 = ["A", "B", "C", "D", "I", "M"]
        var_listA = ["Q12" + str(q1) + q2 for q1 in qnum1 for q2 in qnum2]
        return var_listA

    @property
    def hm_kaiwa(self) -> list[str]:
        """
        夫婦の会話時間
        :return: 変数名のリスト（1要素）
        :rtype: list[str]
        """
        return ["Q1232"]

    @property
    def hm_emergency(self):
        """
        緊急事態宣言中の平日時間　p28のみ
        :return: 変数名のリスト
        :rtype: list[str]
        """
        # 緊急事態宣言時の平日 妻（Q1285）・夫(Q1293)
        qnum1 = range(85, 93)
        qnum2 = ["A", "B", "C", "D", "I", "M"]
        var_listA = ["Q12" + str(q1) + q2 for q1 in qnum1 for q2 in qnum2]
        return var_listA

    def split_hour_minute(self, file_: str, var_lists: list[str]) -> None:
        """
        生活時間の分割処理（3ケタを2ケタと1ケタに分ける）
        格納する変数も2つに分離(e.g., Q493A -> Q493AH, Q493AM)
        :param file_: 時間変数が含まれるCSVファイル名（通常は``_3.csv``）
        :type file_: str
        :param var_lists: 変換する前の時間の変数名
        :type var_lists: list[str]
        """
        df = pd.read_csv(file_)
        # 分離と新変数への格納
        for v in var_lists:
            hour = v + "H"
            minute = v + "M"
            print(v)
            if v == "Q1232":  # 時間に関して夫婦の会話（Q1232）は1分単位（4桁），他は10分単位（3桁）で入っている
                df[hour] = np.floor_divide(df[v], 100)
                df[minute] = df[v] % 100
            else:
                df[hour] = np.floor_divide(df[v], 10)
                df[minute] = df[v] % 10
            df = df.drop(v, axis=1)
        df.to_csv(file_, index=False, float_format="%d")

    def timeuse(self) -> None:
        """
        時間と分に分離した時間変数のCSVファイルへの書き込み
        """
        print("生活時間の変数を時間と分に分離します")
        for c in self.dir_struct.updated_panel_dirs:
            bname = os.path.basename(c)
            var_lists = []
            if bname == "p27":
                var_lists = self.hm_ordinary + self.hm_kaiwa
            elif bname in ["p28", "p29"]:
                var_lists = self.hm_ordinary + self.hm_zaitaku + self.hm_kaiwa
            else:
                var_lists = self.hm_ordinary

            fname = bname + "_3.csv"
            fpath = c / Path(fname)
            print(f"{fname}を処理します")
            self.split_hour_minute(fpath, var_lists)

            if bname == "p28":  # 緊急事態宣言時の時間の処理　シート5にある
                fname2 = bname + "_5.csv"
                fpath2 = os.path.join(c, fname2)
                print(f"{fname}を処理します")
                self.split_hour_minute(fpath2, self.hm_emergency)

    def modify_residence_code(self) -> None:
        """
        居住地の地方公共団体コード（Q4）を5桁の0詰めで統一する．
        各コーホート新規の調査年は引越し履歴にも変更を加える
        :raises AssertionError: 該当変数が含まれるシート1（``_1.csv``）が複数ある場合
        """
        updated_dirs: Path = self.dir_struct.updated_data / self.dir_struct.release_dir
        print("居住地の地方公共団体コードを5桁にそろえます")
        """
        p_1files = []
        for dpath, _, fnames in os.walk(updated_dirs):
            if len(fnames) == 0:
                continue
            fname = [dpath/Path(f) for f in fnames if "_1.csv" in f]
            if not len(fname) == 1:
                msg = "{dir_} に1枚目のシートが複数含まれています".format(dir_=dpath)
                raise AssertionError(msg)
            p_1files = p_1files + fname
        """

        moving_histories = ["P33C", "P34C", "P35C", "P36C", "P37C"]
        # new_entries = [p + "_1" for p in self.dir_struct.new_entries]

        for file_path in updated_dirs.rglob("*_1.csv"):  # 　居住地変数は1枚目のシート
            data = pd.read_csv(file_path)
            data["Q4"] = data["Q4"].map(lambda x: "{0:05d}".format(x))
            # 新規サンプルのデータは引越し履歴の居住地コードも修正
            if file_path.parent.name in self.dir_struct.new_entries:
                for v in moving_histories:
                    data[v] = data[v].map(
                        lambda x: "{0:05d}".format(int(x)) if pd.notnull(x) else x
                    )
                print("{p}の引越し履歴を5桁にそろえました".format(p=file_path))
            data.to_csv(file_path, index=False, float_format="%.0f")
        return


"""
        for file_path in p_1files:
            data = pd.read_csv(file_path)
            print(file_path)
            data["Q4"] = data["Q4"].map(lambda x: "{0:05d}".format(x))

            # 新規サンプルのデータは引越し履歴の居住地コードも修正
            file_name, ext = os.path.splitext(os.path.basename(file_path))
            if file_name in new_entries:
                for v in moving_histories:
                    data[v] = data[v].map(
                        lambda x: "{0:05d}".format(
                            int(x)) if pd.notnull(x) else x
                    )
                print("{p}の引越し履歴を5桁にそろえました".format(p=file_name))
            data.to_csv(file_path, index=False, float_format="%.0f")
        return
"""
