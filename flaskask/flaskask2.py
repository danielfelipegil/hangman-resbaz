import os
from random import randint

from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

app = Flask(__name__)
ask = Ask(app, "/")

gameCounter = 0
maxAttempts = 10
wordPickedFromRep = 'hello'


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


@ask.session_ended
def session_ended():
    return "{}", 200


if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
app.run(debug=True)
