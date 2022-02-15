"""
フルデータ（住居情報を含む）の作成
"""

import toml
from pathlib import Path
import src.keizoku as keizoku
import src.shinki as shinki
from src.dirstruct import DirStructure
from src.csvdiff import Diffs

# TODO
"""
29の時間について

ログファイルの生成

テストの作成
-データの整合性
-差分チェック

ユーザーデータの分離
-直近1年のデータを除外
-居住地情報の除外
--都道府県情報は別途、作成保存

新規データの初回納品と最終納品の差分
=>エディティングリストの自動作成
"""

if __name__ == "__main__":
    # 設定ファイル
    config = toml.load("./config.toml")
    base_dir = Path.home() / Path(config["dir"]["base"])
    data_base_dir = base_dir / Path(config["dir"]["data"]["base"])
    data_dir_toml = config["dir"]["data"]
    editing_dir = base_dir / Path(config["dir"]["editing"]["base"])
    diffs_dir = base_dir / Path(config["dir"]["diffs"])
    data_info = config["data_info"]

    d = DirStructure(
        latest_wave=data_info["latest_wave"],
        latest_wave_user=data_info["latest_wave_user"],
        fixed_width_data=data_base_dir / Path(data_dir_toml["fixed_data"]),
        updated_data=data_base_dir / Path(data_dir_toml["update_data"]),
        old_data=data_base_dir / Path(data_dir_toml["old_data"]),
        user_data=data_base_dir / Path(data_dir_toml["user_data"]),
        tape_formats=data_base_dir / Path(data_dir_toml["tape_formats"]),
        editing_dir=editing_dir,
        editing_file=str(Path(config["dir"]["editing"]["file"])),
        diffs_dir=diffs_dir,
        new_entries=data_info["new_entries"],
        num_sheets=data_info["num_sheets"],
    )

    print(d.fixed_width_data)
    # 継続データ（直近2年以上前のデータ）へのエディティング修正
    k = keizoku.DataFactory(conf=d)
    k.make()

    # 新規（直近2年データ）の固定長からCSVへの変換
    shinki.DataFactory(dir_struct=d).execute()

    # 新規CSVへの修正（生活時間、地域コード）
    shinki.CSVModified(dir_struct=d).execute()
    # m.__call__()

    df = Diffs(conf=d)
    df.check()

    """
    # 差分の取得
    # d = diffs.DiffAllFiles()
    # d.keizoku_csv()
    # d.shinki_csv()
    # d.all_csv()
    """
