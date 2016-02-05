import numpy
import dataset
import nltk
import ConfusionMatrix as cm
import logging as log

from Question import Question
from Flagger import Flagger

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cross_validation import train_test_split, StratifiedShuffleSplit
from sklearn import naive_bayes

log.basicConfig(level=log.DEBUG)


def create_classifier():
    clf = naive_bayes.GaussianNB()
    return clf


def transform_fit_test(conf_matrix, x_train, x_test, y_train, y_test):

    vectorizer = create_tfidf_vectorizer()
    clf = create_classifier()

    log.debug('tfidf transforming...')
    x_train = vectorizer.fit_transform(x_train)
    x_test = vectorizer.transform(x_test)

    y_train = numpy.array(y_train)

    log.debug('fitting')
    clf.fit(x_train.toarray(), y_train)

    log.debug('predicting')
    predictions = clf.predict(x_test.toarray())

    log.debug('accounting predictions')
    conf_matrix.count(predictions, y_test)

    return Flagger(vectorizer, clf)


def test_classifier_with_stratified_shuffle_split(features, classes):
    conf_matrix = cm.ConfusionMatrix()

    cv = StratifiedShuffleSplit(classes, random_state=42)

    for train_idx, test_idx in cv:
        log.debug('  testing split')

        x_train, y_train = [], []
        x_test, y_test = [], []

        for ii in train_idx:
            x_train.append(features[ii])
            y_train.append(classes[ii])
        for jj in test_idx:
            x_test.append(features[jj])
            y_test.append(classes[jj])

        transform_fit_test(conf_matrix, x_train, x_test, y_train, y_test)

    conf_matrix.show()


def create_tfidf_vectorizer():
    stopwords = nltk.corpus.stopwords.words('english')
    # 1000 -> 0.93
    # 2500 -> 0.94980
    # 2750 -> 0.94668
    # 3000 -> 0.9512
    # 3500 -> 0.95112

    # ngram_range(2, 2), max_features=050, Accuracy: 0.96280
    # ngram_range(2, 2), max_features=067, Accuracy: 0.96670
    # ngram_range(2, 2), max_features=071, Accuracy: 0.96723
    # ngram_range(2, 2), max_features=075, Accuracy: 0.96612
    # ngram_range(2, 2), max_features=082, Accuracy: 0.96538
    # ngram_range(2, 2), max_features=100, Accuracy: 0.96341
    # ngram_range(2, 2), max_features=500, Accuracy: 0.94569
    # ngram_range(2, 2), max_features=02k, Accuracy: 0.94160

    # ngram_range(3, 3), max_features=02k, Accuracy: 0.96850
    # ngram_range(3, 4), max_features=02k, Accuracy: 0.96665

    # ngram_range(4, 4), max_features=007, Accuracy: 1.00000
    # ngram_range(4, 4), max_features=015, Accuracy: 0.99131
    # ngram_range(4, 4), max_features=025, Accuracy: 0.98999
    # ngram_range(4, 4), max_features=050, Accuracy: 0.98999
    # ngram_range(4, 4), max_features=250, Accuracy: 0.98786
    # ngram_range(4, 4), max_features=500, Accuracy: 0.98704
    # ngram_range(4, 4), max_features=01k, Accuracy: 0.98409
    # ngram_range(4, 4), max_features=02k, Accuracy: 0.98294
    # ngram_range(4, 4), max_features=03k, Accuracy: 0.98031

    # ngram_range(4, 5), max_features=01k, Accuracy: 0.98409

    # ngram_range(3, 6), max_features=01k, Accuracy: 0.97621

    # ngram_range(3, 6), max_features=05k, Accuracy: 0.95287
    return TfidfVectorizer(stop_words=stopwords, max_features=5000, ngram_range=(3, 5))


def load_data_set():
    log.debug('loading the data set')
    features, classes, ids = dataset.load_from_csv()

    log.debug('Loaded dataset of ', len(ids), ' items')
    log.debug('  with ', len(set(Question.flags.values())), ' flags')

    x_train, x_validation, y_train, y_validation, id_train, id_validation = train_test_split(numpy.array(features),
                                                                                             numpy.array(classes),
                                                                                             ids,
                                                                                             test_size=0.20,
                                                                                             random_state=42)

    return x_train, x_validation, y_train, y_validation, id_train, id_validation


def validate():
    x_train, x_validation, y_train, y_validation, id_train, id_validation = load_data_set()

    log.debug('testing classifier')
    test_classifier_with_stratified_shuffle_split(x_train, y_train)

    log.debug('validating classifier')
    cf = cm.ConfusionMatrix()
    transform_fit_test(cf, x_train, x_validation, y_train, y_validation)
    cf.show()


def get_trained_classifier():
    x_train, x_validation, y_train, y_validation, id_train, id_validation = load_data_set()
    cf = cm.ConfusionMatrix()
    clf = transform_fit_test(cf, x_train, x_validation, y_train, y_validation)
    cf.show()
    return clf
