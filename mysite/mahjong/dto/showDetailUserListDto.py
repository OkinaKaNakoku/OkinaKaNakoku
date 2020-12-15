class ShowDetailUserListDto:
    # コンストラクタ：スコア表示
    def __init__(self, user, hanso):
        self.userId = user.get('user_id')
        self.lastName = user.get('last_name')
        self.firstName = user.get('first_name')
        self.rank = hanso.get('rank')
        self.score = int(hanso.get('score'))
        self.scoreResult = int(hanso.get('score_result'))