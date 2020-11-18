from find_restaurant import FindFoodPlace
from flask import Flask, render_template, request
app = Flask(__name__)
import requests
# bot = ChatBot("Candice")
# bot.set_trainer(ListTrainer)
# bot.set_trainer(ChatterBotCorpusTrainer)
# bot.train("chatterbot.corpus.english")

@app.route("/")
def home():    
	return render_template("home.html") 
@app.route("/get")
def get_bot_response():

	userText = request.args.get('msg')    
	response = FindFoodPlace.find(userText)
	return response
if __name__ == "__main__":    
	app.run(host="0.0.0.0",port=8000)
