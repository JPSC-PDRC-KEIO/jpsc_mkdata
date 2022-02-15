"""
エディティングでの修正を反映するプログラム
前々年度以前のcsvファイルを更新する（研究所担当分）
"""
import os
import os.path
import shutil
import unicodedata
import numpy as np
import pandas as pd
import src.editing as editing


class DataFactory:
    def __init__(self, conf):
        self.conf = conf
        self.release_data_dir = os.path.join(
            self.conf.updated_data, self.conf.release_dir
        )
        self.prev_release_data_dir = os.path.join(
            self.conf.old_data, self.conf.release_dir_lag
        )

    def mk_update_dir(self):
        """
        昨年リリースデータをupdateディレクトリにコピー
        """
        try:
            shutil.rmtree(self.release_data_dir)
        except FileNotFoundError:
            pass

        shutil.copytree(self.prev_release_data_dir, self.release_data_dir)

    def del_prev_year_wave(self):
        """
        前年waveのデータを削除
        中央調査社から更新した前年データも納品されるため
        """
        last_year_wave = self.conf.latest_wave - 1
        dir_ = self.conf.panel_directories[last_year_wave]
        # eg. ["p21abcd","p21e"]
        for d in dir_:
            dirpath = os.path.join(self.conf.updated_data,
                                   self.conf.release_dir, d)
            shutil.rmtree(dirpath)

        if self.conf.latest_wave == 27:
            dir_lag_lag = self.conf.panel_directories[last_year_wave - 1]
            for d in dir_lag_lag:
                dirpath = os.path.join(
                    self.conf.updated_data, self.conf.release_dir, d)
                shutil.rmtree(dirpath)

    def update(self, wave, input_dir, output_dir):
        """
        wave年のエディティングリストの修正を反映
        """
        # el = EditingLists(wave)
        # editing_list = el.editing_list
        u = UpdateData(
            conf=self.conf,
            wave=wave,
            input_dir=input_dir,
            output_dir=output_dir
        )
        u.update()

    def update_latest_wave(self, input_dir, output_dir):
        """[summary]
        最新版のエディティング修正リストを反映
        :param input_dir: [description]
        :type input_dir: [type]
        :param output_dir: [description]
        :type output_dir: [type]
        :return: [description]
        :rtype: [type]
        """

        return self.update(
            wave=self.conf.latest_wave,
            input_dir=input_dir,
            output_dir=output_dir
        )

    def make(self):
        """
        継続データ（除前年調査）へのエディティング修正を行う
        データの格納ディレクトリ作成および前年リリースデータのコピー
        ↓
        前年調査のCSVデータを除外
        ↓
        リリース年度のエディティング情報を反映
        """
        print("継続データにエディティングの修正を施します")
        self.mk_update_dir()
        self.del_prev_year_wave()
        self.update_latest_wave(
            self.prev_release_data_dir, self.release_data_dir)


class UpdateData:
    """
    エディティングの修正指示をデータに反映させる。
    filename: エディティングリスト
    input_dir: 書き換えるファイル群があるディレクトリ、
    通常はdata/old_data/p*_release
    output_dir: 保存先ディレクトリ、通常は
    data/update_data/p22_release
    """

    def __init__(self, conf, wave, input_dir, output_dir):
        self.editing_df = editing.EditingLists(conf, wave)
        self.header = self.editing_df.header
        self.input_path = input_dir  # eg. data/old_data/p21_releas
        self.output_path = output_dir  # ex. data/update_data/p22_release

    def update(self):
        all_sheets = self.editing_df.all_sheets
        ID_ = self.header["ID"]
        trgt_files = self.header["trgt_file"]
        original = self.header["original"]
        update = self.header["update"]
        var_name = self.header["var_name"]

        for name, group in all_sheets.groupby(trgt_files):
            """
            修正があるファイルごとに処理を実行
            name -> 修正を施すデータファイル名（ex p1_1）
            group-> 修正を施すデータファイルごとに更新指示の情報を格納

            例 p9_1,p9_2... と指示を分けていく
               調査年 フォルダ 該当ファイル  ID  変数名  内容  変更前  変更後
            119    9    9   p9_1   755  Q18  家族3人目  年齢    5    4
            5      9    9   p9_1  2189   Q8       本人年齢   28   31
               調査年 フォルダ 該当ファイル  ID  変数名  内容  変更前  変更後
            47    9    9   p9_2  913  Q371  住居    3    2
            66    9    9   p9_2  914  Q371  住居    3    2
            """

            msg = "{0}の修正を行います".format(name)
            print(msg)
            # 読み込み元
            input_path_leaf = "{folder}/{file}.csv".format(
                folder=name[:-2], file=name)
            # eg. p9/p9_1.csv

            input_file_path = os.path.join(self.input_path, input_path_leaf)
            # eg. data/old_data/p21_release/p9/p9_1.csv
            # 一年前リリースディレクトリ

            input_data = pd.read_csv(
                input_file_path, index_col="ID", na_values=np.nan)

            # 出力先
            output_path_leaf = "{folder}/{file}.csv".format(
                folder=name[:-2], file=name)
            output_file_path = os.path.join(self.output_path, output_path_leaf)
            # eg. data/old_data/p21_release/p9/p9_1.csv
            output_data = input_data.copy(deep=True)

            for i, g in group.T.items():
                """
                修正を施すデータファイル(ex p9_2)について、修正項目ごとに情報を抽出
                i -> 各修正項目 のデータ上のindex(Name) 必要な情報ではない
                g -> 項目ごとの情報

                例
                調査年          9
                フォルダ         9
                該当ファイル    p9_2
                ID         913
                変数名       Q371
                内容          住居
                変更前          3
                変更後          2
                Name: 47, dtype: object

                調査年          9
                フォルダ         9
                該当ファイル    p9_2
                ID         914             'ID_'
                変数名       Q371           'var_name'
                内容          住居
                変更前          3           'original'
                変更後          2           'update'
                Name: 66, dtype: object
                """

                id_num = int(g[ID_])
                org = g[original]
                upd = g[update]
                vname = g[var_name]
                vname = unicodedata.normalize("NFKC", vname)
                vname = vname.upper()

                # 値がリストでかえるため複数の値があった場合の処理
                assert (
                    len(input_data.loc[id_num, [vname]]) > 0
                ), """{sheet}, ID={id}, 変数名={vname} について、
                    元ファイルでデータが重複しています""".format(
                    sheet=name, id=int(id_num), vname=vname
                )

                # 修正指示のある項目について変更前のファイルの値
                corg = input_data.loc[id_num, [vname]][0]

                # 指示されている変更前の数字とファイルに記入されている
                # 数字が異なる場合、警告を出す
                if pd.isnull(corg) and pd.isnull(org):
                    # excel修正指示ファイルの空白行をスキップ
                    pass

                else:
                    msg = """{sheet}, ID={idn} ,{vname}.
                        について、{uorg}を{upd}に修正するよう指示されていますが、
                        変更前のCSVファイルの値は {corg}が入っています """
                    msg = msg.format(
                        sheet=name,
                        idn=int(id_num),
                        vname=vname,
                        corg=corg,
                        uorg=org,
                        upd=upd,
                    )
                    assert output_data.loc[id_num, [vname]][0] == org, msg

                # エディティングの修正を記入
                output_data.loc[id_num, [vname]] = upd

            # csvファイルへ整数で記入
            output_data.to_csv(output_file_path, mode="w", float_format="%d")


if __name__ == "__main__":

    d = DataFactory()
    d.make()
