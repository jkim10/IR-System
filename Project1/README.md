## 6111 Project 1: Information Retreival System
By Justin Kim (jyk2149) and Mavis Athene U Chen (mu2288)

**Files in submission:**
* `requirements.txt`
* `search.py`
* `README.md`

**How to Run:**
 1. `pip install -r requirements.txt`
 2. `python search <API Key> <Engine Key> <Precision> <Query>`

Search Engine ID: db7c825fd9c7885a2

API KEY: AIzaSyC6uXsEBblG4JwiO7X25rG5RDUdQrOmrkc

Sample Run with Above API Key and Engine Key:

`python search.py AIzaSyC6uXsEBblG4JwiO7X25rG5RDUdQrOmrkc db7c825fd9c7885a2 .5 "per se"`

**Internal Design:**

All our functional code is in `search.py`. We have a `main` function that is the skeleton code that does displayes the query results, receives user input, calculates the precision, etc. We have a total of four helper functions, two of which are called in `main`: `get_query` and `augment_query`. `get_query` retrieves the top 10 articles from the google api. `augment_query` is the core of implementing our query modification, we call another function `tf-idf` here. `tf-idf` is where we create the tf-idf weights for words in both the relevant and non relevant document summaries and title (provided by the google API). We call the function `normalize_text` is that makes sure that when we perform other calculations the text are all uniform; we get rid of punctions and turn text into lowercase. In addition we use the PorterStemmer external library from NLTK to stem all our text for us (ie, cases -> case). After the documents are cleaned, we calculate the tf-idf by using scikit-learn's TfidfVecotrizer. We store and manipulate the tf-idf vecotrizer output with pandas dataframe. More on the implementation of query modification in the section below.

List of external libaries we used:
* [NLTK - PorterStemmer](https://www.nltk.org/howto/stem.html)
* [Scikit-learn - TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
* [Pandas - Dataframe](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)

**Query Modification:**

We base our query modification on the vector model we discussed in class. There are two main components that we used: tf-idf weights and Rocchio's algorithm. We try to maximize the modified query vector to be as similar to the relevant documents and opposite for the non relevant documents. In the `augment_query` function, we take in the query along with the relevant and non relevant documents, which are the summaries and titles of the relevant and non relevant entires based on user feedback. That is, the documents is simply a string with summary + title. If an entry does not have a summary provided, we simply take the title of the document. We then clean up the documents using the `normalize_text` function (no punctuation, lowercase). We use the stemmer here so we don't weigh same words with different stems, for example "case" instead of "cases". We then create tf-idf vectors in the `tf-idf` function for the query and all relevant and non relevant documents. We use scikit-learn's TfIdfVectorizer to do that for us where we initialize the vectorizer with the following parameters: `tfidf_vectorizer = TfidfVectorizer(stop_words="english", sublinear_tf=True, min_df=2)`. We customize the vectorizer with three parameters: (1) to not count english stop words, (2) sublinear scaling, which means we take 1 + log(tf), (3) the word must appear in at least 2 documents. The vectorizer provides an output that we manipulate using a dataframe from pandas. The output is similar to what we discussed in class, rows represent different documents and columns representing the unique words in each document. We then proceed with with Rocchio's algorithm in which we find the words in relevant documents which would result in the highest augmented query vector. The Rocchio algorithm has three terms, we used `alpha = 1.0` for the original query vector, `beta = 0.75` for the relevant document text, and `gamma = 0.15` for the non relevant document text. We calculated the result for all the words in the relevant documents using the formula discussed in class with the constant mentioned, where we add the original query vector, add the sum of all the relevant document vectors and subtract the sum of all the non relevant document vectors. After we get the results, we sort them in descending order. To construct the new query, we take the first two words, which have the highest scores, and append it to the original query in order: original query + highest scoring word + 2nd highest scoring word. We also make sure that these highest scoring words do not appear in the original query, if it does we simply continue down the result list. Now, we have constructed our new query which will then be return to the main function for the iterative process. 





