class UpdateScoreDAO:
    # コンストラクタ：スコア表示
    def __init__(self, userId, score):
        self.userId = userId
        self.score = int(score)
