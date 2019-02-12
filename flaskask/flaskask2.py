import os
from random import randint

from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

app = Flask(__name__)
ask = Ask(app, "/")

gameCounter = 1
maxAttempts = 10
wordPickedFromRep = 'Hello'

@app.route('/')
def homepage():
    return render_template('index.html')


@ask.launch
def new_game():
    welcome_msg = render_template('welcome')
    return question(welcome_msg)


@ask.intent("YesIntent")
def next_round():
    numbers = [randint(0, 9) for _ in range(3)]
    round_msg = render_template('round', numbers=numbers)
    session.attributes['numbers'] = numbers[::-1]  # reverse
    return question(round_msg)


@ask.intent("AlphabetIntent", convert={'country': str})
def answer(country):
    letterSpoken = country[0]
    global gameCounter
    gameCounter = gameCounter + 1
    if letterSpoken in wordPickedFromRep:
        return question()


    return question(str('Letter selected from the word is ' + country[0]))


@ask.session_ended
def session_ended():
    return "{}", 200


if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
app.run(debug=True)
