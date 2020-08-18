class UserScore:
    # コンストラクタ
    def __init__(self, user, rank, topDiff):
        self.lastName = user.last_name
        self.firstName = user.first_name
        self.scoreSum = user.score_sum
        self.rank = rank
        self.topDiff = topDiff