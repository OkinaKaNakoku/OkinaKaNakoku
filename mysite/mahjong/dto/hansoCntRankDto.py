class HansoCntRank:
    # コンストラクタ：スコア表示
    def __init__(self, user, hansoSum, percentage, rank):
        self.lastName = user.last_name
        self.firstName = user.first_name
        self.hansoSum = hansoSum
        self.percentage = percentage
        self.rank = rank
