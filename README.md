# Neo's Node.js CGI Wish List

Node.js 製の CGI として動作する、オレオレ・ウィッシュリスト・アプリ。


## 機能

- パスワード認証により、管理者だけが管理・閲覧できる、オリジナルのウィッシュリスト
- 次の項目を入力・更新できる
    - 作成日 (`YYYY-MM-DD`)
    - タイトル
    - メモ
    - 完了日 (`YYYY-MM-DD`・入力すると「完了状態」として表示する)
- ウィッシュリストの内容は JSON ファイルに保存する


## 設定

`index.js.cgi` の1行目にある Shebang (`node` へのフルパス)、および `定数` 部分を自環境に合わせて変更する。

- `CREDENTIAL_FILE_PATH`
    - アクセスパスワードを書いた「クレデンシャルファイル」のフルパスを記す
    - クレデンシャルファイルは、任意のアクセスパスワードを記した1行のテキストファイルとする
- `DATA_FILE_PATH`
    - ウィッシュリストの内容を保存する JSON ファイルのフルパスを記す
    - 当該パスにファイルが存在しない場合はその場でファイル作成を試みる
- `PAGE_TITLE`
    - `title` 要素、および `h1` 要素で示されるページタイトル
- `LINK_URL`
    - ページタイトルに指定されるリンク URL


## 管理者閲覧の方法

URL に `credential` パラメータを指定してアクセスするとアプリが表示できる。

- ex. `http://example.com/index.js.cgi?credential=MY_CREDENTIAL`

`credential` パラメータで指定したパスワードの整合性は、「クレデンシャルファイル」と突合して確認する。

管理者用画面では、ウィッシュリストの登録・更新・削除が行える。


## Links

- [Neo's World](https://neos21.net/)
