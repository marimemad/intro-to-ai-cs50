import nltk
import sys
import  os
import  string
import numpy as np

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    data = {}
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        s = open(path,"r")
        data[filename] = s.read()

    return data



def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """

    words = []
    for word in nltk.tokenize.word_tokenize(document.lower()):
        if word not in string.punctuation and  word not in nltk.corpus.stopwords.words("english"):
            words.append(word)

    return words

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    n=len(documents.keys())
    words=[]
    idf={}
    for filename in documents:
        words.extend(documents[filename])

    words=set(words)

    for word in words:
        count=0
        for filename in documents:
            if word in documents[filename]:
                count+=1
        idf[word]=np.log(n/count)
    return idf


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """

    tf_idf = {}
    for filename in files:
        tf_idf[filename] = 0

    for word in query:
        for filename in files:
            if word in files[filename]:
                tf=files[filename].count(word)
                tf_idf[filename] += tf*idfs[word]

    tf_idf=[ k for k,v in sorted(tf_idf.items(), key=lambda item:item[1], reverse=True) ]
    return(tf_idf[:n])



def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    scores = {}
    for sentence in sentences:
        scores[sentence] =[0,0]

    for word in query:
        for sentence in sentences:
            if word in sentences[sentence]:
                d = sentences[sentence].count(word)
                scores[sentence][0] += idfs[word]
                scores[sentence][1] += d

    for sentence in sentences:
        if scores[sentence][1] != 0:
            scores[sentence][1]=scores[sentence][1]/len(sentences[sentence])

    scores = [k for k, v in sorted(scores.items(), key=lambda x: (x[1][0], x[1][1]), reverse=True)]

    return scores[:n]


if __name__ == "__main__":
    main()
