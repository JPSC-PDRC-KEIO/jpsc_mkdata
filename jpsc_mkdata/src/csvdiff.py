import os
import itertools
import json

from csv_diff import load_csv, compare


class Diffs:
    def __init__(self, conf):
        self.conf = conf

    def check(self):
        print("check diff")
        release_dir = os.path.join(
            self.conf.updated_data, self.conf.release_dir)
        prev_release_dir = os.path.join(
            self.conf.old_data, self.conf.release_dir_lag)
        diff_dir = os.path.join(
            self.conf.diffs_dir, self.conf.release_dir)
        os.makedirs(diff_dir, exist_ok=True)
        for pnl_dir in os.listdir(prev_release_dir):

            trgt_dir = os.path.join(prev_release_dir, pnl_dir)
            for f in os.listdir(trgt_dir):
                old_file = os.path.join(prev_release_dir, pnl_dir, f)
                new_file = os.path.join(release_dir, pnl_dir, f)

                if os.path.isfile(old_file):
                    diff = compare(
                        load_csv(open(old_file), key="ID"),
                        load_csv(open(new_file), key="ID"),
                    )

                    v = itertools.chain(*diff.values())
                    if len(list(v)) != 0:
                        f_ = os.path.splitext(f)[0] + ".json"
                        f_name = os.path.join(diff_dir, f_)
                        with open(f_name, "w") as j:
                            json.dump(diff, j)

                else:
                    pass
