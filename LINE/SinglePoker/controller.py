from enum import Enum, auto
import random
from core import SinglePoker, GameNotFinishedError, DeckRunsOutError
import db_score


# *****************************************************************
#  For GameController
# *****************************************************************
class CPUStrength(Enum):
    NORMAL = auto()
    HARD = auto()


class GameController:
    def __init__(self, max_turn: int):
        self.game_master = SinglePoker(max_turn)
        self.cpu_strength = CPUStrength.NORMAL
        self.is_active = False

    def start_game(self):
        self.is_active = True
        yield "===== ゲーム開始 ====="
        yield "あなたと CPU は山札から一枚ずつ引きました。"
        yield from self.advance_until_your_choice()

    def message_handler(self, message: str, user_id: str):
        # --- Your Turn ---
        if message.lower() not in ("y", "n"):
            yield "Y または n と入力してください。"
            yield from self.ask_your_choice()
            return
        yield from self.your_playing(message.lower() == "y")
        self.game_master.advance_turn()

        # --- Game Finish Judge ---
        try:
            winner = self.game_master.winner
        except GameNotFinishedError:
            pass
        else:
            yield from self.show_result(winner)
            ScoreController.update_score(user_id, winner == 1, self.cpu_strength)
            self.is_active = False
            return

        # --- Next Turn ---
        yield from self.advance_until_your_choice()

    def advance_until_your_choice(self):
        yield f"〜{self.game_master.turn.count}(/{self.game_master.max_turn})ターン目〜"
        yield from self.cpu_playing()
        self.game_master.advance_turn()
        yield from self.show_status()
        yield "【あなたのターン】"
        yield from self.ask_your_choice()

    def show_status(self):
        yield f"山札: 残り{self.game_master.num_cards_in_deck}枚"
        yield f"現在の捨て札: [{', '.join(map(str, self.game_master.trash))}]"
        yield f"あなたの手札: {self.game_master.hands[1]}"

    def show_result(self, winner: int):
        yield f"CPU の手札: {self.game_master.hands[0]}"
        yield f"あなたの手札: {self.game_master.hands[1]}"
        result = "勝ち" if winner == 1 else "負け"
        yield f"あなたの{result}です。"
        yield "===== ゲーム終了 ====="
        if result == "勝ち" \
                and self.cpu_strength is CPUStrength.NORMAL \
                and random.randint(0, 4) == 0:
            yield "【隠しモード】"
            yield "「遊ぶ」の代わりに「ハードモード」と入力すると、CPU が少し強くなります。"

    def cpu_playing(self):
        yield "【CPU のターン】"
        if self.cpu_strength is CPUStrength.NORMAL:
            replace_hand = self.to_replace_hand_normal()
        elif self.cpu_strength is CPUStrength.HARD:
            replace_hand = self.to_replace_hand_hard()
        else:
            raise Exception(f"unsupported CPUStrength {self.cpu_strength}")

        if replace_hand:
            try:
                self.game_master.replace_hand(player=0)
            except DeckRunsOutError:
                yield "山札が無いため、CPU は手札を交換できませんでした。"
            else:
                yield "CPU は手札を捨て、山札から一枚引きました。"
        else:
            yield "CPU はステイしました。"

    def to_replace_hand_normal(self) -> bool:
        # Implement a behavior of 'Normal' CPU here
        raise NotImplementedError

    def to_replace_hand_hard(self) -> bool:
        # Implement a behavior of 'Hard' CPU here
        raise NotImplementedError

    @staticmethod
    def ask_your_choice():
        yield "手札を交換しますか？(Y/n)"

    def your_playing(self, replace_hand: bool):
        if replace_hand:
            try:
                self.game_master.replace_hand(player=1)
            except DeckRunsOutError:
                yield "山札が無いため、あなたは手札を交換できませんでした。"
            else:
                yield "あなたは手札を捨て、山札から一枚引きました。"
        else:
            yield "あなたはステイしました。"


# *****************************************************************
#  For ScoreController
# *****************************************************************
class ScoreController:
    def __init__(self):
        self.is_asking_clear_score = False

    def message_handler(self, message: str, user_id: str):
        if not self.is_asking_clear_score:
            return
        if message.lower() == "y":
            yield from self.clear_score(user_id)
        elif message.lower() == "n":
            yield from self.cancel_clear_score()
        else:
            yield "Y または n と入力してください。"
            yield from self.ask_clear_score()

    @staticmethod
    def show_score(user_id: str):
        yield "【スコア】"
        score = db_score.get_score(user_id)
        if score.win_hard is score.lose_hard is None:
            yield f"{score.win}勝{score.lose}敗"
        else:
            yield f"ノーマルモード：{score.win}勝{score.lose}敗"
            yield f"ハードモード：{score.win_hard}勝{score.lose_hard}敗"

    @staticmethod
    def update_score(user_id: str, b_win: bool, cpu_strength: CPUStrength):
        b_lose = not b_win
        win, lose, win_hard, lose_hard = db_score.get_score(user_id)
        if cpu_strength is CPUStrength.NORMAL:
            win += int(b_win)
            lose += int(b_lose)
        elif cpu_strength is CPUStrength.HARD:
            win_hard = int(b_win) if win_hard is None else win_hard + int(b_win)
            lose_hard = int(b_lose) if lose_hard is None else lose_hard + int(b_lose)
        else:
            raise Exception(f"unsupported CPUStrength {cpu_strength}")
        db_score.update_score(user_id, win, lose, win_hard, lose_hard)

    def ask_clear_score(self):
        yield "スコアを消去しますか？この操作は元に戻せません。(Y/n)"
        self.is_asking_clear_score = True

    def clear_score(self, user_id: str):
        db_score.clear_score(user_id)
        yield "スコアを消去しました。"
        self.is_asking_clear_score = False

    def cancel_clear_score(self):
        yield "スコアの消去はキャンセルされました。"
        self.is_asking_clear_score = False
