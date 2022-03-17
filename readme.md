JPSC Data Set
====
JPSCデータの作成プログラムパッケージ


## Description
- リリースデータの作成
	- 委員データ
		- 新規データを固定長データから作成
		- 継続データにエディティングの修正を加える
	- ユーザーデータ
		- 委員データをもとにデータを作成（基本は1年ラグ）
		- 地域情報を999999に変換
		- 都道府県コードのみを抽出し，別途保存
		- すべてのcsvファイルをマージしたデータ(csv, Apache Parquet)を作成
- データ整合性のチェック
- 新変数の作成（未実装）

## Requirement
- Python 3.10 or higher


- データ関連
	- 新規データ（固定長txt）直近2年分
	- エディティング修正リスト
	 
## Usage
- データの準備
	- 委員データ
		- 固定長データ
			- 中央調査社から納品された最新データを`jpsc_dataset/data/fixed_width_data/p*_release`の配下のフォルダーに配置
		- テープフォーマット
			- アドレス情報と変数名が入った対応するテープフォーマット（xlsx形式）を`data/fixed_width_data/tape_formats`に配置
			- ファイル名は `formatnp[調査回].xlsx` とする
		- 継続データについて
			- 特に必要無し。自動的に昨年度リリースデータをdata/old_data/p(*-1)_release 以下に作成(未実装)
		- 作成しようとするリリース年のデータセットがすでに`jpsc_dataset`内にある場合は削除か名前を変更
	- ユーザーデータ
		- 特になし．参照元の委員データが`jpsc_dataset/data/update_data`にあることを確認

- データの作成
	- 委員データ
		-`./config.toml`の`dir.base`を自身の環境で`jpsc_dataset`を置いている位置に合わせる
		- 同　`data_info.latest_wave`にリリースする調査回を記述
		-  `main.py`を実行
		- `data/update_data`以下に当該年度csvファイル一式が作成される(`p*_release`)
	- ユーザーデータ
		-`./config.toml`の`dir.base`を自身の環境で`jpsc_dataset`を置いている位置に合わせる
		- 同　`data_info.latest_wave_user`にリリースする調査回を記述
		- 同　`data_info.user_org_wave`に参照する委員データの調査回を記述
		-  `main_user_data.py`を実行
		- `data/user_data`以下に当該年度csvファイル一式が作成される(`p*_release`)
			- `original`： 参照委員データ（確認用．リリースしないこと）
			- `recoded`: 地域情報をつぶしたデータ（リリースするデータ）
			- `pref`: 都道府県データ（学部生にはリリースしない）
			- `all*.csv`, `all*.parquet`: 　`recoded`一式をマージしたデータ
- データ整合性のチェック
	- nosetests の実行
		- 継続データについて、今年度リリスデータと前年度との差分が、エディティング修正指示と一致
		しているかをチェック
		- 同一IDについて、年齢が1歳刻みで入っているかのチェック
		- 新規データのチェックは未実装
       - 年齢に不整合があった場合
                - longitudinal.py をrootディレクトリから実行
                - 不整合のIDは tests/inconsistents 下のCSVファイルに保存



##TODO
- [ ] ログファイル作成の自動化


- [ ] データ作成
    - [] リリースデータセットの作成（）

    - [] ユーザーデータの作成
        - [] 直近1年データの除外
        - [] 居住地情報（含む引っ越し履歴）の削除、都道府県データの別途保存
    
- [ ] テスト関連
    - [] 新規データのチェック
        - [] 初回納品と最終納品の差分
        - []　変数の内容（特に合成変数）の妥当性

- [ ] 新変数の作成
	
- [x] DONE


## Contribution


## Author
