class ShowDetailUserListDto:
    # コンストラクタ：スコア表示
    def __init__(self, userId, lastName, firstName, rank, score, horaCnt, horaPer, hojuCnt, hojuPer, scoreResult, isMine):
        self.userId = userId
        self.lastName = lastName
        self.firstName = firstName
        self.rank = rank
        self.score = score
        self.horaCnt = horaCnt
        self.horaPer = horaPer
        self.hojuCnt = hojuCnt
        self.hojuPer = hojuPer
        self.scoreResult = scoreResult
        self.isMine = isMine
