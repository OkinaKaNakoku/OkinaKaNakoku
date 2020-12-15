class UserRecordDto:
    # コンストラクタ：戦績表示
    def __init__(self, user, rank, score, hansoCnt, maxScore, minScore, gameCnt, horaCnt, horaPercent, hojuCnt, hojuPercent, days):
        self.user = user
        self.rank = rank
        self.score = score
        self.hansoCnt = hansoCnt
        self.maxScore = maxScore
        self.minScore = minScore
        self.gameCnt = gameCnt
        self.horaCnt = horaCnt
        self.horaPercent = horaPercent
        self.hojuCnt = hojuCnt
        self.hojuPercent = hojuPercent
        self.days = days
