import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn import metrics
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
import matplotlib.pyplot as plt
from sklearn.model_selection import validation_curve
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report


# Using grid search to perform parameter tuning
def parameter_tuning(training_matrix, training_labels, testing_labels, testing_matrix):
    # Set the parameters by cross-validation
    tuned_parameters = [{'C': np.linspace(0.01, 10, 100)}]
    #tuned_parameters = [{'n_neighbors': range(1,11)}]

    clf = GridSearchCV(LogisticRegression(penalty = "l2"), tuned_parameters, cv=4, scoring="accuracy")
    #clf = GridSearchCV(KNeighborsClassifier(), tuned_parameters, cv=4, scoring="accuracy")
    clf.fit(training_matrix, training_labels)

    print("Best parameters set found on development set:")
    print()
    print(clf.best_params_)
    print()
    print("Grid scores on development set:")
    print()
    means = clf.cv_results_['mean_test_score']
    stds = clf.cv_results_['std_test_score']
    for mean, std, params in zip(means, stds, clf.cv_results_['params']):
        print("%0.3f (+/-%0.03f) for %r"
                % (mean, std * 2, params))
    print()

    print("Detailed classification report:")
    print()
    print("The model is trained on the full development set.")
    print("The scores are computed on the full evaluation set.")
    print()
    y_true, y_pred = testing_labels, clf.predict(testing_matrix)
    print(classification_report(y_true, y_pred))
    print()
    print("Total accuracy:")
    print(accuracy_score(y_true, y_pred))
    print()

# Plot the validation curve
def validationCurve(document_features, label_vec):
    
    param_range = np.linspace(0.1, 4, 40)
    #param_range = range(1,11)
    train_scores, test_scores = validation_curve(
    SVC(kernel = "linear"), document_features, label_vec, param_name="C", param_range=param_range,
    cv=4, scoring="accuracy", n_jobs=1)

    #train_scores, test_scores = validation_curve(
    #LogisticRegression(), document_features, label_vec, param_name="C", param_range=param_range,
    #cv=4, scoring="accuracy", n_jobs=1)

    #train_scores, test_scores = validation_curve(
    #KNeighborsClassifier(), document_features, label_vec, param_name="n_neighbors", param_range=param_range,
    #cv=4, scoring="accuracy", n_jobs=1)

    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    plt.title("Validation Curve with Logistic Regression")
    #plt.title("Validation Curve with KNN")
    plt.xlabel("$C$")
    #plt.xlabel("$K$")
    plt.ylabel("Score")
    plt.ylim(0.5, 1.1)
    #plt.ylim(0.0, 1.1)
    lw = 2
    plt.semilogx(param_range, train_scores_mean, label="Training score",
                 color="darkorange", lw=lw)
    plt.fill_between(param_range, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.2,
                     color="darkorange", lw=lw)
    plt.semilogx(param_range, test_scores_mean, label="Cross-validation score",
                 color="navy", lw=lw)
    plt.fill_between(param_range, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.2,
                     color="navy", lw=lw)
    plt.legend(loc="best")
    plt.show()

    print("Plot complete")


def main():
    data_path = "../../Data collection/"

    training = open(data_path + "training", "rb")
    train_lst = pickle.load(training)
    training.close()

    testing = open(data_path + "testing", "rb")
    test_lst = pickle.load(testing)
    testing.close()

    stopwd = open(data_path + "stopwords", "rb")
    stopwords = pickle.load(stopwd)
    stopwd.close()

    #vectorizer = TfidfVectorizer(encoding = "utf8", decode_error = "strict", strip_accents = None, \
                                #stop_words = stopwords, ngram_range = (1,1), max_df = 0.9, min_df = 2, max_features = 10000)
    
    label_vec = []
    text_matrix = []

    true_label = []
    test_matrix = []

    for instance in train_lst:
        label_vec.append(instance[0])
        text_matrix.append(instance[1])

    for instance in test_lst:
        true_label.append(instance[0])
        test_matrix.append(instance[1])

    # Vectorize
    #document_features = vectorizer.fit_transform(text_matrix)
    #test_features = vectorizer.transform(test_matrix)
    
    document_features = np.matrix(text_matrix)
    
    test_features = np.matrix(test_matrix)

    # Parameter tuning
    print("Start Plotting")
    validationCurve(document_features, label_vec)
    print("Start Tuning")
    parameter_tuning(document_features, label_vec, true_label, test_features)






if __name__ == "__main__":
    main()
