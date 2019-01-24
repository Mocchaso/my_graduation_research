import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def is_positive(text):
    """
    ネガポジ判定でcompoundが0.5以上ならポジティブとする
    return: True or False
    """
    positive_threshold = 0.5 # ポジティブであると見なす閾値
    nltk.download("vader_lexicon") # ネガポジ判定に必要なモデルをダウンロード
    analyzer = SentimentIntensityAnalyzer()
    all_score = analyzer.polarity_scores(text)
    print("all_score '{}': {}".format(text, all_score))
    compound_score = all_score["compound"]
    return compound_score >= positive_threshold

if __name__ == "__main__":
    is_positive("I'm happy.")