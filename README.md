# KIT Card Checker GUI

## 説明

### `record-csv.py`

金沢工業大学の学生証・職員証をNFCリーダーでスキャンし、IDとスキャン日時をCSVに保存するプログラムです。

デフォルトの保存場所はプログラムを実行したディレクトリ直下で、CSVファイル名は`scan-yyyyMMdd.csv`となります。

「ファイル保存場所を選択」のボタンを押すことにより、保存場所を変更できます。

CSVファイルの保存形式は`UTF-8 with BOM`です。

|      id      |         scan_datetime         |
| :----------: | :---------------------------: |
| xxxxxxx(int) | yyyy-MM-dd hh:mm:ss(datetime) |

### `ref-csv.py`

下記の形式のCSVファイルを読み込み、金沢工業大学の学生証・職員証のIDと名前、スキャン日時を表示するプログラムです。

1列目が`id`、2列目が`name`として設定されている必要があります。

|      id      |     name     |  ...  |
| :----------: | :----------: | :---: |
| xxxxxxx(int) | xxxxxxx(str) |  ...  |

実行時は、「CSVファイルを選択」のボタンを押すことにより、CSVファイルを選択できます。

スキャンを行うと、CSVの末尾にscanned列とscan_datetime列が追記されます。

保存形式は`UTF-8 with BOM`です。

|      id      |     name     |  ...  |    scanned    |         scan_datetime         |
| :----------: | :----------: | :---: | :-----------: | :---------------------------: |
| xxxxxxx(int) | xxxxxxx(str) |  ...  | true(boolean) | yyyy-MM-dd hh:mm:ss(datetime) |


## 環境構築

### Windows(exeファイル)で実行する場合

1. NFCリーダーのドライバーをダウンロード

「C:\Users\username\Downloads」に保存した場合の説明です。(usernameはお使いのPCのユーザー名に置き換えてください。)

[こちら](https://www.sony.co.jp/Products/felica/consumer/support/download/nfcportsoftware.html)からドライバーをダウンロードしてください。

2. タスクバーの検索ボックスに「cmd」と入力してコマンドプロンプトを起動してください。
3. コマンドプロンプトで「cd フォルダ名」と入力して作業フォルダを移動してください。(今回はユーザー名のダウンロードフォルダに保存したので「cd Downloads」と入力します)
4. `NFCPortWithDriver.exe /WinUSB`と入力してください。
5. インストール画面が表示されますので、画面の指示に従ってインストールしてください。
6. 検索ボックスまたは、すべてのアプリから「NFCポート自己診断(ドライバ切り換え)」を選択し、起動してください。
7. 「NFCポート自己診断(ドライバ切り換え)」を起動すると、デフォルトで「RC-S380」に設定されています。
「NFC Port」が選択されている場合は「WinUSB」のチェックボックスを選択し、「更新(U)」ボタンをクリックしてください。

## ソフトウェアの起動方法

### Pythonで実行する場合

#### uv を用いる場合

1. `uv sync` を実行してください。
2. `uv run record-csv.py`または、`uv run ref-csv.py`を実行してください。

#### uv以外を用いる場合

1. Python3.8以上をインストールしてください。
2. `pip install -r requirements.txt`を実行してください。
3. `python record-csv.py`または、`python ref-csv.py`を実行してください。

### Windows(exeファイル)を実行する場合

1. exeファイルをダウンロードしてください。
2. ダウンロードしたexeファイルを実行してください。
