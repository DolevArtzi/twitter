from dotenv import load_dotenv
from transformers import RobertaForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
import numpy as np
import re
from scipy.special import softmax
from tqdm import tqdm
class TweetSentiment:
    def __init__(self) -> None:
        load_dotenv()
        MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL)
        self.config = AutoConfig.from_pretrained(MODEL)
        self.model = RobertaForSequenceClassification.from_pretrained(MODEL)
        self.map = {0:'negative',1:'neutral',2:'positive'}
        # model.save_pretrained(MODEL)

    # def clean(self,text): #we'll start by cleaning the text, potentially throwing away info that we may later choose to include
    #     pattern = re.compile(r'[^a-zA-Z\s]')
    #     return re.sub(pattern, '', text)

    def _preprocess(self,text):
        new_text = []
        for t in text.split(" "):
            t = '@user' if t.startswith('@') and len(t) > 1 else t
            t = 'http' if t.startswith('http') else t
            new_text.append(t)
        return " ".join(new_text)

    def getText(self,tweet):
        print(tweet)
        if 'tweetText' not in tweet:
            return ''
        return self._preprocess(tweet['tweetText']) 

    def _getScores(self,text):
        encoded_input = self.tokenizer(text,return_tensors='pt')
        output = self.model(**encoded_input)
        out = output[0][0].detach().numpy()
        scores = softmax(out)
        scores = [(self.map[i],score) for i,score in enumerate(scores)]
        scores = sorted(scores,key=lambda x: -x[1])
        return scores

    def printScores(self,scores):
        print('Scores:')
        for label,score in scores:
            print(f'{label}: {score:.3f}')
            

    def _score(self,text,print_=False):
        text = self._preprocess(text)
        scores = self._getScores(text)
        if print_:
            self.printScores(scores)
        return scores
    
    def score(self,tweet,print=False):
        text = self.getText(tweet)
        if not text:
            return False
        return self._score(text,print_=print)

    
    def getTopScore(self,text,print=False):
        ranked = self.score(text)
        if print:
            print(ranked[::-1])
        return ranked[::-1]

    def averageScore(self,tweets):
        if not tweets:
            return {self.map[i]:0 for i in range(3)}
        avgs = {i:0 for i in range(3)}
        l = 0
        for t in tqdm(tweets):
            scores = self.score(t)
            print(scores)
            if scores != False:
                l += 1
            for i in range(len(scores)):
                avgs[i] += scores[i][1]
        for k in avgs:
            v = avgs[k]
            del avgs[k]
            avgs[self.map[k]] = v / l
        return avgs

