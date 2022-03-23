"""
ユーザーリリース用データの作成
"""
import csv
import shutil
import sys
import pandas as pd
from pathlib import Path
from src.dirstruct import DirStructure  # noqa
from src.merge import merge as pmerge  # noqa


class DataFactory:
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

    def mkdir(self):
        try:
            self.conf.release_user_dir_abs.mkdir(parents=True)
        except FileExistsError as e:
            print(f"{self.conf.release_user_dir_abs}を取り除いてください")
            print(e)
            sys.exit(1)

        user_org_wave = "p" + str(self.conf.user_org_wave) + "_release"
        shutil.copytree(
            self.conf.updated_data / Path(user_org_wave), self.org_dir
        )  # releaseオリジナルデータ（委員データ）をコピーしてoriginal に名前を変更
        shutil.copytree(self.org_dir, self.recoded_dir)  # originalからrecodedにファイル群をコピー

        self.pref_dir.mkdir()  # 都道府県データdir 作成

    def recode(self) -> None:
        """
        p*_1.csvの地域情報を99999（9）に置き換え
        """
        odir: Path = self.org_dir
        rdir: Path = self.recoded_dir
        pdir: Path = self.pref_dir

        for fname_abs in odir.glob("**/*_1.csv"):
            data = pd.read_csv(fname_abs)  # (os.path.join(root, fname))

            """
            p1, p5b, p11c, p16d, p21e は引っ越し情報（P33）もつぶす
            """
            if fname_abs.name in [
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
                        lambda x: "{0:.0f}".format(x)[:-3] if pd.notnull(x) else x
                    )
                data["Q4"] = data["Q4"].map(lambda x: "{0:.0f}".format(x)[:-3])

            else:
                data_pref = pd.DataFrame(data, columns=["ID", "PANEL", "Q4"])
                data_pref["Q4"] = data_pref["Q4"].map(
                    lambda x: "{0:.0f}".format(x)[:-3]
                )
                data_pref.rename(columns={"Q4": "KEN"}, inplace=True)

            # Q2, Q4の置き換え
            # data["Q2"] = 9
            data["Q4"] = 99999

            # ユーザーリリース用データ（地域情報を含まない）の保存

            fname = fname_abs.name
            wave = fname_abs.parent.name
            recoded_file_path = rdir / wave / fname
            data.to_csv(
                recoded_file_path,
                index=False,
                quoting=csv.QUOTE_NONE,
                float_format="%.0f",
            )

            # 都道府県データの保存＝>"prefecture"ディレクトリに作成
            # fname = os.path.splitext(fname)
            # fname_pref = fname[0][:-2] + "pref" + fname[1]
            fname_pref = Path(wave + "pref.csv")
            data_pref.to_csv(
                pdir / fname_pref,
                index=False,
                quoting=csv.QUOTE_NONE,
                float_format="%.0f",
            )

    def merge(self) -> None:
        mdir = self.conf.release_user_dir_abs / Path("merged")
        mdir.mkdir()
        pmerge(
            data_dir=self.recoded_dir,
            save_dir=mdir,
            wave=self.conf.latest_wave_user,
        )

    def make(self) -> None:
        """
        self.mkdir と　self.recodeの実行
        """
        self.mkdir()
        self.recode()

    def make_merge(self) -> None:
        """
        make(地域情報つぶし) と　merge（データの結合）の2つを実行 
        """
        self.make()
        self.merge()
