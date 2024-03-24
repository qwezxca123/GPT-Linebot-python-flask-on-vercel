from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
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
    
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

@line_handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    previous_sentence = event.message.text
    inputs = torch.tensor(tokenizer.encode(previous_sentence)).unsqueeze(0) 
    outputs = model.generate(inputs, max_length=100, 
                             do_sample=True, temperature=0.7,
                             pad_token_id=tokenizer.eos_token_id)

    predicted_response = tokenizer.decode(outputs[0, :], skip_special_tokens=True)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=predicted_response))
    return

if __name__ == "__main__":
    app.run()
