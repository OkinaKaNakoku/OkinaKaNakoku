from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

class LineBotCommand:
    line_bot_api = LineBotApi('QPWgl8tLIh8dHOdURlaXp+HiPny7jSkApqGdKqHTWRMVvzL2SjeVskSy0+26ILVQB0+UkocJZtDoiIKgTqtptSvopzFs+/m0loeJh8KwoApvUt6IYjWHBBB51Kfxx3IeUjiRwS2CNWtksO/V9aIlTQdB04t89/1O/w1cDnyilFU=')
    def pushMessage(msg):
        msg = msg + "ランキングを確認しませんか？" + "\r\n" + "https://okinakanakoku.pythonanywhere.com/mahjong/showRanking"
        LineBotCommand.line_bot_api.broadcast(TextSendMessage(text=msg))

    def pushTest(msg):
        LineBotCommand.line_bot_api.broadcast(TextSendMessage(text=msg))
