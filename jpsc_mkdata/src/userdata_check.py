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

    def previous_check(self) -> None:
        """
        前年ユーザーデータとの差分．変更があったファイルをjson形式で書き出し．
        """
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
            else:
                current_path

    def original_check(self) -> None:
        """
        元になる委員データとの差分をとる．
        1). 地域変数が適切につぶされているか, 2).それ以外の変数に変更が加わっていないかのチェック.
        不具合があった場合，1）.はp*_resion.csv, 2). はp*_others.csvに書き込む．
        """
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
            recoded_data: pd.DataFrame = pd.read_csv(recoded_path, index_col="ID")
            org_data: pd.DataFrame = pd.read_csv(org_path, index_col="ID")
            diff_df: pd.DataFrame = org_data.compare(recoded_data)
            diff_columns: pd.Index = diff_df.columns.droplevel(1).unique()
            if any(diff_columns):  # 委員データとユーザーデータで差がある場合
                region_vars = ["Q4", "P33C", "P34C", "P35C", "P36C", "P37C"]
                if any(diff_columns.isin(region_vars)):  # 地域変数のチェック
                    resion_padded: pd.DataFrame = diff_df[
                        diff_df.isin(region_vars)
                    ].iloc[:, diff_df.columns.get_level_values(1) == "other"]
                    if (
                        ~(resion_padded % 9 == 0).all().all()
                    ):  # 地域変数に99999以外の埋め草が入っている場合
                        diff_region_file = recoded_path.stem + "_resion.csv"
                        diff_df[~(resion_padded % 9 == 0).all(axis=1)].to_csv(
                            odir / Path(diff_region_file)
                        )  # 99999以外が含まれる行のみ書き出し
                if not all(diff_columns.isin(region_vars)):  # 地域情報以外の変数に変更があった場合
                    others = set(diff_columns) - set(region_vars)
                    diff_other_file = recoded_path.stem + "_other.csv"
                    diff_df[others].to_csv(odir / Path(diff_other_file))

    def check(self):
        self.mk_release_diff_dir()
        self.previous_check()
        self.original_check()
