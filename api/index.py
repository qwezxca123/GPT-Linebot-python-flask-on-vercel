from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

app = Flask(__name__)

# domain root
@app.route('/')
def home():
    return 'Hello, World!'

@app.route("/webhook", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'
    
@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入一張圖片"))
    
    if event.message.text = "image":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="image"))
        return

@line_handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    image_url = line_bot_api.get_message_content(event.message.id).content_url
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"您所上傳的圖片的URL為：{image_url}"))
    
if __name__ == "__main__":
    app.run()
