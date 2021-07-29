class ShowDetailBattleListDto:
    # コンストラクタ：スコア表示
    def __init__(self, battleNo, detailUsers, totalCnt):
        self.battleNo = battleNo
        self.detailUsers = detailUsers
        self.totalCnt  = totalCnt
