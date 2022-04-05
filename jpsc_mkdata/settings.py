from pathlib import Path
import toml
from src.dirstruct import DirStructure

config = toml.load("./config.toml")
base_dir = Path(config["dir"]["base"])
data_base_dir = base_dir / Path(config["dir"]["data"]["base"])
data_dir_toml = config["dir"]["data"]
editing_dir = base_dir / Path(config["dir"]["editing"]["base"])
diffs_dir = base_dir / Path(config["dir"]["diffs"]["base"])
data_info = config["data_info"]

d = DirStructure(
    latest_wave=data_info["latest_wave"],
    latest_wave_user=data_info["latest_wave_user"],
    user_org_wave=data_info["user_org_wave"],
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
