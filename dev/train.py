import pickle
from os import path

import numpy as np
from sklearn import svm
from sklearn.model_selection import cross_val_score

from dev.common import load_training_data
from src.util import my_print


def init_classifier():
    return svm.SVC(kernel='linear')


def train_classifier(X, y):
    classifier = init_classifier()
    classifier.fit(X, y)
    return classifier


def save_classifier(classifier):
    with open(path.join('src', 'classifier.p'), 'wb') as f:
        pickle.dump(classifier, f)


def score_classifier(X, y):
    classifier = init_classifier()
    return np.mean(cross_val_score(classifier, X, y))


def main():
    X, y = load_training_data()
    classifier = train_classifier(X, y)
    save_classifier(classifier)
    score = score_classifier(X, y)
    my_print('Created classifier with accuracy score %f' % score)


if __name__ == '__main__':
    main()
