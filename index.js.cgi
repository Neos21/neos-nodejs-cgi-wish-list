#!/usr/bin/node


/*!
 * Neo's Node.js CGI Wish List
 * 
 * Neo (@Neos21) https://neos21.net/
 */


const fs = require('fs');


// 定数
// ====================================================================================================

// Credential ファイルのフルパス
const CREDENTIAL_FILE_PATH = '/PATH/TO/credential.txt';

// データファイルのフルパス
const DATA_FILE_PATH = '/PATH/TO/wish-list.json';

// ページタイトル
const PAGE_TITLE = 'Wish List';

// リンク URL
const LINK_URL = 'https://neos21.net/';


// 事前処理
// ====================================================================================================

// ヘッダを出力しておく
console.log('Content-Type: text/html; charset=UTF-8\n\n');

// エラー時の処理
function onError(error) {
  console.log('<pre style="color: #f00; font-weight: bold;">Error :<br>', error, '</pre>');
}

// 例外発生時にエラー出力する
process.on('uncaughtException', error => onError(error));


// メイン処理
// ====================================================================================================

(async () => {
  try {
    if(process.env.REQUEST_METHOD === 'POST') {
      const requestBody = await getRequestBody();
      const credentialParam = requestBody.credential;
      if(!isValidCredential(credentialParam)) return writeInvalidPage();
      
      if(requestBody.mode === 'add'   ) return add   (credentialParam, requestBody);
      if(requestBody.mode === 'update') return update(credentialParam, requestBody);
      if(requestBody.mode === 'remove') return remove(credentialParam, requestBody);
      return redirectToListPage(credentialParam);
    }
    else {
      const queryParams = getQueryParams();
      const credentialParam = queryParams.credential;
      if(!isValidCredential(credentialParam)) return writeInvalidPage();
      return writeListPage(credentialParam);
    }
  }
  catch(error) {
    onError(error);
  };
})();


// 共通処理
// ====================================================================================================

// クエリ文字列を取得する
function getQueryParams() {
  return [...new URLSearchParams(process.env.QUERY_STRING)].reduce((acc, pair) => ({...acc, [pair[0]]: pair[1]}), {});
}

// POST 時にリクエストボディを取得する
async function getRequestBody() {
  let rawRequestBody = '';
  for await(const chunk of process.stdin) { rawRequestBody += chunk; }
  return [...new URLSearchParams(rawRequestBody)].reduce((acc, pair) => ({...acc, [pair[0]]: pair[1]}), {});
}

// HTML ヘッダを出力する
function writeHtmlHeader() {
  console.log(`
    <!DOCTYPE html>
    <html lang="ja">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="robots" content="noindex,nofollow">
        <title>${PAGE_TITLE}</title>
        <link rel="icon" href="/favicon.ico">
        <style>

@font-face { font-family: "Yu Gothic"; src: local("Yu Gothic Medium"), local("YuGothic-Medium"); }
@font-face { font-family: "Yu Gothic"; src: local("Yu Gothic Bold")  , local("YuGothic-Bold")  ; font-weight: bold; }
*, ::before, ::after { box-sizing: border-box; }

:root {
  --colour-border    : #080;
  --colour-text      : #0d0;
  --colour-background: #000;
}

html {
  overflow: hidden scroll;
  font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, YuGothic, "Yu Gothic", "Noto Sans JP", "Noto Sans CJK JP", "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Hiragino Kaku Gothic Pro", Meiryo, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
  text-decoration-skip-ink: none;
  -webkit-text-decoration-skip: objects;
  word-break: break-all;
  line-height: 1.5;
  background: var(--colour-background);
  cursor: default;
}

html, a { color: var(--colour-text); }
body { margin: .5rem; }

h1 { font-size: 1rem; }
h1 a       { text-decoration: none;      }
h1 a:hover { text-decoration: underline; }

input {
  height: 2rem;
  margin: 0;
  border: 0;
  border-radius: 0;
  padding: .25rem .5rem;
  color: inherit;
  font-size: 1rem;
  font-family: inherit;
  background: var(--colour-background);
  vertical-align: top;
  outline: none;
}

input::placeholder, [type="button"]:hover, [type="button"]:focus {
  color: var(--colour-border);
}

[type="button"] {
  cursor: pointer;
  -webkit-appearance: none;  /* For iOS Safari */
}

[type="date"] {
  min-width: 10rem;
  font-family: "Noto Sans Mono CJK JP", Osaka-mono, "MS Gothic", Menlo, Consolas, Courier, "Courier New", monospace, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
  text-align: center;
  -webkit-appearance: none;  /* For iOS Safari */
}

label {
  padding: 0 .5rem;
  text-align: center;
  background: var(--colour-background);
}

[type="checkbox"] {
          appearance: none;  /* For Chrome */
  -webkit-appearance: none;  /* For iOS Safari */
  position: relative;
  height: 1.1rem;
  border: 1px solid var(--colour-border);
  vertical-align: bottom;
}

[type="checkbox"]:checked::after {
  content: "";
  position: absolute;
  display: block;
  width: .7rem;
  height: .5rem;
  border: 2px solid var(--colour-text);
  border-top: 0;
  border-right: 0;
  transform: rotate(-45deg) translate(-20%, -60%);
}

form > div {
  display: grid;
  gap: 1px;
  margin-bottom: 1rem;
  padding: 1px;
  background: var(--colour-border);
}


/* Add */

#form-add-controls {
  grid-template-areas: "created btn-add"
                       "title   title"
                       "memo    memo";
}

@media (min-width: 600px) {
  #form-add-controls {
    grid-template-columns: 10rem 1fr 1fr 10rem;
    grid-template-areas: "created title memo btn-add";
  }
}

#form-add-controls > [name="created"] { grid-area: created; }
#form-add-controls > [name="title"]   { grid-area: title  ; }
#form-add-controls > [name="memo"]    { grid-area: memo   ; }
#form-add-controls > [name="btn-add"] { grid-area: btn-add; }


/* Update */

.form-update-controls {  /* For iOS Portrait */
  grid-template-areas: "is-completed created completed completed"
                       "title        title   title     btn-update"
                       "memo         memo    memo      btn-remove";
}

@media (min-width: 600px) {  /* For iOS Landscape */
  .form-update-controls {
    grid-template-areas: "is-completed created completed completed btn-update btn-remove"
                         "title        title   title     memo      memo       memo";
  }
}

@media (min-width: 980px) {  /* For PC */
  .form-update-controls {
    grid-template-columns: auto auto 1fr 1fr auto auto auto;
    grid-template-areas: "is-completed created title memo completed btn-update btn-remove";
    margin-bottom: -1px
  }
}

.form-update-controls > label               { grid-area: is-completed; }
.form-update-controls > [name="created"]    { grid-area: created;      }
.form-update-controls > [name="completed"]  { grid-area: completed;    }
.form-update-controls > [name="title"]      { grid-area: title;        }
.form-update-controls > [name="memo"]       { grid-area: memo;         }
.form-update-controls > [name="btn-update"] { grid-area: btn-update;   }
.form-update-controls > [name="btn-remove"] { grid-area: btn-remove;   }


/* Completed */

[type="checkbox"]:checked { border-color: #666; }
.completed > div          { background  : #666; }
.completed input          { color       : #999; }

      </style>
    </head>
    <body>
  `);
}

// HTML フッタを出力する
function writeHtmlFooter() {
  console.log(`
      </body>
    </html>
  `);
}

// ファイルの内容を取得する
function getData() {
  try {
    fs.statSync(DATA_FILE_PATH);
  }
  catch(_error) {
    fs.writeFileSync(DATA_FILE_PATH, '[]', 'utf-8');  // ファイルがなければ空配列のファイルを作っておく
  }
  const raw = fs.readFileSync(DATA_FILE_PATH, 'utf-8');
  const data = JSON.parse(raw);
  return data;
}

// ファイルに書き込む
function writeData(data) {
  fs.writeFileSync(DATA_FILE_PATH, JSON.stringify(data, null, '  '), 'utf-8');
}

// 一覧表示ページにリダイレクトする
function redirectToListPage(credentialParam) {
  writeHtmlHeader();
  console.log(`<script> location.href = location.href + '?credential=${credentialParam}'; </script>`);
  writeHtmlFooter();
}


// 認証
// ====================================================================================================

// Credential が一致するかどうか
function isValidCredential(credentialParam) {
  const credential = fs.readFileSync(CREDENTIAL_FILE_PATH, 'utf-8').trim();
  return credentialParam === credential;
}

// 認証エラー時のページ表示
function writeInvalidPage() {
  writeHtmlHeader();
  console.log(`
    <h1><a href="${LINK_URL}" rel="noreferrer noopener">${PAGE_TITLE}</a></h1>
    <p><strong>Invalid Credentials</strong></p>
  `);
  writeHtmlFooter();
}


// リスト表示
// ====================================================================================================

// 今日日付を取得する
function getToday() {
  const now = new Date();
  return `${now.getFullYear()}-${('0' + (now.getMonth() + 1)).slice(-2)}-${('0' + now.getDate()).slice(-2)}`;
}

// リスト表示
function writeListPage(credentialParam) {
  writeHtmlHeader();
  const data = getData();
  
  // 追加フォーム
  console.log(`
    <form action="${process.env.SCRIPT_NAME}" method="POST" id="form-add">
      <input type="hidden" name="credential" value="${credentialParam}">
      <input type="hidden" name="mode"       value="add">
      <div id="form-add-controls">
        <input type="date"   name="created"    value="${getToday()}" placeholder="Created">
        <input type="text"   name="title"      value=""              placeholder="Title">
        <input type="text"   name="memo"       value=""              placeholder="Memo">
        <input type="button" name="btn-add"    value="＋"            onclick="add()">
      </div>
    </form>
  `);
  
  if(!data || !data.length) {
    console.log('<p>Items Not Exist</p>');
  }
  else {
    // 一覧・更新フォーム
    const dataHtml = data.reduce((html, item, index) => {
      return html + `
        <form action="${process.env.SCRIPT_NAME}" method="POST" id="form-update-${index}" class="${item.completed ? 'completed' : ''}">
          <input type="hidden" name="credential" value="${credentialParam}">
          <input type="hidden" name="mode"       value="update">
          <input type="hidden" name="index"      value="${index}">
          <div class="form-update-controls">
            <label><input type="checkbox" name="is-completed" onclick="updateCompleted(this, '${index}')" ${item.completed ? 'checked' : ''}></label>
            <input type="date"     name="created"      value="${item.created}"   placeholder="Created">
            <input type="date"     name="completed"    value="${item.completed}" placeholder="Completed" onblur="updateIsCompleted(this, '${index}')">
            <input type="text"     name="title"        value="${item.title}"     placeholder="Title">
            <input type="text"     name="memo"         value="${item.memo}"      placeholder="Memo">
            <input type="button"   name="btn-update"   value="○"                 onclick="update('${index}')">
            <input type="button"   name="btn-remove"   value="×"                 onclick="remove('${index}')">
          </div>
        </form>
      `;
    }, '');
    console.log(dataHtml);
  }
  
  console.log(`
    <script>

// 追加フォーム
function add() {
  const form = document.getElementById('form-add');
  const created = form.querySelector('[name="created"]').value.trim();
  const title   = form.querySelector('[name="title"]').value.trim();
  if(!created) return alert('Created Is Empty');
  if(!title  ) return alert('Title Is Empty');
  form.submit();
}

// チェックボックス押下時
function updateCompleted(checkboxElem, index) {
  const form = document.getElementById('form-update-' + index);
  const completed = form.querySelector('[name="completed"]');
  if(checkboxElem.checked) {
    form.classList.add('completed');
    if(!completed.value) completed.value = '${getToday()}';
  }
  else {
    form.classList.remove('completed');
    completed.value = '';
  }
}

// 完了日変更時 (Blur)
function updateIsCompleted(completedElem, index) {
  const form = document.getElementById('form-update-' + index);
  form.querySelector('[name="is-completed"]').checked = !!completedElem.value;
  form.classList[form.querySelector('[name="is-completed"]').checked ? 'add' : 'remove']('completed');
}

// 更新
function update(index) {
  const form = document.getElementById('form-update-' + index);
  const created = form.querySelector('[name="created"]').value.trim();
  const title   = form.querySelector('[name="title"]').value.trim();
  if(!created) return alert('Created Is Empty');
  if(!title  ) return alert('Title Is Empty');
  form.querySelector('[name="mode"]').value = 'update';
  form.submit();
}

// 削除
function remove(index) {
  if(!confirm('Remove [' + index + '] ?')) return;
  const form = document.getElementById('form-update-' + index);
  form.querySelector('[name="mode"]').value = 'remove';
  form.submit();
}

    </script>
  `);
  
  writeHtmlFooter();
}


// ファイル更新処理
// ====================================================================================================

// 追加する
function add(credentialParam, requestBody) {
  const data = getData();
  data.unshift({
    created  : requestBody.created,
    title    : requestBody.title,
    memo     : requestBody.memo,
    completed: ''
  });
  writeData(data);
  redirectToListPage(credentialParam);
}

// 更新する
function update(credentialParam, requestBody) {
  const data = getData();
  data[requestBody.index] = {
    created  : requestBody.created,
    title    : requestBody.title,
    memo     : requestBody.memo,
    completed: requestBody.completed
  };
  writeData(data);
  redirectToListPage(credentialParam);
}

// 削除する
function remove(credentialParam, requestBody) {
  const data = getData();
  data.splice(requestBody.index, 1);
  writeData(data);
  redirectToListPage(credentialParam);
}
