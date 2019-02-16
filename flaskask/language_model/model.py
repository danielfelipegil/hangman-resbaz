from string import ascii_lowercase
from collections import defaultdict
import pickle
import math

ngram_counts = pickle.load(
    open("/Users/kartik/PycharmProjects/hangman-resbaz/flaskask/language_model/ngram_counts.pickle", "rb"))


def get_ngram_prob(letter, context, n, lambdas):
    prob = 0
    # create tuples to make a query with context
    if (n > 1):
        if (len(context) > 1):
            conditional = tuple(context)
        elif (len(context) == 1):
            conditional = context[0]
        else:
            conditional = tuple()  # no context at all

    if (n > 4):

        # calculate the fivegram
        fivegram_count = ngram_counts[5][conditional][letter] * lambdas[5]
        fivegram_total_count = float(sum(ngram_counts[5][conditional].values()))
        if fivegram_total_count != 0:
            interp_prob_fivegram = fivegram_count / fivegram_total_count
        else:
            interp_prob_fivegram = 0
            lambdas[4] += lambdas[5]  # if count is 0 I will give the lambda weight to the next ngram

        prob += interp_prob_fivegram

    if (n > 3):
        # calculate the fourgram
        fourgram_count = ngram_counts[4][conditional][letter] * lambdas[4]
        fourgram_total_count = float(sum(ngram_counts[4][conditional].values()))
        if fourgram_total_count != 0:
            interp_prob_fourgram = fourgram_count / fourgram_total_count
        else:
            interp_prob_fourgram = 0
            lambdas[3] += lambdas[4]  # if count is 0 I will give the lambda weight to the next ngram

        prob += interp_prob_fourgram

    if (n > 2):
        # calculate the trigram
        trigram_count = ngram_counts[3][conditional][letter] * lambdas[3]
        trigram_total_count = float(sum(ngram_counts[3][conditional].values()))
        if trigram_total_count != 0:
            interp_prob_trigram = trigram_count / trigram_total_count
        else:
            interp_prob_trigram = 0
            lambdas[2] += lambdas[3]  # if count is 0 I will give the lambda weight to the next ngram

        prob += interp_prob_trigram

    if (n > 1):
        # calculate the bigram
        bigram_count = ngram_counts[2][conditional][letter] * lambdas[2]
        bigram_total_count = float(sum(ngram_counts[2][conditional].values()))
        if bigram_total_count != 0:
            interp_prob_bigram = bigram_count / bigram_total_count
        else:
            interp_prob_bigram = 0
            lambdas[1] += lambdas[2]  # if count is 0 I will give the lambda weight to the next ngram

        prob += interp_prob_bigram

    if (n > 0):
        unigram_count = ngram_counts[1][letter] * lambdas[1]
        unigram_total_count = float(sum(ngram_counts[1].values()))
        if unigram_total_count != 0:
            interp_prob_unigram = (unigram_count) / (
                unigram_total_count)  #  not smoothed with laplace like the unigram model
        else:

            # out-of-vocabulary words = 1 / |V|
            lambdas[0] += lambdas[1]
            vocab_size = len(unigram_total_count)
            interp_prob_unigram = (1 / float(vocab_size)) * lambdas[0]
        prob += interp_prob_unigram

    return math.log(prob)


def ngram_guesser(mask, guessed, **kwargs):
    letter_available = [letter for letter in ascii_lowercase if letter not in guessed]
    blank_probs = {}
    letter_probs = {}
    probs = []
    if kwargs.get('n'):
        n = kwargs.get('n')
    else:
        n = 1
    if kwargs.get('lambdas'):
        lambdas = kwargs.get('lambdas')
    else:
        lambdas = {1: 1}
    word = convert_word(mask, 2)
    letter_probs = defaultdict(float)
    for i in range(len(word)):
        if (word[i] == "_"):
            context = []
            j = i - 1
            context_len = 1
            while word[j] != "_" and j >= 0 and context_len < n:
                context.insert(0, word[j])
                j -= 1
                context_len += 1
            for letter in letter_available:
                probability = get_ngram_prob(letter, context.copy(), n, lambdas.copy())
                letter_probs[letter] += probability

    letter_choice = max(letter_probs, key=letter_probs.get)

    return letter_choice


def convert_word(word, n):
    start = []
    end = []
    start_index = 1

    # padding with sentinent symbols

    while start_index < n:
        start.append("<s" + str(start_index) + ">")
        start_index += 1

    end_index = n
    while end_index > 1:
        end.append("</s" + str(end_index - 1) + ">")
        end_index -= 1

    return start + [l.lower() for l in word] + end
