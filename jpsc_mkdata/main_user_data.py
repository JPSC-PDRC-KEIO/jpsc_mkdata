"""
ユーザーデータの作成

地域情報（居住地ー都道府県・自治体コード、引越し履歴）を9999等で埋める
都道府県の情報を別ファイルに移して保存
"""

from settings import *  # main と共通の変数一式を読み込み
import src.userdata as user
import src.userdata_check as user_check


if __name__ == "__main__":
    # usr = user.DataFactory(conf=d)
    # usr.make() # ファイルのマージなし
    # usr.make_merge()
    user_check.DataCheck(conf=d).check()
