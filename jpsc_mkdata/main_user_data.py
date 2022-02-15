"""
ユーザーデータの作成

地域情報（居住地ー都道府県・自治体コード、引越し履歴）を9999等で埋める
都道府県の情報を別ファイルに移して保存
"""
import os
import datetime
import glob

import toml

import jpsc_mkdata.src.dirstruct as dirstruct  # 設定ファイル（調査年、ディレクトリ構成）
import src.userdata as user
from jpsc_mkdata.src.dirstruct import DirStructure


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
    settings = toml.load("./config.toml")
    base_dir = settings["dir"]["base"]
    data_dir = settings["dir"]["data_dir"]
    data_base_path = os.path.join(base_dir, data_dir["base"])
    editing = settings["dir"]["editing"]
    diffs_dir = os.path.join(base_dir, settings["dir"]["diffs"])

    data_info = settings["data_info"]

    d = DirStructure(
        latest_wave=data_info["latest_wave"],
        latest_wave_user=data_info["latest_wave_user"],
        fixed_width_data=os.path.join(data_base_path, data_dir["fixed_data"]),
        updated_data=os.path.join(data_base_path, data_dir["update_data"]),
        old_data=os.path.join(data_base_path, data_dir["old_data"]),
        user_data=os.path.join(data_base_path, data_dir["user_data"]),
        tape_formats=os.path.join(data_base_path, data_dir["tape_formats"]),
        editing_dir=os.path.join(base_dir, editing["base"]),
        editing_file=editing["file"],
        diffs_dir=diffs_dir,
        new_entries=data_info["new_entries"],
        num_sheets=data_info["num_sheets"],
    )

    usr = user.DataFactory(conf=d)
    usr.make()
