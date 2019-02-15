import os
import pickle
import random
from random import randint

from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
from language_model.model import ngram_guesser
from game import hangman

app = Flask(__name__)
ask = Ask(app, "/")

gameCounter = 0
maxAttempts = 10
wordPickedFromRep = 'hello'


@app.route('/')
def homepage():
    return render_template('index.html')


@ask.launch
def welcome_game():
    welcome_msg = render_template('welcome')
    
    # GET NEW WORD
    return question(welcome_msg)

@ask.intent("HangmanIntent")
def new_game():
    # GET NEW WORD
    
    words = pickle.load( open( "/Users/danielgil/Documents/Repos/hangman-resbaz/flaskask/language_model/test_set.pickle", "rb" ) )
    word=random.choice(words)
    session.attributes['word']=word
    return question(word)

@ask.intent("GuessIntent", convert={'country': str})
def guess(country):
    global gameCounter
    gameCounter = gameCounter + 1
    letterSpoken = country[0]
    if letterSpoken.lower() in wordPickedFromRep:
        if gameCounter < maxAttempts:
            return question(render_template('correct', letter=letterSpoken, attempts=(maxAttempts - gameCounter)))
        else:
            return statement(render_template('lose', attempts=maxAttempts))
    elif letterSpoken.lower() not in wordPickedFromRep:
        if gameCounter < maxAttempts:
            return question(render_template('incorrect', letter=letterSpoken, attempts=(maxAttempts - gameCounter)))
        else:
            return statement(render_template('lose', attempts=maxAttempts))

@ask.intent("NLTKGuessIntent")
def nltk_guess():
    attempts=12
    word=session.attributes['word']
    nltk_mistakes,mask=hangman(word, ngram_guesser, attempts, True,lambdas=[0.01]*10,n=3)
    
    return question(str(nltk_mistakes)+" mistakes! Result: "+' '.join(mask))

@ask.session_ended
def session_ended():
    return "{}", 200


if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
app.run(debug=True)

