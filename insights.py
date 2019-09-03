import pandas as pandas
import numpy as np
import json
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.pipeline import make_pipeline
from sklearn.cluster import KMeans


def top_tfidf_feats(row, features, top_n=25):
    ''' Get top n tfidf values in row and return them with their corresponding feature names.'''
    topn_ids = np.argsort(row)[::-1][:top_n]
    top_feats = [(features[i], row[i]) for i in topn_ids]
    df = pandas.DataFrame(top_feats)
    df.columns = ['feature', 'tfidf']
    return df

def top_feats_in_doc(Xtr, features, row_id, top_n=25):
    ''' Top tfidf features in specific document (matrix row) '''
    row = np.squeeze(Xtr[row_id].toarray())
    return top_tfidf_feats(row, features, top_n)

def top_mean_feats(Xtr, features, grp_ids=None, min_tfidf=0.1, top_n=25):
    ''' Return the top n features that on average are most important amongst documents in rows
        indentified by indices in grp_ids. '''
    if grp_ids:
        D = Xtr[grp_ids].toarray()
    else:
        D = Xtr.toarray()

    D[D < min_tfidf] = 0
    tfidf_means = np.mean(D, axis=0)
    return top_tfidf_feats(tfidf_means, features, top_n)

def top_feats_per_cluster(X, y, features, min_tfidf=0.1, top_n=25):
    dfs = []
    labels = np.unique(y)
    for label in labels:
        ids = np.where(y==label)
        feats_df = top_mean_feats(X, features, ids, min_tfidf=min_tfidf, top_n=top_n)
        feats_df.label = label
        dfs.append(feats_df)
    return dfs

def main():
    with open('config.json') as json_config:
        config = json.load(json_config)

    emails = pandas.read_csv(config['filename'])

    # Prints [rows, columns]
    print("Rows, Columns")
    print(emails.shape)

    # Prints first email
    print(emails.head())

    # filter out stopwords
    stopwords = ENGLISH_STOP_WORDS.union(config['stopwords'])
    vect = TfidfVectorizer(analyzer='word', stop_words=stopwords, max_df=0.3, min_df=2)

    # Use 'subject' column.
    X = vect.fit_transform(emails['subject'].values.astype('U'))
    features = vect.get_feature_names()

    print("************ Top Features in Doc ************")
    print(top_feats_in_doc(X, features, 1, 25))

    print("************ Top Terms out of all emails ************")
    print(top_mean_feats(X, features, top_n=25))

    # Bucket emails into 3 clusters
    n_clusters = 3
    clf = KMeans(n_clusters=n_clusters,
                max_iter=1000,
                init='k-means++',
                n_init=1)
    labels = clf.fit_predict(X)

    print("************ Top Features per cluster ************")
    print(top_feats_per_cluster(X, labels, features, 0.1, 10))

if __name__ == '__main__':
    main()
