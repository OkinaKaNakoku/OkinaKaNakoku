class ShowDetailUserListDto:
    # コンストラクタ：スコア表示
    def __init__(self, userId, lastName, firstName, rank, score, scoreResult):
        self.userId = userId
        self.lastName = lastName
        self.firstName = firstName
        self.rank = rank
        self.score = score
        self.scoreResult = scoreResult

