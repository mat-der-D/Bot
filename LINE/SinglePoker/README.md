# 各ファイルの構成
* main.py
本体。handle_message 内で受け答えを制御する。ユーザーごとに AppInterface オブジェクトを保持するための InterfaceDict を持っている。TOKEN や SECRET などの文字列もこのファイルで環境変数から呼び出す。

* interface.py
main.py の直接の窓口となる AppInterface クラスを定義。一回のやり取りで終了する操作(ルール表示やスコア表示など)は自分自身で処理し、二回以上のやり取りが必要な操作(ゲーム本体, スコア消去)は controller.py 内のクラスに任せる。

* controller.py
GameController クラスと ScoreController クラスを定義。それぞれゲーム本体の進行とスコア消去の際の役割を担う。いずれも AppInterface とコアエンジンの間に立ち、コアエンジンには状態の変化の命令を伝え、AppInterface には必要な文言を yield で渡す。GameController に対応するコアエンジンは core の SinglePoker で、ScoreController のコアエンジンは db_score 内の諸関数である。

* core.py
シングルポーカーのゲーム進行のコアエンジンを担う SinglePoker クラスを定義。サンプル用のゲームも実装してあるので、このファイル単体で実行しても遊べる。

* db_score.py
データベース内の score テーブルとの簡単なやり取りを関数として定義する。この関数たちを直接呼ぶのは ScoreController のみにし、データベースを更新したい場合は必ず ScoreController を経由するようにしている。データベースにアクセスするための設定もこのファイル内(で環境変数の値を呼ぶこと)で行っている。

* Procfile, requirements.txt, runtime.txt
Heroku で自動化する際に必要。詳しくは「Heroku LINEBot」等で検索。

# よくわからないポンチ絵
* 全体のフロー
LINE
↓メッセージ　↑返信
main.handle_message
↓メッセージ　↑返信の断片
interface.AppInterface().message_handler
↓メッセージ　↑返信の断片
controller.GameController()
controller.ScoreController()

* ゲームの制御[^1]
controller.GameController
↓進行の操作　↑ゲームの状態
core.SinglePoker()
[^1]ゲーム終了時のスコア更新のみ controller.ScoreController とやり取りする。

* スコアの制御
controller.ScoreController
↓DB操作　　　↑結果
db_score.py
↓クエリ　　　↑結果
データベース
