from enum import Enum, auto
from controller import GameController, ScoreController, CPUStrength


class Status(Enum):
    MENU = auto()
    GAME = auto()
    SCORE = auto()


class AppInterface:
    def __init__(self, max_turn: int):
        self.max_turn = max_turn
        self.status = Status.MENU
        self.game_controller = GameController(max_turn)
        self.score_controller = ScoreController()

    def handle_message(self, message: str, user_id: str):
        if self.status is Status.MENU:
            yield from self.menu_handle_message(message, user_id)
        elif self.status is Status.GAME:
            yield from self.game_handle_message(message, user_id)
        elif self.status is Status.SCORE:
            yield from self.score_handle_message(message, user_id)
        else:
            raise Exception(f"unsupported Status {self.status}")

    # --- message handler for MENU mode ---
    def menu_handle_message(self, message: str, user_id: str):
        if message in ("遊ぶ", "ハードモード"):
            if message == "ハードモード":
                self.game_controller.cpu_strength = CPUStrength.HARD
            yield from self.game_controller.start_game()
            self.status = Status.GAME
        elif message == "ルール":
            yield from self.show_rule()
        elif message == "スコア":
            yield from self.show_score(user_id)
        elif message == "スコアを消す":
            yield from self.score_controller.ask_clear_score()
            self.status = Status.SCORE
        else:
            yield from self.show_commands()

    @staticmethod
    def show_rule():
        rule_text = (
            "〜 ルール説明 〜\n"
            "シングルポーカーは、あなたと CPU で一枚の手札の強さを競うトランプゲームです。"
            "最初の山札はA,2,3,4,5,6,7,8,9,10,J,Q,Kの13枚です。"
            "次の手順でゲームが進行します。\n\n"
            "1) あなたと CPU は山札からそれぞれ一枚引く。\n\n"
            "2) CPU は手札を捨てるかどうか選択し、捨てる場合は山札から一枚引く。"
            "捨てたカードは公開される。\n\n"
            "3) あなたは手札を捨てるかどうか選択し、捨てる場合は山札から一枚引く。"
            "捨てたカードは公開される。\n\n"
            "4) 2),3) をあと4回繰り返す。\n\n"
            "5) 最終的に残った手札の強さが強いほうが勝ち。強さは次の通り:\n"
            "2<3<4<5<6<7<8<9<10<J<Q<K\n"
            "AはJ,Q,Kには勝ち、それ以外には負ける。"
        )
        yield rule_text

    @staticmethod
    def show_score(user_id: str):
        yield from ScoreController.show_score(user_id)

    @staticmethod
    def show_commands():
        yield "以下のいずれかの言葉を送信してください。"
        yield "「遊ぶ」：ゲームを開始します。"
        yield "「ルール」：ルールを表示します。"
        yield "「スコア」：スコアを表示します。"
        yield "「スコアを消す」：スコアを消去します。"

    # --- message handler for GAME mode ---
    def game_handle_message(self, message: str, user_id: str):
        yield from self.game_controller.handle_message(message, user_id)
        if not self.game_controller.is_active:
            self.status = Status.MENU
            self.game_controller.__init__(self.max_turn)

    # --- message handler for SCORE mode ---
    def score_handle_message(self, message: str, user_id: str):
        yield from self.score_controller.handle_message(message, user_id)
        if not self.score_controller.is_asking_clear_score:
            self.status = Status.MENU
