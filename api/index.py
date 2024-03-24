from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage
from transformers import AutoTokenizer, AutoModelWithLMHead
import os
from io import BytesIO
from PIL import Image

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

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
model = AutoModelWithLMHead.from_pretrained("distilbert-base-uncased")

@line_handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    previous_sentence = event.message.text
    inputs = tokenizer.encode(previous_sentence, return_tensors='pt')
     
    # Get prediction from model
    outputs = model(inputs)[0]
    
    # Get predicted token ids and convert them into string
    predicted_response = tokenizer.decode(outputs[0, -1, :].argmax())
    
    # Log the relationship for future training
    with open("training_data.txt", "a") as f:
        f.write(f"{previous_sentence}\t{predicted_response}\n")

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=predicted_response))
    return

@line_handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    # 將 message_content 轉換為 bytes
    image_binary = BytesIO(message_content.content)
    # 解碼圖片
    image = Image.open(image_binary)
    image_url = "https://cdn2.ettoday.net/images/2904/2904577.jpg"
    preview_image_url=image_url = "https://cdn2.ettoday.net/images/2904/2904577.jpg"
    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text="收到圖片"),
            ImageSendMessage(
                original_content_url=image_url,
                preview_image_url=image_url
            )
        ])
    
if __name__ == "__main__":
    app.run()
