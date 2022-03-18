from functools import reduce
from pathlib import Path
import pandas as pd

import pyarrow as pa
import pyarrow.parquet as pq


def merge(data_dir: Path, save_dir: Path, wave: int) -> None:
    pnl_dataset = pd.DataFrame()

    for pnl in data_dir.iterdir():
        sheets = []
        pnl_dir = data_dir / pnl

        for sheet in pnl_dir.glob("*.csv"):
            sdata = pd.read_csv(sheet)
            sheets.append(sdata)
        each_data = reduce(
            lambda left, right: pd.merge(
                left, right.drop(columns=["REC", "PANEL"]), how="inner", on="ID"
            ),
            sheets,
        )

        pnl_dataset = pd.concat([pnl_dataset, each_data], ignore_index=True)

    pnl_dataset.sort_values(by=["PANEL", "ID"])
    csv_file_name = f"all_{wave}.csv"
    pq_file_name = f"all_{wave}.parquet"

    pnl_dataset.to_csv(save_dir / Path(csv_file_name), index=False)

    table = pa.Table.from_pandas(pnl_dataset)
    pq.write_table(table, save_dir / Path(pq_file_name))
