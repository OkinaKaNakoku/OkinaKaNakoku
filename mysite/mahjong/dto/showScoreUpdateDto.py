class ShowScoreUpdateLabel:
    # コンストラクタ：スコア表示
    def __init__(self, user, rank, isOya):
        self.userId = user.user_id
        self.name = user.last_name + ' ' + user.first_name
        self.rank = rank
        self.score = "{:,}".format(user.score)
        self.isOya = isOya

class ShowScoreUpdate:
    def __init__(self, user):
        self.userId = user.user_id
        self.name = user.last_name + ' ' + user.first_name

class GameStatus:
    def __init__(self, gameStatus):
        self.kyoku = gameStatus.ba + " " + str(gameStatus.kyoku) + " " + "局"
        self.kyotaku = gameStatus.kyotaku
        self.honba = gameStatus.honba
