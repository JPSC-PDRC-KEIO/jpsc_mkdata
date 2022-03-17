"""
ユーザーデータの作成

地域情報（居住地ー都道府県・自治体コード、引越し履歴）を9999等で埋める
都道府県の情報を別ファイルに移して保存
"""

from settings import *
import src.userdata as user

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
    usr = user.DataFactory(conf=d)
    # usr.make()
    usr.make_merge()
