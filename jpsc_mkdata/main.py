"""
委員データ（住居情報を含む）の作成
"""

import src.keizoku as keizoku
import src.shinki as shinki
from src.csvdiff import Diffs
from settings import *  # main_user と共通の変数一式を読み込み

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
