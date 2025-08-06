import pyxel
import random

# --- 定数 ---
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 100
TOTAL_QUESTIONS = 5  # 総問題数

# ノート名
NOTE_NAMES = ["C", "D", "E", "F", "G", "A", "B"]


class App:
    def __init__(self):
        """ゲームの初期化"""
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Perfect Pitch Game", fps=30)
        pyxel.mouse(True)  # マウスカーソルを表示

        self.game_state = "title"  # ゲームの状態 (title, playing, result)
        self.game_mode = 0  # 1:単音モード, 2:和音モード
        self.questions = []  # 出題される問題のリスト
        self.correct_answers = []  # 現在の問題の正解
        self.user_answers = []  # ユーザーの回答
        self.current_question_index = 0
        self.score = 0
        self.feedback_timer = 0  # 正解/不正解表示用のタイマー
        self.start_delay = 0  # ゲーム開始時の遅延タイマー
        self.last_answer_correct = False  # 直前の回答が正解だったか

        self.setup_sounds()  # Pyxelのサウンドをセットアップ

        pyxel.run(self.update, self.draw)

    def setup_sounds(self):
        """C4からB4までの音をセットアップ"""
        note_strings = ["c4", "d4", "e4", "f4", "g4", "a4", "b4"]
        for i, note_str in enumerate(note_strings):
            # 音符を4つ連続させて再生時間を長くする
            long_note_str = note_str * 4
            pyxel.sounds[i].set(long_note_str, "s", "5", "n", 12)

    # --- ゲームの状態ごとの更新処理 ---

    def update(self):
        """全体の更新処理"""
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
            if self.feedback_timer == 0:
                self.next_question()
            return  # フィードバック表示中は他の操作を無視

        # ゲームの状態に応じて処理を分岐
        if self.game_state == "title":
            self.update_title()
        elif self.game_state == "playing":
            self.update_playing()
        elif self.game_state == "result":
            self.update_result()

    def update_title(self):
        """タイトル画面の更新"""
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            # 1音モードボタン
            if self.is_mouse_over(30, 40, 40, 20):
                self.start_game(1)
            # 2音(和音)モードボタン
            if self.is_mouse_over(90, 40, 50, 20):
                self.start_game(2)

    def update_playing(self):
        """プレイ画面の更新"""
        if self.start_delay > 0:
            self.start_delay -= 1
            if self.start_delay == 0:
                self.play_notes()  # 遅延終了後に最初の音を鳴らす
            return  # 遅延中は操作を受け付けない

        if not pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            return

        # REPEATボタンのクリック判定
        if self.is_mouse_over(SCREEN_WIDTH - 42, 5, 40, 15):
            self.play_notes()
            return

        # 音符ボタンのクリック判定
        for i in range(len(NOTE_NAMES)):
            x = 12 + i * 20
            y = 75
            if self.is_mouse_over(x, y, 18, 15):
                if i not in self.user_answers:
                    self.user_answers.append(i)
                if len(self.user_answers) == self.game_mode:
                    self.check_answer()
                return

    def update_result(self):
        """結果画面の更新"""
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.is_mouse_over(50, 70, 60, 20):
                self.game_state = "title"

    # --- ゲームの状態ごとの描画処理 ---

    def draw(self):
        """全体の描画処理"""
        pyxel.cls(1)

        if self.game_state == "title":
            self.draw_title()
        elif self.game_state == "playing":
            self.draw_playing()
        elif self.game_state == "result":
            self.draw_result()

        # フィードバック表示
        if self.feedback_timer > 0:
            msg = "O" if self.last_answer_correct else "X"
            color = 8 if self.last_answer_correct else 7
            pyxel.rect(60, 35, 40, 20, color)
            pyxel.text(78, 42, msg, 0)

            # 不正解だった場合、正解を表示
            if not self.last_answer_correct:
                correct_notes_str = ", ".join(
                    [NOTE_NAMES[i] for i in self.correct_answers]
                )
                answer_msg = f"Correct: {correct_notes_str}"
                pyxel.text(SCREEN_WIDTH // 2 - len(answer_msg) * 2, 60, answer_msg, 7)

    def draw_title(self):
        """タイトル画面の描画"""
        pyxel.text(45, 20, "PERFECT PITCH GAME", 7)
        self.draw_button("1 NOTE", 30, 40, 40, 20)
        self.draw_button("2 NOTES", 90, 40, 50, 20)
        pyxel.text(98, 52, "(CHORD)", 7)

    def draw_playing(self):
        """プレイ画面の描画"""
        q_text = f"Q: {self.current_question_index + 1} / {TOTAL_QUESTIONS}"
        pyxel.text(5, 5, q_text, 7)
        score_text = f"SCORE: {self.score}"
        pyxel.text(5, 15, score_text, 7)

        if self.start_delay > 0:
            msg = "START!" if self.start_delay < 30 else "READY..."
            pyxel.text(SCREEN_WIDTH // 2 - len(msg) * 2, 45, msg, 7)
            return

        # ユーザーの回答表示位置を調整
        if self.game_mode == 2:
            ans_text = ""
            if len(self.user_answers) > 0:
                ans_text += NOTE_NAMES[self.user_answers[0]]
            if len(self.user_answers) > 1:
                ans_text += f", {NOTE_NAMES[self.user_answers[1]]}"
            # 表示位置を画面上部に変更
            pyxel.text(5, 25, f"Your Answer: {ans_text}", 7)

        # REPEATボタンを描画
        self.draw_button("REPEAT", SCREEN_WIDTH - 42, 5, 40, 15)

        for i, name in enumerate(NOTE_NAMES):
            x = 12 + i * 20
            y = 75
            self.draw_button(name, x, y, 18, 15, selected=(i in self.user_answers))

    def draw_result(self):
        """結果画面の描画"""
        pyxel.text(65, 30, "RESULT", 7)
        result_text = f"{self.score} / {TOTAL_QUESTIONS}"
        pyxel.text(SCREEN_WIDTH // 2 - len(result_text) * 2, 50, result_text, 7)
        self.draw_button("TITLE", 50, 70, 60, 20)

    # --- ヘルパー関数 ---

    def start_game(self, mode):
        """ゲームを開始する"""
        self.game_mode = mode
        self.score = 0
        self.current_question_index = 0
        self.questions = []
        for _ in range(TOTAL_QUESTIONS):
            if mode == 1:
                self.questions.append([random.randint(0, len(NOTE_NAMES) - 1)])
            else:  # mode == 2 (和音モード)
                note1 = random.randint(0, len(NOTE_NAMES) - 1)
                note2 = random.randint(0, len(NOTE_NAMES) - 1)
                # 2度の音程(隣り合う音)を避ける (音程の差が2未満)
                while abs(note1 - note2) < 2:
                    note2 = random.randint(0, len(NOTE_NAMES) - 1)
                self.questions.append(sorted([note1, note2]))

        self.user_answers = []
        self.correct_answers = self.questions[self.current_question_index]
        self.game_state = "playing"
        self.start_delay = 60  # 2秒間の遅延

    def next_question(self):
        """次の問題に進む"""
        self.current_question_index += 1
        if self.current_question_index >= TOTAL_QUESTIONS:
            self.game_state = "result"
            return

        self.user_answers = []
        self.correct_answers = self.questions[self.current_question_index]
        self.play_notes()

    def play_notes(self):
        """現在の問題の音（単音または和音）を再生する"""
        if self.game_mode == 1:
            note1_index = self.correct_answers[0]
            pyxel.play(0, note1_index, loop=False)
        elif self.game_mode == 2:
            note1_index, note2_index = self.correct_answers
            pyxel.play(0, note1_index, loop=False)
            pyxel.play(1, note2_index, loop=False)

    def check_answer(self):
        """答え合わせ"""
        user_answers_sorted = sorted(self.user_answers)
        self.last_answer_correct = user_answers_sorted == self.correct_answers
        if self.last_answer_correct:
            self.score += 1

        # フィードバック時間を2秒間に設定
        self.feedback_timer = 60

    def is_mouse_over(self, x, y, width, height):
        """マウスが指定範囲内にあるか判定"""
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        return x <= mx < x + width and y <= my < y + height

    def draw_button(self, text, x, y, width, height, selected=False):
        """ボタンを描画する"""
        col_text = 7
        if selected:
            col_bg = 10
        elif self.is_mouse_over(x, y, width, height):
            col_bg = 13
        else:
            col_bg = 6

        pyxel.rect(x, y, width, height, col_bg)
        pyxel.text(
            x + (width - len(text) * 4) // 2 + 1, y + (height - 6) // 2, text, col_text
        )


App()
