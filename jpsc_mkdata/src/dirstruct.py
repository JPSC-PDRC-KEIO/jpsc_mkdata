from pathlib import Path
from dataclasses import dataclass
from typing import Dict


@dataclass
class DirStructure:
    """
    格納データのディレクトリ情報を格納したクラス．各種設定は``config.toml``に記述

    * リリースデータ 地域情報等を間引いていないデータ　最新版
    * ユーザーデータ 地域情報等を間引いたデータ　最新版よりラグあり
    """

    latest_wave: int  # データの最新年　（e.g. 29）
    latest_wave_user: int  # ユーザーデータの最新年
    fixed_width_data: Path  # 固定長データ（元データ）の格納ディレクトリ
    updated_data: Path  # 新規作成のフルデータ（リリースデータ, csv）の格納ディレクトリ
    old_data: str  # 昨年のリリースデータを格納ディレクトリ
    user_data: str  # ユーザーデータの格納ディレクトリ
    tape_formats: Path  # テープフォーマット（固定長データにおける変数名と位置情報）格納ディレクトリ
    editing_dir: str  # データ修正（エディティング）のリストの格納ディレクトリ
    editing_file: str  # データ修正リストのファイル名
    diffs_dir: str  # 作成データと前年リリースデータとの差分を格納するディレクトリ
    # 新規サンプルのディレクトリ名 ["p1", "p5b", "p11c", "p16d", "p21e"]
    new_entries: list[str]
    num_sheets: int  # テープフォーマット　Excelブックのシート数　5枚

    def __post_init__(self):
        """
        リリースデータのディレクトリを作成調査回（latest_wave, latest_wave_user）の情報から作成
        JPSCデータ特有のディレクトリ，ファイル名（e.g. p21_releaseの接頭辞pと'_release'を付加）
        ベースとなるディレクトリ名から自動生成
        """
        self.release_dir: Path = Path(
            "p" + str(self.latest_wave) + "_release"
        )  # e.g. p22_release
        self.release_user_dir: Path = Path(
            "p" + str(self.latest_wave_user) + "_release_user"
        )
        self.release_dir_lag: Path = Path("p" + str(self.latest_wave - 1) + "_release")
        # e.g. p21_release if p22

    @property
    def panel_directories(self) -> Dict[int, list[Path]]:
        """
        調査年(wave)と対応するデータを格納したディレクトリ名のリストを表すディクショナリを返す
        原則は第n回調査に対してpnとなる．
        新規追加の年（5, 11, 16, 21）は継続対象者のデータと新規追加対象者のデータが異なるため2つディレクトリが存在する．
        新規・既存データのディレクトリ走査，作成に必要
        :return: 調査年とデータディレクトリのPath（リスト）の辞書
        :rtype: dict[int, list[Path]]
        """
        pdirs: Dict[int, list[Path]] = {
            i: [Path(f"p{i}")] for i in range(1, self.latest_wave + 1)
        }
        pdirs[5] = [Path("p5a"), Path("p5b")]
        pdirs[11] = [Path("p11ab"), Path("p11c")]
        pdirs[16] = [Path("p16abc"), Path("p16d")]
        pdirs[21] = [Path("p21abcd"), Path("p21e")]
        return pdirs

    @property
    def shinki_data_dirs(self) -> list[Path]:
        """
        中央調査社からは調査最新年とエディティングの修正を施した前年の，2年分データが納品される．その2か年のディレクトリ名を表す．
        ``panel_dorectories``属性から原則，直近2か年の情報を引き抜いたもの．
        :return: 調査回のデータディレクトリ名が入ったリスト
        :rtype: list[Path]
        """
        p: list[Path] = self.panel_directories[self.latest_wave]
        plag: list[Path] = self.panel_directories[self.latest_wave - 1]
        pnls: list[Path]
        if self.latest_wave == 27:
            # 27回調査は中央調査社のミスにより3年分のデータが納品されたためイレギュラーな処理 27, 26, 25
            plaglag: list[Path] = self.panel_directories[self.latest_wave - 2]
            pnls = p + plag + plaglag
        else:
            pnls = p + plag

        return pnls

    @property
    def updated_panel_dirs(self) -> list[Path]:
        """
        作成したデータを保存するディレクトリ群について
        各調査回(panel,wave)のデータを格納したディレクトリ名（path）まで
        リストで返す．
        * e.g. p22の作成データだと，["data/update_data/p22_release/p21abcd",
             "data/update_data/p22_release/p21e",
             "data/update_data/p22_release/p22"]
        :return: 新規データ格納ディレクトリ群のPathが入ったリスト
        :rtype: list[Path]
        """

        prnt_dir: Path = self.updated_data / self.release_dir
        updated_dir: list[Path] = [prnt_dir / d for d in self.shinki_data_dirs]

        return updated_dir
