from flask import Flask, render_template,request,url_for,redirect
from flask_bootstrap import Bootstrap
from main import SentimentAnalysis
import json
# NLP Packages
from textblob import TextBlob,Word
import random
import time

app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def index():
	return render_template('index.html')

@app.route("/chart")
def chart():
	return render_template('chart.html', set=zip(values, labels, colors))
@app.route('/analyse',methods=['GET,''POST'])
def analyse():
	sa = SentimentAnalysis()
	start = time.time()
	if request.method == 'POST':
		rawtext = request.form['rawtext']
		numTweets = request.form['numTweets']
		sa.DownloadData(rawtext, numTweets)
	return render_template('index.html',received_text = sa.searchTerm,number_of_tokens=numTweets,blob_subjectivity=sa.subjectivity_result,summary=sa.summary,keyword=rawtext, labels=sa.labels, values=sa.sizes, colors=sa.colors)

if __name__ == '__main__':
	app.run(debug=True)
