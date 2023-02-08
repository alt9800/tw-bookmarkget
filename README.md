# tw-bookmarkget
Sample for retrieving your own saved bookmarks using Twitter's v2API.

note; I will make an English version if asked.

----

# 概要

Twitterのv2プラグインにおけるBookmarkの取得について、

OAuth 2.0トークンによる断続的なリクエストにより、全件(これは実際には限度があるが実質全件)のブックマークの取得をするようなコードを作成しました。

Developers Portal Bookmarks

https://developer.twitter.com/en/docs/twitter-api/tweets/bookmarks/introduction

Ruby,Javascript,Python向けに公式が掲載してくれている[サンプル](https://github.com/twitterdev/Twitter-API-v2-sample-code/tree/main/Bookmarks-lookup)がしっかりしているので、特に最新の100件に関する取得難易度は低いです。

(Rubyは308が返ってきて取得ができなくなっているのでPull Requestを建てる必要があります。)

これを書いている(2023-02-09)にはAPIはCloseされるとの情報もあるのでこれを見ている人が土壇場で間に合うかは謎ですが覚書として残しておきます。

https://twitter.com/TwitterDev/status/1621026986784337922?s=20&t=4xCaAtpWDrBP51IC-vBrig

----

# 環境作成

## step0 デベロッパーサイトより登録しBearerトークンを取得

TwitterのDevelopers Portalにアクセスし、APIエンドポイントを作成します。 
https://developer.twitter.com/en/portal/dashboard  

デベロッパー登録がまだの方は作文の工程などがあるので少し手間かも。


TwitterJPにリツイートされていた記事など、2022年3月末にリリースされたv2APIの始め方も日本語で数多く情報が見つかります。
https://twitter.com/TwitterDevJP/status/1585172198297604097?s=20&t=4xCaAtpWDrBP51IC-vBrig

https://qiita.com/stephinami/items/f341d55dd9fe6668e709


この手の工程に慣れている方は公式のQuick StartガイドからPostmanを用いてすぐに試すこともできるかもしれません。

https://developer.twitter.com/en/docs/twitter-api/tweets/bookmarks/quick-start/manage-bookmarks

----

### 迷ったときに見る項目

登録が済んだら、

Project & Apps > Overview > Add Apps でアプリケーション(用のエンドポイント)を設定する。


|項目|処理|
|---|---|
|App permissions|取得(GET)しか行わないので`Read`でOK|
|Type of App|Public clientとして実装するので`Native App`でOK|
|Callback URI / Redirect URL |`https://github.com/` などを指定しておくと認証時にこちらに遷移するようになる|
|Website URL|こちらも上記同様仮置で可|

----

## step1 環境変数をコマンドラインで設定

コードをPythonで実行する前に、各種ライブラリやトークンをコマンドラインより設定してあげる必要があります。

公式サンプルを動かすために必要なのは`BEARER_TOKEN`および`CLIENT_ID`で、改良したコードもそれに準じます。

``` bash
# python3.10 -m pip install --upgrade pip3
pip3 install requests_oauthlib
pip3 install requests
export BEARER_TOKEN='{My Token}'
export CLIENT_ID='{My ID}'
```

私のIntel Mac環境だと `requests_oauthlib` および `requests` をインストールするためにpip3のアップグレードを促されました。(Python 3.10.9を使っています。怒られたらpip3をpipに変えるといいでしょう)

----

## step2 コードを自分の環境に合わせる

公式サンプルの、
```python
redirect_uri = "https://www.example.com"
```

を上記のコールバック用のURIに設定して保存するだけで動きます。

結果をJsonで保存したかったので、`Respose`の`print`前後でファイル書き込みをしました。

```python
with open("data.json", "w") as f:
    # JSON 形式の文字列を書き込む
    json.dump(json_response, f , indent=4, sort_keys=True)
```

気をつけることとしては、

レスポンスに含まれる`text`は例えば日本語や絵文字といった複数バイト文字が
Unicode文字列として表現されるのでデコードをしてあげる必要があります。

上のコードではDict型のjson_responseに含まれるUnicode文字列を変換されずにjsonに保存されるため、
別途繰り返し処理を用いてデコードしたほうがいいです。


```
例えば
\ud83d\udc7b
は
👻
です
```

「Unicode デコード」などで検索すると便利なWebサービスが見つかると思うのでそちらで対処しても可。

json文字列の中にあるUnicodeをデコードしてくれる便利ツールもあります。


JSON To CSV Converter 

https://www.convertcsv.com/json-to-csv.htm  



ただし、これも一つ問題があって、`with`と`open`でで繰り返し処理を用いて一つのjsonに書き込む場合はきれいなjsonの形式を満たせなかったりするので、一工夫入ります。(手作業で修正するのもそんなに手間じゃないけど)

----

## step3 スクリプトを走らせる

Twitter v2プラグインにおけるOauth2認証の流れとしては

```planetext

アプリ(Pythonスクリプト)を起動

↓

ブラウザが開かれTwitterの認証画面に遷移 (WindowsやOpenコマンドが入っていないLinux環境がどうなんだろう😳)

↓

認証

↓

CallbackURIに遷移

↓

アドレスバーより `https://github.com?state={文字列1}&code={文字列2}`という文字列が得られるのでこれを`Visit the following URL to authorize your App on behalf of your Twitter handle in a browser:`に続いてコマンドラインに貼り付ける。

↓

リクエストとレスポンスが得られてコマンドライン上にコマンドライン上にjsonが表示される

```

という感じです。

この方法はあまり行儀が良くない方法であり、安定した利用のために、

せめてコールバックとしてlocalhost:3000などを指定しておき、それを`open`コマンドなどブラウザを開く処理をpythonから実行し、

遷移後のURLをパラメータごと変数として処理してレスポンスを取得する、というやり方がベターかもしれません。

----

## step4 繰り返し処理を用いてブックマークを回収できるようにする。

上記を踏まえて、コードを変更してみると`main.py`のようになります。

Step2~3と同様にコマンドラインとブラウザを駆使してレスポンスを取得します。

やっていることとしては、
1回目のレスポンスが

```json
{
    "data": [
      {
        "edit_history_tweet_ids": [
          "1623160692470874113"
        ],
        "id": "1623160692470874113",
        "text": "Time for me to learn about React and R3F 🤓\nhttps://t.co/Q3UndtHeWv https://t.co/nLmLJV5V18"
      },
      {
        "edit_history_tweet_ids": [
          "1622933201202339840"
        ],
        "id": "1622933201202339840",
        "text": "参考にした動画です。\n色んなエフェクトとかデザインがあるからめちゃくちゃ参考になる。\nhttps://t.co/WmnE0SaHLp"
      },
      ........
    ]
    "meta": {
      "next_token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
      "result_count": 100
    }
}
```

という形式で返ってきていたので、

```python
while "next_token" in json_response.get("meta", {}):
  #{処理}

```

という感じでnext_tokenが含まれる限りループで処理するという感じにしました。

ここが肝なのですが、
`next_token`は実際にはbookmarksのエンドポイントに対しては他のv2APIと同様に`pagenation_token`パラメータを与えるとリクエストが得られます。

```python
    url = "https://api.twitter.com/2/users/{}/bookmarks".format(user_id) + "?pagination_token=" + json_response["meta"]["next_token"] 

```

これは試しに`?next_token="文字列"`を与えてリクエストしてみたときにUsageが返って来たことで気づきました。

```bash
Exception: Request returned an error: 400 {"errors":[{"parameters":{"next_token":["zldjwdz3w6sba13nbs1171oq2s8nk5xdjurwaejrn76"]},"message":"The query parameter [next_token] is not one of [id,max_results,pagination_token,expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields]"}],"title":"Invalid Request","detail":"One or more parameters to your request was invalid.","type":"https://api.twitter.com/2/problems/invalid-request"}

```

まだまだこのエンドポイントに対しては指定できるパラメータがあるみたいですね。



一回目のループから引き継がれている変数の都合上、まだコードを削れるところはあると思いますがご容赦ください。







----

Pythonに書き慣れてない以上に実装上課題点はいろいろありますが、とりあえず動いたのでヨシ！

(mdなのに長くなっちゃったので、遷移図のマーメイド記法や、スタイルの調整をすべきだったな)


で、これを

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">With 100 days until the <a href="https://twitter.com/hashtag/G7?src=hash&amp;ref_src=twsrc%5Etfw">#G7</a> <a href="https://twitter.com/hashtag/HiroshimaSummit?src=hash&amp;ref_src=twsrc%5Etfw">#HiroshimaSummit</a>, let&#39;s touch on the host city&#39;s attractions - incl. <a href="https://twitter.com/hashtag/Hiroshima?src=hash&amp;ref_src=twsrc%5Etfw">#Hiroshima</a> Castle 🏯! Constructed by MORI Terumoto in the 16th century, it was later lost; rebuilt in 1958, it offers a museum showcasing Hiroshima&#39;s history.<a href="https://t.co/Kak2dIB2Oo">https://t.co/Kak2dIB2Oo</a> <a href="https://t.co/oJ3S6Jvd6Q">pic.twitter.com/oJ3S6Jvd6Q</a></p>&mdash; japan (@japan) <a href="https://twitter.com/japan/status/1623200012057579520?ref_src=twsrc%5Etfw">February 8, 2023</a></blockquote>

みたいな感じで埋め込み形式でhtmlにパースすると見やすいかも。


しかしよくいままでこのAPIを無料で保持していたなと思います。
