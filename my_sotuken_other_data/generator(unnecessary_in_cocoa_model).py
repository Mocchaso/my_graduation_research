import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from cocoa.core.util import read_pickle, write_pickle
from cocoa.model.counter import build_vocabulary, count_ngrams
from cocoa.model.ngram import MLENgramModel

from core.tokenizer import detokenize

### changed parts:
"""
import os
from collections import OrderedDict
import pprint
from core.tokenizer import tokenize
import gensim
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
"""
###

class Generator(object):
    def __init__(self, templates):
        self.templates = templates.templates

        """
        print("self.templates:")
        print(self.templates)
        print("self.templates.shape:")
        print(self.templates.shape)
        """

        """
        # output template to csv
        # self.templates.to_csv("../all_templates.csv", encoding="utf-8")
        """

        """
        context, template = self.templates["context"].values, self.templates["template"].values
        template_tuple = zip(context, template) # [(context_i, template_i)]
        context_word_df = pd.DataFrame(columns=["word", "word_count"])
        template_word_df = pd.DataFrame(columns=["word", "word_count"])
        
        cv_contexts = CountVectorizer(token_pattern=u'(?u)\\b\\w+\\b') # include 1 character word by token_pattern
        cv_templates = CountVectorizer(token_pattern=u'(?u)\\b\\w+\\b') # include 1 character word by token_pattern
        context_matrix = cv_contexts.fit_transform(context)
        template_matrix = cv_templates.fit_transform(template)
        context_matrix = context_matrix.toarray()
        template_matrix = template_matrix.toarray()

        print("context_matrix:")
        print(context_matrix)
        print("context_matrix.shape:")
        print(context_matrix.shape)
        print("type(context_matrix):")
        print(type(context_matrix))

        print("template_matrix:")
        print(template_matrix)
        print("template_matrix.shape:")
        print(template_matrix.shape)
        print("type(template_matrix):")
        print(type(template_matrix))

        context_words_count = np.sum(context_matrix, axis=0)
        template_words_count = np.sum(template_matrix, axis=0)

        # exchange key and value
        context_dict = {v: k for k, v in cv_contexts.vocabulary_.items()}
        template_dict = {v: k for k, v in cv_templates.vocabulary_.items()}

        for word_id, word in sorted(context_dict.items()): # ascend sort by word_id
            s = pd.Series([word, context_words_count[word_id]], index=context_word_df.columns)
            context_word_df = context_word_df.append(s, ignore_index=True)
        print("finish recording context word count.")

        for word_id, word in sorted(template_dict.items()): # ascend sort by word_id
            s = pd.Series([word, template_words_count[word_id]], index=template_word_df.columns)
            template_word_df = template_word_df.append(s, ignore_index=True)
        print("finish recording template word count.")

        context_word_df.to_csv("../all_contexts_word_count.csv")
        template_word_df.to_csv("../all_templates_word_count.csv")
        """

        """
        context_word_df = pd.read_csv("../all_contexts_word_count.csv", index_col=0)
        template_word_df = pd.read_csv("../all_templates_word_count.csv", index_col=0)

        context_word_df = context_word_df.sort_values("word_count", ascending=False)
        template_word_df = template_word_df.sort_values("word_count", ascending=False)

        print("context_word_df:")
        print(context_word_df)
        print("template_word_df:")
        print(template_word_df)
        print("descend ... template_word_df['word_count'].values:")
        print(template_word_df['word_count'].values)
        """

        """
        ### record sorted by word_count to csv
        context_word_df.to_csv("../descend_all_contexts_word_count.csv")
        template_word_df.to_csv("../descend_all_templates_word_count.csv")

        ### record removed stopwords
        self.stopwords_en = stopwords.words("english")
        context_word_df = pd.read_csv("../descend_all_contexts_word_count.csv", index_col=0)
        template_word_df = pd.read_csv("../descend_all_templates_word_count.csv", index_col=0)
        
        context_word_df = context_word_df[~context_word_df["word"].isin(self.stopwords_en)]
        template_word_df = template_word_df[~template_word_df["word"].isin(self.stopwords_en)]

        context_word_df.to_csv("../no_stopwords_all_contexts_word_count.csv")
        template_word_df.to_csv("../no_stopwords_all_templates_word_count.csv")
        """


        self.vectorizer = TfidfVectorizer()
        self.build_tfidf()

        """
        ### changed parts:
        self.now_executing_path = os.getcwd()
        ### load Google's pre-trained Word2Vec model.
        ### take about 2 minitues
        if "my_sotuken" in self.now_executing_path:
            print("loading Google's pre-trained Word2Vec model. ")
            self.model = gensim.models.KeyedVectors.load_word2vec_format('./GoogleNews-vectors-negative300.bin', binary=True)
            print("finish loading Google's pre-trained Word2Vec model.")
        ###
        """

    def build_tfidf(self):
        # memo:
        # self.templates -> [38651 rows x 8 columns]
        # documents -> list, 38651 length
        documents = self.templates['context'].values
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)

    def _add_filter(self, locs, cond):
        locs.append(locs[-1] & cond)

    def _select_filter(self, locs):
        print [np.sum(loc) for loc in locs]
        for loc in locs[::-1]:
            if np.sum(loc) > 0:
                return loc
        return locs[0]

    def get_filter(self, used_templates=None):
        if used_templates:
            loc = (~self.templates.id.isin(used_templates))
            if np.sum(loc) > 0:
                return loc
        # All templates
        return self.templates.id.notnull()
    
    '''
    ### changed parts:
    def normalize_vec(self, v):
        """
        type(v): numpy.ndarray
        """
        return v / np.linalg.norm(v)

    def avg_feature_vector(self, utterance_template, model, num_features):
        """
        Calculate average words of feature vector in a utterance template
        """
        # remove unnecessary token
        utterance_template = utterance_template.replace("{", "")
        utterance_template = utterance_template.replace("}", "")
        utterance_template = utterance_template.replace("<", "")
        utterance_template = utterance_template.replace(">", "")

        words = tokenize(utterance_template)
        print("words in a template:")
        print(words)

        feature_vec = np.zeros((num_features,), dtype="float32") # initialize feature vector variable
        skipped_word_count = 0
        for word in words:
            try:
                # if now ord is included in english stopwords, do nothing.
                if word not in self.stopwords_en:
                    feature_vec = np.add(feature_vec, model.wv[word])
                else:
                    skipped_word_count += 1
                    print("word: {} is stopword.".format(word))
                    print("skipped a word: '{}'".format(word))
            except KeyError as e:
                # if now word is not in Word2Vec, do nothing.
                skipped_word_count += 1
                print(e)
                print("skipped a word: '{}'".format(word))
        if len(words) > 0:
            # feature_vec = np.divide(feature_vec, len(words) - skipped_word_count)
            pass
        return feature_vec
    ###
    '''
    
    def retrieve(self, context, used_templates=None, topk=20, T=1., **kwargs):
        """
        ### changed parts:
        ### divide processing by executing path(my_sotuken or craigslistbargain)
        print("self.now_executing_path: {}".format(self.now_executing_path))
        ###

        if "my_sotuken" in self.now_executing_path:
            import user_attributes_manager
            
            ### changed parts: topk = 20 -> 40
            topk = 40
            ###
            loc = self.get_filter(used_templates=used_templates, **kwargs)
            if loc is None:
                return None

            if isinstance(context, list):
                context = detokenize(context)
            
            ### memo: extract feature from current dialogue context
            features = self.vectorizer.transform([context])
            ### memo: calculate similarities
            
            print("self.tfidf_matrix:")
            print self.tfidf_matrix
            print("self.tfidf_matrix.shape:")
            print self.tfidf_matrix.shape
            print("features.T:")
            print features.T
            print("features.T.shape:")
            print features.T.shape
            
            scores = self.tfidf_matrix * features.T
            scores = scores.todense()[loc]
            scores = np.squeeze(np.array(scores), axis=1)
            
            print("scores:")
            print(scores)
            print("scores.shape:")
            print(scores.shape)
            
            ### memo: rank two context vectors, and extract top k ids
            
            ids = np.argsort(scores)[::-1][:topk]
            print("ids:")
            print(ids)

            print("self.templates:")
            print self.templates
            print("self.templates.shape: {}".format(self.templates.shape)) # 38651, 8
            print("self.templates[loc]:")
            print self.templates[loc]
            print("self.templates[loc].shape: {}".format(self.templates[loc].shape)) # 236, 8

            ##### original element!

            topk_templates = self.templates['context'][ids].values
            print("topk_templates:")
            print(topk_templates)
            topk_templates_average = None

            ### changed method in changed parts:
            ### TF-IDF -> Word2Vec

            # method by Word2Vec
            attr_word_vec = self.model.wv["quality"]
            # normalize 
            attr_word_vec = self.normalize_vec(attr_word_vec)
            print("attr_word_vec:")
            print(attr_word_vec)
            print("attr_word_vec.shape:")
            print(attr_word_vec.shape)

            for template in topk_templates:
                print("now template:")
                print(template)

                num_features = 300 # dimension of Word2Vec pretrained model
                template_feature_avg = self.avg_feature_vector(template, self.model, num_features)
                # normalize
                template_feature_avg = self.normalize_vec(template_feature_avg)
                print("template_feature_avg:")
                print(template_feature_avg)
                print("template_feature_avg.shape:")
                print(template_feature_avg.shape)

                # calculate cosine similarity
                # -> attr_word and template_feature_avg were normalized
                # -> can calculate correctly with only np.dot
                cos_sim = np.dot(attr_word_vec, template_feature_avg)
                print("cosine similarity (attr, template):")
                print(cos_sim)

            # method by TF-IDF (came to be unnecessary)
            for template in topk_templates:
                # remove unnecessary token
                template = template.replace("{", "")
                template = template.replace("}", "")
                template = template.replace("<", "")
                template = template.replace(">", "")
                words = tokenize(template)

                ### calculate each word feature of template
                word_dim = 8850
                # word_features = np.array([])
                word_features = np.empty((0, word_dim), float)
                print("word_features:")
                print(word_features)
                print("word_features.shape:")
                print(word_features.shape)
                print("type(word_features):")
                print(type(word_features))
                for word in words:
                    word_feature = self.vectorizer.transform([word]) # type: scipy.sparse.csr.csr_matrix
                    word_feature = word_feature.tolil()
                    word_feature = word_feature.toarray()
                    print("word_feature -> 1 no kazu:")
                    print(np.sum(word_feature == 1))

                    print("type(word_feature):")
                    print(type(word_feature))
                    print("word_feature:")
                    print(word_feature)
                    print("word_feature.shape:")
                    print(word_feature.shape)
                    
                    # np.vstack((word_features, word_feature))
                    word_features = np.append(word_features, word_feature, axis=0)
                
                print("word_features:")
                print(word_features)
                print("word_features.shape:")
                print(word_features.shape)
                print("type(word_features):")
                print(type(word_features))
                print("len(words):")
                print(len(words))

                ### calculate average of template context
                template_average = np.average(word_features, axis=0)
                print("template_average -> 0 janai kazu:")
                print(np.sum(template_average != 0))
                print("type(template_average):")
                print(type(template_average))
                print("template_average:")
                print(template_average)
                
                # topk_templates[""] = template_average

                attr_test = self.vectorizer.transform(["hello"])
                similarity_test = template_average * attr_test.T
                print("similarity test:")
                print(similarity_test)


            topk_tfidf = self.tfidf_matrix[ids, :]

            ### changed parts:
            ### store a result of questionnaire before a dialogue
            ### -> "conditon", "price", "brand", "popular"

            questionnaire_result = user_attributes_manager.UserAttributesManager.attributes_priority
            ### attributes name
            consider_attrs = [i[0] for i in questionnaire_result]
            ###

            ### changed parts:
            ### quality: [0, 6155], condition: [0, 2054]
            ### price: [0, 6007]
            ### sense: [0, 6908] ... intuition, hunch, perception, instinct: not found
            ### effect: [0, 2844]
            ### brand: [0, 1441]
            ### infromation: [0, 4173]
            ### popular: [0. 5904] ... trend, popularity, fashion: not found
            ###
            ### attr -> PPMI, SVD + Glove?
            features_t = [self.vectorizer.transform([attr]).T for attr in consider_attrs]
            attrs_features_table = OrderedDict(zip(consider_attrs, features_t))

            print("attrs_features_table:")
            pprint.pprint(attrs_features_table)
            ###
            
            print("topk_tfidf:")
            print(topk_tfidf)
            print("topk_tfidf.shape:")
            print(topk_tfidf.shape)
            

            scores = [topk_tfidf * attr_feature_t for attr_feature_t in attrs_features_table.values()]
            scores = [score.todense() for score in scores]
            ### memo: squeeze -> remove unnecessary dimension
            scores = [np.squeeze(np.array(score), axis=1) for score in scores]
            scores = OrderedDict(zip(consider_attrs, scores))
            pprint.pprint(scores)

            ids_from_scores = [np.argsort(score)[::-1] for score in scores.values()]
            ids_from_scores = OrderedDict(zip(consider_attrs, ids_from_scores))
            
            print("ids_from_scores:")
            pprint.pprint(ids_from_scores)

            score = topk_tfidf * self.vectorizer.transform(["price"]).T
            score = score.todense()
            score = np.squeeze(np.array(score), axis=1)
            ids = np.argsort(score)[::-1]
            #print(topk_tfidf)
            #print(self.vectorizer.transform(["price"]).T)
            #print(score)

            candidates = self.templates[loc]
            candidates = candidates.iloc[ids]
            ### sort cos similarity between retrieved context vectors and user's shopping attribute
            #candidates = candidates.iloc[result_ids]
            print("{} candidates: ".format(topk))
            print candidates
            
            rows = self.templates[loc]
            rows = rows.iloc[ids]
            logp = rows['logp'].values

            return self.sample(logp, candidates, T)
        
        elif "craigslistbargain" in self.now_executing_path:
        """

        loc = self.get_filter(used_templates=used_templates, **kwargs)
        if loc is None:
            return None

        if isinstance(context, list):
            context = detokenize(context)
        features = self.vectorizer.transform([context])
        scores = self.tfidf_matrix * features.T
        scores = scores.todense()[loc]
        scores = np.squeeze(np.array(scores), axis=1)
        ids = np.argsort(scores)[::-1][:topk]

        candidates = self.templates[loc]
        candidates = candidates.iloc[ids]
        rows = self.templates[loc]
        rows = rows.iloc[ids]
        logp = rows['logp'].values

        return self.sample(logp, candidates, T)

    def sample(self, scores, templates, T=1.):
        probs = self.softmax(scores, T=T)
        template_id = np.random.multinomial(1, probs).argmax()
        template = templates.iloc[template_id]
        return template

    def softmax(self, scores, T=1.):
        exp_scores = np.exp(scores / T)
        return exp_scores / np.sum(exp_scores)


class Templates(object):
    """Data structure for templates.
    """
    def __init__(self, templates=[], finalized=False):
        self.templates = templates
        self.template_id = len(templates)
        self.finalized = finalized

    @classmethod
    def from_pickle(cls, path):
        templates = read_pickle(path)
        return cls(templates=templates, finalized=True)

    def add_template(self, utterance, dialogue_state):
        raise NotImplementedError

    def finalize(self):
        self.templates = pd.DataFrame(self.templates)
        self.score_templates()
        self.finalized = True

    def save(self, output):
        assert self.finalized
        write_pickle(self.templates, output)

    def score_templates(self):
        sequences = [s.split() for s in self.templates.template.values]
        vocab = build_vocabulary(1, *sequences)
        counter = count_ngrams(3, vocab, sequences, pad_left=True, pad_right=False)
        model = MLENgramModel(counter)
        scores = [-1.*model.entropy(s)*len(s) for s in sequences]
        if not 'logp' in self.templates.columns:
            self.templates.insert(0, 'logp', 0)
        self.templates['logp'] = scores
