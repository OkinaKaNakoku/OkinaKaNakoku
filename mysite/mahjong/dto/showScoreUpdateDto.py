class ShowScoreUpdate:
    # コンストラクタ：スコア表示
    def __init__(self, user):
        self.userId = user.user_id
        self.name = user.last_name + ' ' + user.first_name
