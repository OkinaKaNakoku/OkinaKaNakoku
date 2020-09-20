class HoraPercentageRankDto:
    # コンストラクタ：スコア表示
    def __init__(self, user, cnt, horaCnt, percentage, rank):
        self.lastName = user.last_name
        self.firstName = user.first_name
        self.cnt = cnt
        self.horaCnt = horaCnt
        self.percentage = percentage
        self.rank = rank
