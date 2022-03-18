"""
ユーザーデータチェック用
1. 委員データとの差分
2. 前年リリースデータとの差分_
"""
import json
import shutil
import pandas as pd
from pathlib import Path
from src.dirstruct import DirStructure  # noqa
from csv_diff import load_csv, compare

# csv-diff https://pypi.org/project/csv-diff/


class DataCheck:
    """_summary_
    ユーザーデータ格納ディレクトリの設定 user_data/p_*release_user 以下にoriginal, recoded, pref の3種をつくる
    """

    def __init__(self, conf: DirStructure) -> None:
        """_summary_

        :param conf: ディレクトリ設定情報
        :type conf: DirStructure
        """
        self.conf: DirStructure = conf

    @property
    def current_dir(self) -> Path:
        """
        リリースするユーザーデータのパス
        :return: ユーザーデータの絶対パス e.g. jpsc_dataset/data/user_data/p29_release_user
        :rtype: Path
        """
        return self.conf.release_user_dir_abs

    @property
    def previous_dir(self) -> Path:
        """
        昨年リリースしたユーザーデータのパス
        :return: （昨年）ユーザーデータのパス e.g. jpsc_dataset/data/user_data/p29_release_user
        :rtype: Path
        """
        return self.conf.release_user_dir_lag_abs

    @property
    def diff_dir_parent(self) -> Path:
        """
        チェックした差分の格納する親ディレクトリ
        :return: jpsc_dataset/diffs
        :rtype: Path
        """
        return self.conf.diffs_dir

    @property
    def release_diff_dir(self) -> Path:
        """
        チェックした差分の格納ディレクトリ
        :return: jpsc_dataset/diffs/p*_release_user
        :rtype: Path
        """
        return self.diff_dir_parent / Path(self.current_dir.name)

    def mk_release_diff_dir(self) -> None:
        """
        差分格納ディレクトリの作成
        """
        self.release_diff_dir.mkdir(exist_ok=True)

    def previous_check(self):
        pdir = self.release_diff_dir / Path("previous")
        if pdir.exists():
            shutil.rmtree(pdir)
        pdir.mkdir()
        target_dirs = self.current_dir / Path("recoded")
        for current_path in target_dirs.glob("**/*.csv"):
            prev_path = (
                self.previous_dir
                / Path("recoded")
                / Path(current_path.parent.name)
                / Path(current_path.name)
            )
            if prev_path.exists():
                diff = compare(
                    load_csv(open(prev_path), key="ID"),
                    load_csv(open(current_path), key="ID"),
                )
                if any(diff.values()):
                    diff_file_name = current_path.stem + ".json"
                    with open(
                        self.release_diff_dir / Path("previous") / Path(diff_file_name),
                        mode="w",
                    ) as f:
                        json.dump(diff, f)

    def original_check(self):
        odir = self.release_diff_dir / Path("original")
        if odir.exists():
            shutil.rmtree(odir)
        odir.mkdir()
        target_dirs = self.current_dir / Path("recoded")
        for recoded_path in target_dirs.glob("**/*.csv"):
            org_path = (
                self.current_dir
                / Path("original")
                / Path(recoded_path.parent.name)
                / Path(recoded_path.name)
            )
            recoded_data = pd.read_csv(recoded_path)
            org_data = pd.read_csv(org_path)
            diff = org_data.compare(recoded_data)
            diff_columns = diff.columns.droplevel(1).unique()
            print(diff_columns)
            if any(diff_columns):
                diff_file_name = recoded_path.stem + ".txt"
                with open(odir / Path(diff_file_name), "w") as f:
                    f.write(str(diff_columns))

    def check(self):
        self.mk_release_diff_dir()
        self.previous_check()
        self.original_check()

    @property
    def org_dir(self):
        # 元データ格納dir
        return self.conf.release_user_dir_abs / Path("original")

    @property
    def recoded_dir(self):
        # 地域情報をつぶしたデータ格納dir
        return self.conf.release_user_dir_abs / Path("recoded")

    @property
    def pref_dir(self):
        # 都道府県データ格納dir
        return self.conf.release_user_dir_abs / Path("prefecture")
