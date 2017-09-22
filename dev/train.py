import pickle
from os import listdir

import numpy as np
from scipy.io import wavfile
from sklearn import svm

from src.sound_processing import extract_features


def get_features_for_all(dirname):
    data = []
    for filename in listdir(dirname):
        if filename.endswith('.wav'):
            _, x = wavfile.read(dirname + filename)
            if x.dtype == np.int16:
                x = x.astype(np.float16, order='C') / 2 ** 15
            features = extract_features(x)
            data.append(features)
    return data


if __name__ == '__main__':
    positive_features = get_features_for_all('out/positives/')
    negative_features = get_features_for_all('out/negatives/')
    all_features = positive_features + negative_features
    all_labels = [True] * len(positive_features) + [False] * len(negative_features)
    classifier = svm.SVC()
    classifier.fit(all_features, all_labels)
    with open('classifier.p', 'wb') as f:
        pickle.dump(classifier, f)
