import time
import pickle
import pylab
import feedparser
from pattern.vector import Document, LEMMA
from pattern.web import Wikipedia, Google, NEWS

def gettitles(feeds):
    titles = {}
    for key in feeds:
        titles[key] = []
        newsfeed = feedparser.parse(feeds[key])
        for article in newsfeed['entries']:
            titles[key].append(article.title)
    return titles

def doclist_from_feeds(feeds):
    titles = gettitles(feeds)
    documents = []
    for key in titles:
        doc = Document(" ".join(titles[key]), stemmer=LEMMA, threshold=0)
        documents.append(doc)
    return documents

def gettopics(feeds):
        
    documents = doclist_from_feeds(feeds)
    topicsets = []
    
    for doc in documents:
        words = []
        for tup in doc.keywords(top=20):
            words.append(str(tup[1]))
        topicsets.append(words)

    topdict = {}
    for topiclist in topicsets:
        for topic in topiclist:
            try:
                topdict[topic] = topdict[topic] + 1
            except KeyError:
                topdict[topic] = 0

    topics = []
    for key in topdict:
        if topdict[key] > 0: #mentioned more than once
            if(key.endswith('ium')):
            #stemmer thinks country names are Latin plurals
               topics.append(key.replace('ium','ia'))
            else:
                topics.append(key)

    return topics

##Wikipedia, the poor man's ontology
def isnews(topic):
    engine = Wikipedia()
    result = engine.search(topic)
    if result:
        if topic not in result.title:
            return False
        newsthings = ['places','cities','capitals','countries','people','wars']
        categories = result.categories
        for category in categories:
            for thing in newsthings:
                if thing in category.lower():
                    return True
        return False
    else:
        return False

def gnewshits(topic):
    engine = Google()
    results = engine.search(topic, type=NEWS)
    return results.total

feedlist = {'AJE':'http://english.aljazeera.net/Services/Rss/?PostingId=2007731105943979989',
            'CNN':'http://rss.cnn.com/rss/cnn_world.rss',
            'BBC':'http://feeds.bbci.co.uk/news/world/rss.xml',
            'GOOGTOP':'http://news.google.com/news?ned=us&topic=h&output=rss',
            'GOOGWORLD':'http://news.google.com/news?ned=us&topic=w&output=rss',
            'REUTOP':'http://feeds.reuters.com/reuters/topNews?format=xml',
            'REUWORLD':'http://feeds.reuters.com/reuters/worldNews?format=xml',
            'APTOP':'http://hosted2.ap.org/atom/APDEFAULT/3d281c11a96b4ad082fe88aa0db04305',
            'APWORLD':'http://hosted2.ap.org/atom/APDEFAULT/cae69a7523db45408eeb2b3a98c0c9c5'}

HOUR = 3600 #seconds
DAY = 24

topicdata = [] #(time.now, [(topic, hits)])

timestr = str(time.time())
storename = 'news/news-'+timestr+'.data'
logname = 'news/news-'+timestr+'.log'
log = open(logname,'w')
print timestr + ' starting NewsGrapher'
log.write(timestr + ' starting NewsGrapher\n')
for i in range(DAY):
    topics = gettopics(feedlist)
    print topics
    topics = filter(isnews, topics)
    print topics
    topics = map(lambda x: (x, gnewshits(x)), topics)

    data = (time.time(), topics)
    topicdata.append(data)
    
    log.write(str(data) + "\n")
    log.flush()
    
    time.sleep(HOUR)
    msg = str(time.time()) + ' hour ' + str(i+1) + ' has passed.\n'
    print msg
    log.write(msg)
log.close()

store = open(storename, 'w')
pickle.dump(topicdata, store)
store.close()
    
    
