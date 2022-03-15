"""
ユーザーデータの作成

地域情報（居住地ー都道府県・自治体コード、引越し履歴）を9999等で埋める
都道府県の情報を別ファイルに移して保存
"""
from pathlib import Path
import toml
import src.userdata as user
from src.dirstruct import DirStructure


# TODO
"""
ログファイルの生成

テストの作成
-データの整合性
-差分チェック

ユーザーデータの分離
-直近1年のデータを除外
-居住地情報の除外
--都道府県情報は別途、作成保存

"""

if __name__ == "__main__":

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
    usr = user.DataFactory(conf=d)
    usr.make()
