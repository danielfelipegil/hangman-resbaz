import json
import os
import pickle
import random

import validation
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
from game import hangman
from language_model.model import ngram_guesser

app = Flask(__name__)
ask = Ask(app, "/")

maxAttempts = 10
wordPickedFromRep = 'Sample'


@app.route('/')
def homepage():
    return render_template('index.html')


@ask.launch
def welcome_game():
    # This is the start of the game, just presenting to user the welcome intent
    # Initialize session with defaults
    session.attributes['word'] = ''
    session.attributes['mask'] = ''
    session.attributes['gameCounter'] = 0
    session.attributes['flag'] = 0
    session.attributes['letterUsed'] = []

    return question(render_template('welcome'))


@ask.intent("HangmanIntent")
def new_game():
    # On getting a utterance of GO from the user, this will choose word and store it in session
    words = pickle.load(open('./language_model/test_set.pickle', 'rb'))
    word = random.choice(words)

    # Setting session details
    session.attributes['word'] = word
    session.attributes['mask'] = '_' * len(word)
    session.attributes['gameCounter'] = 0
    session.attributes['letterUsed'] = []
    session.attributes['flag'] = 1  # Indicates that guessing can begin

    # Here we should return the hint about the word, such as the length
    return question(render_template('length_hint', length=len(word), attempts=maxAttempts))


@ask.intent("GuessIntent", convert={'country': str})
def guess(country):
    # Get details from session
    gameCounter = session.attributes['gameCounter']
    wordPickedFromRep = session.attributes['word']
    mask = session.attributes['mask']
    flag = session.attributes['flag']
    lettersUsed = session.attributes['letterUsed']

    if flag:
        # Check whether word said is a country or not
        if country.lower() not in validation.country:
            return question(render_template('wrong_country', country=country))

        # Get the country's first letter and add it to the set of alphabets spoken till now
        letterSpoken = (country[0]).lower()
        lettersUsed.append(letterSpoken)
        tempSet = set(lettersUsed)
        lettersUsed = list(tempSet)
        session.attributes['letterUsed'] = lettersUsed

        # Evaluation logic
        if letterSpoken in wordPickedFromRep:
            if gameCounter < maxAttempts:
                updatedMask = masking(wordPickedFromRep, mask, letterSpoken)
                session.attributes['mask'] = updatedMask
                createJSON_File(updatedMask, lettersUsed, gameCounter)
                # Win condition
                if '_' not in session.attributes['mask']:
                    return question(render_template('win', quest=wordPickedFromRep))
                return question(render_template('correct', letter=letterSpoken, attempts=(maxAttempts - gameCounter)))
            else:
                return statement(render_template('lose', attempts=maxAttempts))
        elif letterSpoken not in wordPickedFromRep:
            # Update game counter for every incorrect choice made
            gameCounter = gameCounter + 1
            session.attributes['gameCounter'] = gameCounter
            createJSON_File(mask, lettersUsed, gameCounter)
            if gameCounter < maxAttempts:
                return question(render_template('incorrect', letter=letterSpoken, attempts=(maxAttempts - gameCounter)))
            else:
                return statement(render_template('lose', attempts=maxAttempts))
    else:
        return question(render_template('wrong_GO'))


@ask.intent("NLTKGuessIntent")
def nltk_guess():
    attempts = 12
    word = session.attributes['word']
    nltk_mistakes, mask = hangman(word, ngram_guesser, attempts, True, lambdas=[0.01] * 10, n=3)
    return question(str(nltk_mistakes) + ' mistakes! Result: ' + ' '.join(mask))


@ask.session_ended
def session_ended():
    return "{}", 200


def masking(original, masked, letter):
    newMasked = ''
    for character in original:
        if letter == character:
            newMasked = newMasked + letter
        else:
            newMasked = newMasked + '_'
    newMasked2 = ''
    for charOld, charNew in zip(masked, newMasked):
        if charOld == '_' and charNew == '_':
            newMasked2 = newMasked2 + '_'
        elif charNew not in '_' and charOld in '_':
            newMasked2 = newMasked2 + charNew
        else:
            newMasked2 = newMasked2 + charOld
    return newMasked2


def createJSON_File(mask, lettersUsed, gameCounter):
    # JSON Dictionary - Update with details to display
    js = {}
    js['maskedWord'] = mask
    js['alphabetsUsed'] = lettersUsed
    js['livesRemaining'] = maxAttempts - gameCounter
    # Dump to file
    with open('data.json', 'w') as jsonFile:
        json.dump(js, jsonFile)


if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=True)
