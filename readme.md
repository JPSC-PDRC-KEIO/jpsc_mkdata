jpsc_mkdata
====
JPSCデータの作成プログラムパッケージ


## Description
- リリースデータの作成
	- 委員データ
		- 新規データを固定長データから作成
		- 継続データにエディティングの修正を加える
	- ユーザーデータ
		- 委員データをもとにデータを作成（基本は1年ラグ）
		- 地域情報を99999に変換
		- 都道府県コードのみを抽出し，別途保存
		- すべてのcsvファイルをマージしたデータ(csv, Apache Parquet)を作成
- データ整合性のチェック
- 新変数の作成（未実装）

## Requirement
- Python 3.10 or higher


- データ関連
	- データセット群[`jpsc_dataset`](#jpsc_datasetの構造)
		- 委員データ作成の場合は下記を追加：
			1. 新規データ（固定長txt）直近2年分
			2. エディティング修正リスト


## Usage
- データの準備
	- 委員・ユーザーデータ共通
		- データセット群[`jpsc_dataset`](#jpsc_datasetの構造)を用意
		- 上書き禁止．作成する該当リリースデータ（`p*release`）がすでに`jpsc_dataset`内にあれば削除するか名前を変更すること
	- 委員データ
		- 固定長データ
			- 中央調査社から納品された最新データを`jpsc_dataset/data/fixed_width_data/p*_release`の配下のフォルダーに配置
		- テープフォーマット
			- アドレス情報と変数名が入った対応するテープフォーマット（xlsx形式）を`data/fixed_width_data/tape_formats`に配置
			- ファイル名は `formatnp[調査回].xlsx` とする
		- 継続データについて
			- 特に必要無し。自動的に昨年度リリースデータをdata/old_data/p(*-1)_release 以下に作成(未実装)
		- 過去データの修正リスト
			- 過去の調査データについて、昨年リリースのデータセットから変更を加える場合は、`jpsc_dataset/editing/lists`配下のエクセルシートに修正内容を記載する
			- エクセルのファイル名は"panel*_editing.xslx" *は最新リリースデータとする
		- 作成しようとするリリース年のデータセットがすでに`jpsc_dataset`内にある場合は削除か名前を変更
	- ユーザーデータ
		- 特になし．参照元の委員データが`jpsc_dataset/data/update_data`にあることを確認

- データの作成
	- 委員・ユーザーデータ共通
		- ターミナルで　`/jpsc_mkdata/jpsc_mkdata` へ移動
		- コマンド `pipenv shell`, `pipenv install` を実行して仮想環境に入る
		- `./config.toml`の`dir.base`に，自身の環境での`jpsc_dataset`の絶対バスを記述
			- 実行環境がWindowsであればディレクトリの区切り記号を `\\` (二重バックスラッシュ)とする

	- 委員データ		
		- `./config.toml`の`data_info.latest_wave`にリリースする調査回を記述
		-  `main.py`を実行
		- `jpsc_dataset/data/update_data`以下に当該年度csvファイル一式が作成される(`p*_release`)
	- ユーザーデータ
		- `./config.toml`の`dir.base`の　`data_info.latest_wave_user`にリリースする調査回を記述
		- 同　`data_info.user_org_wave`に参照する委員データの調査回を記述
		-  `main_user_data.py`を実行
		- [`jpsc_dataset/data/user_data`](#userdataディレクトリ以下)以下に当該年度csvファイル一式が作成される(`p*_release`)
			- `original`： 参照委員データ（確認用．リリースしないこと）
			- `recoded`: 地域情報をつぶしたデータ（リリースするデータ）
			- `prefecture`: 都道府県データ（学部生にはリリースしない）
			- `merged`: `recoded`一式をマージしたデータ
				- `all*.csv`: csvフォーマット
				- `all*.parquet`: Apache Parquetフォーマット


- データ整合性のチェック
	- ユーザデータ
		- `jpsc_dataset/diffs`内の`p*_release_user`に委員データ，前年リリースデータとの差分が出力される
		- `original`: 元になる委員データとの差分．地域情報のマスキングが実行されているかとその他の変数に変更がないかのチェック
			- `P*_1_region.csv`: 地域情報が適切にマスキングがされていない場合に該当箇所を出力
			- `p*_*_others.csv`: 他の変数について異なる値が入っている場合に出力される
			- 両ファイルとも作成されていたら，何らかの不整合があることになる
		- `previous`: 前年データとの差分
			- 差分をjson形式で出力
			- `added`: 追加（主に復活サンプル），`removed`: 削除，　`changed`: 変更


	- nosetests の実行(過去分)
		- 継続データについて、今年度リリスデータと前年度との差分が、エディティング修正指示と一致
		しているかをチェック
		- 同一IDについて、年齢が1歳刻みで入っているかのチェック
		- 新規データのチェックは未実装
       - 年齢に不整合があった場合
                - longitudinal.py をrootディレクトリから実行
                - 不整合のIDは tests/inconsistents 下のCSVファイルに保存


## jpsc_datasetの構造
```
.
├── data
│   ├── fixed_width_data
│   ├── old_data
│   ├── tape_formats
│   ├── update_data
│   └── user_data
├── diffs
|	├─ p*_release
|	└─ p*_release_user
└── editing
    └── lists
```
### user_dataディレクトリ以下

各年`p*_release_user`があり，その配下に
```
.
├── merged
├── original
├── prefecture
└── recoded

```

## TODO
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
