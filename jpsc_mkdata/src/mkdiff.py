# -*- coding: utf-8 -*-
import filecmp as fc
import os
import sys

import numpy as np
import pandas as pd
import xarray as xr

import src.dirconfig as dconf

# sys.path.append(os.getcwd())
# sys.path.append("../")
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class DiffAllFiles:
    def __init__(self):
        f = Files_()
        self.changed_files = f.changed_files
        self.changed_keizoku_shinki = f.changed_keizoku_shinki
        self.pad = DiffCheck.PAD
        self.pad_nan = DiffCheck.PAD_NAN
        self.d = dconf.Settings()
        release = self.d.pdir
        diffs = self.d.diffs_dir
        self.path_ = os.path.join(diffs, release)

    @property
    def overwritten_IDs_all(self):
        """
        すべてのシートについての変更情報を
        pandasのPanel DataFrameで保存（items->panel(調査年)）。
        panel × ID × 変数
        """
        changed_files = self.changed_files
        overwritten_IDs_list = []
        print("本年度と昨年度のリリースデータの差分をとります")
        for file in changed_files:
            fname, ext = os.path.splitext(os.path.basename(file[0]))
            d = DiffCheck(file[0], file[1])
            if len(d.diff_panel.major_axis) == 0:
                continue
            print("{0}の差分を書き込んでいます".format(fname))
            # overwritten_IDs[fname] = d.overwritten_ID
            oIDs = d.overwritten_ID.assign_coords(sheet=fname)
            overwritten_IDs_list.append(oIDs.expand_dims("sheet"))
        # print("overwritten")
        # print(type(overwritten_IDs))
        # print(overwritten_IDs.head())
        # overwritten_IDs = pd.Panel4D(overwritten_IDs)
        # print(overwritten_IDs)

        self._overwritten_IDs_all = xr.merge(overwritten_IDs_list)
        return self._overwritten_IDs_all

    def overwritten_IDs_separate(self, dtype="keizoku"):
        """
        すべてのシートについて変更情報を
        pandaのPanel DataFrameで保存（items->panel(調査年)）。
        panel × ID × 変数
        
        overwritten_ID_allメソッドで得られる
        差分を新規（昨年データ）と継続に分けて出力
        パラメータ
        dtype: 
        'keizoku'-> 継続データ（直近2年より前のデータ）
        'shinki' -> 新規ータ（昨年データ）
        """
        changed_files = self.changed_keizoku_shinki
        changed_data_type = changed_files[dtype]
        data_type_dict = {"keizoku": "継続", "shinki": "新規"}
        overwritten_IDs_list = []
        msg = "{dtype}データについて、本年度と昨年度のリリースデータの差分をとります".format(
            dtype=data_type_dict[dtype]
        )
        print(msg)
        print("chngd data", changed_data_type)
        for file in changed_data_type:
            print("file", file)
            fname, ext = os.path.splitext(os.path.basename(file[0]))
            d = DiffCheck(file[0], file[1])
            print("diff_panel dict")
            # print("dd", d.diff_panel.__dict__)
            print("dd", d.diff_panel.__slots__)
            print(d.diff_panel.coords["ID"])
            if len(d.diff_panel.coords["ID"]) == 0:
                continue
            print("{0}の差分を書き込んでいます".format(fname))
            oIDs = d.overwritten_ID.assign_coords(sheet=fname)
            overwritten_IDs_list.append(oIDs.expand_dims("sheet"))
            # overwritten_IDs[fname] = d.overwritten_ID
        # print("overwritten2")
        # overwritten_IDs = xr.Dataset.from_dict(overwritten_IDs)
        overwritten_IDs = xr.merge(overwritten_IDs_list)
        return overwritten_IDs

    def outputs_stacked(self, diffs):
        """
        変更情報について、panel×ID×変数のPanel DataFrame
        (outputs_stackedメソッドの戻り値)をpanel方向にばらす
        パラメータ
        diffs: 変更情報を格納したPanel DataFrame,
        通常、outputs_stackedメソッドの戻り値
        """
        pad = self.pad
        pad_nan = self.pad_nan
        # dall = []
        # print("diffs")
        # print(type(diffs))
        # print(diffs.__dict__)
        # print(diffs)
        # for pnl in diffs.labels:
        """
        for pnl in diffs.sheet:
            print("pnl")
            print(type(pnl))
            print(pnl.__dict__)

            #d = diffs[pnl, :, :, :]
            d = diffs.sel(sheet=pnl)
            print("d", d)
            #d.minor_axis.names = ["変数名"]
            #d = d.to_frame()
            #d["変更シート"] = pnl
            #dall.append(d)
        """
        # dall = pd.concat(dall)
        print(diffs)
        diffs_df = diffs.to_dataframe()
        if len(diffs_df) == 0:
            dall = diffs_df
        else:
            dall = diffs_df.stack()
            dall = dall.unstack(level=-1)
            # print("dall", dall)
            dall = dall.reset_index()
            # 変更のない変数については除外
            dall = dall[(dall["変更前"] != pad) & (dall["変更後"] != pad)]
            # 欠測の埋め草をnp.nanに戻す
            dall.replace(pad_nan, np.nan, inplace=True)
        return dall

    @property
    def outputs_all_stacked(self):
        """
        継続、新規のデータを分けずに、変更のあったIDとシートを
        DataFrameで返す。
        ID × ["変数名", "変更前", "変更後", "変更シート"]
        """
        diffs = getattr(self, "_overwritten_IDs_all", self.overwritten_IDs_all)
        dall = self.outputs_stacked(diffs=diffs)
        self._outputs_all_stacked = dall
        return self._outputs_all_stacked

    @property
    def outputs_keizoku_stacked(self):
        """
        継続データ（直近2年以前調査データ）について
        変更のあったIDとシートをDataFrameで返す。
        ID × ["変数名", "変更前", "変更後", "変更シート"]
        """
        diffs = self.overwritten_IDs_separate(dtype="keizoku")
        dall = self.outputs_stacked(diffs=diffs)
        print("dall")
        print(dall)
        self._outputs_keizoku_stacked = dall
        return self._outputs_keizoku_stacked

    @property
    def outputs_shinki_stacked(self):
        """
        新規データ（昨年調査データ）について
        変更のあったIDとシートをDataFrameで返す。
        ID × ["変数名", "変更前", "変更後", "変更シート"]
        """
        diffs = self.overwritten_IDs_separate(dtype="shinki")
        dall = self.outputs_stacked(diffs=diffs)
        self._outputs_shinki_stacked = dall
        return self._outputs_shinki_stacked

    def _mk_diff_dir(self):
        try:
            os.mkdir(self.path_)
        except FileExistsError:
            pass

    def all_csv(self):
        self._mk_diff_dir()
        diffs = getattr(self, "_outputs_all_stacked", self.outputs_all_stacked)
        fname = os.path.join(self.path_, "diffs_all.csv")
        diffs.to_csv(fname, index=False)
        return

    def keizoku_csv(self):
        self._mk_diff_dir()
        diffs = getattr(self, "_outputs_keizoku_stacked", self.outputs_keizoku_stacked)
        print(diffs)
        fname = os.path.join(self.path_, "diffs_keizoku.csv")
        diffs.to_csv(fname, index=False)

    def shinki_csv(self):
        self._mk_diff_dir()
        diffs = getattr(self, "_outputs_shinki_stacked", self.outputs_shinki_stacked)
        fname = os.path.join(self.path_, "diffs_shinki.csv")
        diffs.to_csv(fname, index=False)


class Files_:
    def __init__(self):
        self.d = dconf.Settings()

    @property
    def filesets(self):
        """
        新旧リリースの全ファイル(csv）のパスを、ペアで取得
        """
        d = self.d
        fsets = []
        old_path = d.old_data_prnt_lag
        upd_path = d.update_data_prnt
        if __name__ == "__main__":
            old_path = os.path.join("..", old_path)
            upd_path = os.path.join("..", upd_path)

        for root, dirs, files in os.walk(old_path):
            for f in files:
                old_file = os.path.join(root, f)
                b = os.path.basename(root)  # ex. p20,p21abcd,p21e,...
                upd_file = os.path.join(upd_path, b, f)
                fsets.append([old_file, upd_file])
        self._filesets = fsets
        return self._filesets

    @property
    def changed_keizoku_shinki(self):
        """
        changed_filesメソッドで得られる変更のあったデータセットを
        新規データと継続データに分ける。
        戻り値：下記のような、リストを値にもつ辞書形式
        {'shinki': [('data/old_data/p21_release/p21abcd/p21abcd_1.csv',
        'data/update_data/p22_release/p21abcd/p21abcd_1.csv'),...,
        ('data/old_data/p21_release/p21e/p21e_5.csv',
        'data/update_data/p22_release/p21e/p21e_5.csv')],
        'keizoku': [('data/old_data/p21_release/p1/p1_2.csv',
        'data/update_data/p22_release/p1/p1_2.csv'),...
        ('data/old_data/p21_release/p17/p17_5.csv',
        'data/update_data/p22_release/p17/p17_5.csv')]
        """
        d = self.d
        filesets = getattr(self, "_changed_files", self.changed_files)
        shinki = []
        keizoku = []
        for f in filesets:
            file_name, ext = os.path.splitext(os.path.basename(f[0]))
            file_name_base = file_name[:-2]
            if file_name_base in d.shinki_data_dirs_name:
                shinki = shinki + [tuple(f)]
            else:
                keizoku = keizoku + [tuple(f)]
        filesets_dict = {"shinki": shinki, "keizoku": keizoku}

        self._changed_keizoku_shinki = filesets_dict
        return self._changed_keizoku_shinki

    @property
    def changed_files(self):
        """
        昨年リリースデータと本年度リリースデータに差がある
        データファイル名セットをリストで取得。
        filecmpモジュールのcmpメソッドで
        ファイルの組に差の存在を検出。
        """
        filesets = self.filesets
        chngd_files = []
        for files in filesets:
            if not fc.cmp(*files):
                chngd_files.append(files)

        self._changed_files = chngd_files
        return self._changed_files


class DiffCheck:
    """
    昨年リリースデータと本年度リリースデータの差分を抽出

    下記サイトのプログラムを援用
    'Using Pandas To Create an Excel Diff' 
    http://pbpython.com/excel-diff-pandas.html

    プログラムの骨子は、新旧データを結合して重複行があるかどうかを判断。
    各IDの内容に変更がなければ、結合データで重複行となることを利用.
    """

    # 非該当などの埋め草用。回答に6桁のコードがないことを前提
    PAD = 999999
    PAD_NAN = sys.maxsize

    def __init__(self, old_file, update_file):
        self.old = pd.read_csv(old_file)
        self.upd = pd.read_csv(update_file)

    def report_diff(self, x):
        """
        ファイル間で変更がある場合、変更後の値を記入。
        用途として、ID×変数のDataFrameへのapllyを想定。
        x＝変数を引数とし、各IDについてapply。
        overwritten_ID プロパティを作成する際に使用。
        """
        # ファイル間で値が同じ（両方欠測の場合も）かどうか、
        # 同じならDiffCheck.PAD(=999999)を返す。
        # DiffCheck.PADは別処理で除外する
        pad = DiffCheck.PAD
        if x[0] == x[1]:
            r = pd.Series([pad, pad], index=["変更前", "変更後"])
        else:
            r = pd.Series([x[0], x[1]], index=["変更前", "変更後"])
        return r

    @property
    def full_set(self):
        """
        昨年度と本年度の新旧データを、
        各データファイル(ex. p10_1,P10_2,...)の単位で結合。
        'version'という変数を追加し、新旧を識別。
        """
        old = self.old
        upd = self.upd
        old["version"] = "old"
        upd["version"] = "update"

        # Join all the data together and ignore indexes
        # so it all gets added
        full_set = pd.concat([old, upd], ignore_index=True)

        self._full_set = full_set
        return self._full_set

    @property
    def changed_vars(self):
        """
        昨年度と本年度のデータで値が変わった変数の組を抽出。
        変更のあったIDが多い場合に呼び出す。
        """
        old = self.old
        upd = self.upd
        pad_nan = DiffCheck.PAD_NAN
        old.fillna(pad_nan, inplace=True)
        upd.fillna(pad_nan, inplace=True)
        upd = upd[upd["ID"].isin(old["ID"])]
        old = old.transpose()
        upd = upd.transpose()

        # Join all the data together and ignore indexes
        # so it all gets added
        full_setT = pd.concat([old, upd], ignore_index=False)

        full_setT.drop_duplicates(inplace=True)
        self._changed_vars = full_setT.index[full_setT.index.duplicated()]
        # self._changed_vars = full_setT.index.get_duplicates() depricated
        return self._changed_vars

    @property
    def changes(self):
        old = self.old
        full_set = self.full_set
        pad_nan = DiffCheck.PAD_NAN
        full_set.fillna(pad_nan, inplace=True)

        subset = list(old.columns)
        subset = [s for s in subset if s not in ["PANEL", "version"]]

        # Let's see what changes in the main columns we care about
        changes = full_set.drop_duplicates(subset=subset, keep="last")

        self._changes = changes
        return self._changes

    @property
    def diff_panel(self):
        changes = getattr(self, "_changes", self.changes)

        # We want to know where the duplicate ID numbers are,
        # that means there have been changes
        dup_ID = changes.set_index("ID").index[
            changes.set_index("ID").index.duplicated()
        ]
        # dup_ID = changes.set_index('ID').index.get_duplicates() #deprecated

        # Get all the duplicate rows
        dupes = changes[changes["ID"].isin(dup_ID)]

        if dupes.shape[0] > 300:
            v = self.changed_vars
            if "ID" not in v:
                v.append("ID")
            dupes = dupes[v]

        # Pull out the old and new data into separate dataframes
        change_update = dupes[(dupes["version"] == "update")]
        change_old = dupes[(dupes["version"] == "old")]

        # Drop the temp columns - we don't need them now
        change_update = change_update.drop(["version"], axis=1)
        change_old = change_old.drop(["version"], axis=1)

        # Index on the account numbers
        # inplace はNoneを返すため代入はNG
        change_update.set_index("ID", inplace=True)
        change_old.set_index("ID", inplace=True)
        # diff_panel = pd.DataFrame.from_dict(
        #    dict(変更前=change_old, 変更後=change_update))

        change_update.columns.name = "変数名"
        change_old.columns.name = "変数名"

        diff_panel = xr.Dataset(dict(変更前=change_old, 変更後=change_update))
        # diff_panel = pd.Panel(dict(変更前=change_old, 変更後=change_update))
        self._diff_panel = diff_panel
        return self._diff_panel

    @property
    def overwritten_ID(self):
        """
        変数の値を上書きしたID
        """
        diff_panel = getattr(self, "_diff_panel", self.diff_panel)
        # print("OID", diff_panel)
        diffs = diff_panel["変更前"] == diff_panel["変更後"]
        diffs_loc = diffs.where(diffs == False, drop=True)
        # print("ddd", diff_panel.where(diffs==False, drop=True))
        overwritten_ID = diff_panel.where(diffs == False, drop=True)
        # overwritten_ID = diff_panel.apply(self.report_diff, axis=0)
        self._overwritten_ID = overwritten_ID
        return self._overwritten_ID

    @property
    def removed_ID(self):
        """
        同一年のデータファイルについて
        昨年度のリリースデータに含まれ、今年度に含まれていないID。
        理論上、存在してはいけない。
        """
        changes = getattr(self, "_changes", self.changes)
        changes["duplicate"] = changes["ID"].isin(dup_ID)
        removed_ID = changes[
            (changes["duplicate"] == False) & (changes["version"] == "old")
        ]
        self._removed_ID = removed_ID
        return self._removed_ID

    @property
    def comeback_ID(self):
        """
        昨年度脱落、今年度で調査に復活したID。
        新規（今年度、昨年度実施調査）データにしか存在してはいけない。
        """
        full_set = getattr(self, "_full_set", self.full_set)
        update_ID_set = full_set.drop_duplicates(subset=subset, take_last=False)

        update_ID_set["duplicate"] = update_ID_set["ID"].isin(dup_ID)
        comeback_ID = update_ID_set[
            update_ID_set["duplicate"] == False & (update_ID_set["version"] == "update")
        ]
        self._comeback_ID = comeback_ID
        return self._comeback_ID

    def wrte_excel(self):
        writer = pd.ExcelWriter("mydiff.xlsx")
        overwritten_ID.to_excel(writer, "changed")
        removed_ID.to_excel(writer, "removed", index=False, columns=["ID"])
        comeback_ID.to_excel(writer, "comeback", index=False, columns=["ID", "PANEL"])
        writer.save()


if __name__ == "__main__":

    # diff = DiffAllFiles()
    # diff.keizoku_csv()
    f = Files_()
    print(f.changed_keizoku_shinki)

"""
http://stackoverflow.com/questions/10751127/returning-multiple-values-from-pandas-apply-on-a-dataframe
"""
