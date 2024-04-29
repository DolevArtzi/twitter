import json
from random import shuffle,choice
import re
class TweetRetriever:
    def __init__(self,likes_path='me/all_likes.json',bookmarks_path='me/all_bookmarks.json') -> None:
        self.path_to_data = '../../data/'
        self.l_path = self.path_to_data + likes_path
        self.b_path = self.path_to_data + bookmarks_path
        self.likes = self.loadFromFile(self.l_path)
        self.key_names = list(self.likes[0].keys())
        self.interaction_key_names = list(self.likes[0]['interaction'].keys())
        self.bookmarks = self.loadFromFile(self.b_path)
        self.all = self._union(self.bookmarks,self.likes)
        self.datasets = ['all','bookmarks','likes']
        self.dataMap = {'all':self.all,'bookmarks':self.bookmarks,'likes':self.likes}
        self._cleanNames(self.likes)
        self._cleanNames(self.bookmarks)
        self._cleanNames(self.all)

    
    def _cleanNames(self,tweets):
        for t in tweets:
            name = t['authorName']
            if '\n' in name:
                name = name.split('\n')[0]
                t['authorName'] = name

    def randomLike(self):
        return choice(self.likes)
    
    def randomBookmark(self):
        return choice(self.bookmarks)
    
    def random(self):
        return choice(self.all)

    def retrieveLikes(self,limit=None,random=False):
        if not random:
            if limit:
                return self.likes[:min(limit,len(self.likes))]
            return self.likes
        if not limit:
            copy = self.likes[:]
            shuffle(copy)
            return copy
        copy = self.likes[:]
        shuffle(copy)
        return copy[:min(limit,len(self.likes))]
    
    def snippet(self,tweet):
        keys = ['handle','tweetText','time']
        return {k:tweet[k] for k in keys}


    def retrieveSnippet(self,limit=None,random=False):
        l = self.retrieveLikes(limit=limit,random=random)
        keys = ['handle','tweetText','time']
        return [{k:x[k] for k in keys} for x in l]
    
    def getTweetID(self,tweet):
        url = tweet['postUrl']
        return url.split('/')[-1]

    def clean(self,text):
        pattern = re.compile(r'[^a-zA-Z\s]')
        return re.sub(pattern, '', text)

    def contains(self,text,substrs):
        text = self.clean(text)
        lower = text.lower()
        for s in substrs:
            if s in lower:
                return True
            # if re.search(text,s,re.IGNORECASE):
                # return True
        return False
    
    def filterContains(self,substrs,dataset='all'):
        data = self.dataMap[dataset] if dataset in self.datasets else dataset[1]
        return [tweet for tweet in data if 'tweetText' in tweet and self.contains(tweet['tweetText'],substrs)]

    def filterAuthor(self,handle,dataset='bookmarks'):
        data = self.dataMap[dataset]
        return [t for t in data if t['handle'] == handle]

    def prettyPrint(self,tweet):
        print(json.dumps(tweet, indent=4))
        print()
    
    def getLink(self,tweet):
        if 'postUrl' in tweet:
            return tweet['postUrl']
        return None
    
    def prettyTime(self,time):
        # '2023-12-10T16:15:31.000Z'
        dates = time.split('-')
        yr = dates[0]
        month = dates[1]
        daytime = dates[2].split('.')[0].split('T')
        day = daytime[0]
        times = daytime[1].split(':')
        hr = int(times[0]) % 12
        ampm = 'am' if int(times[0]) <= 12 else 'pm'
        if hr == 0:
            hr = 12
        mins = times[1]
        return '.'.join([month,day,yr]) + ' at ' + str(hr) + ':' + mins + ' ' + ampm
        
    def prettifyForWrite(self,tweet,sp=True):
        s = ''
        s += '*' * 100 + '\n'
        if 'authorName' in tweet:
            s += 'author: ' + tweet['authorName'] + '\n'
        if 'handle' in tweet:
            s += tweet['handle'] + "'s tweet\n"
        if 'time' in tweet:
            s += self.prettyTime(tweet['time']) + '\n'
        if 'tweetText' in tweet:
            s += tweet['tweetText'] + '\n'
        if 'postUrl' in tweet:
            s += tweet['postUrl'] + '\n'

        s += '*' * 100 + ('\n' if sp else '')
        return s

    def _union(self,l1,l2):
        m = {}
        for x in l2:
            m[self.getTweetID(x)] = x
        for x in l1:
            id = self.getTweetID(x)
            if id in m:
                continue
            m[id] = x
        return list(m.values())

    def writeTweetsToFile(self,tweets,file,includeInteractions=False,share_header=None,pretty=False):
        base = '../../data/analyzed_data/'
        if share_header:
            # tweets = self._excludeInteractions(tweets)
            try:
                with open(base + 'shareable/' + ''.join(file.split(".")[:-1]) + ".txt",'x') as f:
                    f.write('=' * 200 + '\n')
                    f.write(share_header)
                    f.write('\n\n')
                    if pretty:
                        for t in tweets:
                            f.write(self.prettifyForWrite(t))
                            f.write('\n')
                    else:
                        f.write(json.dumps(t,indent=4))
                    f.write('\n')
                    f.write('=' * 200 + '\n')
            except FileExistsError:
                print('File already exists! Aborting.')
        else:
            if includeInteractions:
                tweets = self._excludeInteractions(tweets)
            try:
                with open(base + '/raw_analyzed_data/' + file,'x') as f:
                    f.write(json.dumps(tweets))
            except FileExistsError:
                print('File already exists! Aborting.')

    
    def filterContainsAndWrite(self,substrs,file,dataset='all',includeInteractions=False,shareable=False):
        print('=' * 80)
        print(f'In dataset "{dataset if isinstance(dataset,str) else dataset[0]}"')
        print('Searching for substrings:')
        phrases = ',\n '.join(substrs)
        tweets = self.filterContains(substrs,dataset) #if dataset in self.datasets and isinstance(dataset,str) else self.filterContains(substrs,dataset[1])
        print(f'Writing {len(tweets)} Tweets to {file}...')
        if len(tweets) > 0:
            self.writeTweetsToFile(tweets,file,includeInteractions=includeInteractions)
            if shareable:
                print(f'Writing {len(tweets)} Prettyfied Tweets to {"".join(file.split(".")[:-1]) + ".txt"}...')
                header = f'Tweets in dataset "{dataset if isinstance(dataset,str) else dataset[0]}" containing one or more of the following phrases:\n'
                header += phrases
                self.writeTweetsToFile(tweets,file,includeInteractions=False,share_header=header,pretty=True)
        else:
            print('No matching Tweets found.')
        print('Done')
        print('=' * 80)

        if not includeInteractions:
            return self._excludeInteractions(tweets)
            
        return tweets

    def loadFromFile(self,file):
        with open(file,'r') as f:
            return json.load(f)

    def _excludeInteractions(self,tweets):
        tweets = tweets[:]
        for t in tweets:
            if 'interaction' in t:
                del t['interaction']
        return tweets

if __name__ == '__main__':
    tr = TweetRetriever()
    snippets = tr.retrieveSnippet(2,random=1)
    for s in snippets:
        print(json.dumps(s,indent=2))