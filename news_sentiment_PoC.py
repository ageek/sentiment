import feedparser
import datetime
import matplotlib.pyplot as plt
import numpy as np

##Works perfectly for AJE
##BBC results suspect; so much extra crap on the page
def heuristic_scrape(article):
    from pattern.web import URL, Document, HTTP404NotFound, URLError, plaintext
    try:
        s_content = URL(article).download()
    except (URLError, HTTP404NotFound):
        print "Error downloading article"
        return ("could not download", article)

    dom = Document(s_content)
    
    text = ''

    for node in dom.by_tag('p'):
        for c in node:
            if c.type == 'text':
                text = text + ' ' + plaintext(c.source())
    return text.strip()

##Bag-of-words sentiment analysis using SentiWordNet
def sentiment(content):
    from pattern.en import parse, split, wordnet #must have sentiwordnet available
    wordnet.sentiment.load()
    relevant_types = ['JJ', 'VB', 'RB'] #adjectives, verbs, adverbs
    score = 0
    sentences = split(parse(content, lemmata=True))
    for sentence in sentences:
        for word in sentence.words:
            if word.type in relevant_types:
                pos, neg, obj = wordnet.sentiment[word.lemma]
                score = score + ((pos - neg) * (1 - obj)) #weight subjective words heavily
    return 1 if score >=0 else -1

def analyze_rss_feeds(feeds):
    result = {}
    for key in feeds:
        result[key] = []
        newsfeed = feedparser.parse(feeds[key])
        entries = newsfeed['entries']
        for entry in entries:
            content = heuristic_scrape(entry.link)
            score = sentiment(content)
            result[key].append((entry.title, 'NEG' if score < 0 else 'POS'))
            print key, entry.title, entry.link, 'NEG' if score < 0 else 'POS'
    return result

#from matplotlib examples
def autolabel(rects):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                ha='center', va='bottom')

def plot(articles):
    negbars = []
    posbars = []
    for key in articles:
        neg, pos = 0, 0
        for title, polarity in articles[key]:
            if polarity == 'NEG':
                neg = neg+1
            else:
                pos = pos+1
        negbars.append(neg)
        posbars.append(pos)

    maxheight = max(max(negbars), max(posbars))

    N = len(articles) #number of keys
    ind = np.arange(N)
    width = 0.35

    plt.subplot(111)

    rects1 = plt.bar(ind, posbars, width, color='#007510')
    rects2 = plt.bar(ind+width, negbars, width, color='#b30f0f')

    ax = plt.gca()
    ax.set_ylim([0,maxheight+5])
    
    plt.xticks(ind+width, articles.keys())
    plt.title("World news RSS feeds - " + str(datetime.datetime.now()))
    plt.ylabel('Article count')
    plt.legend((rects1[0],rects2[0]),('Positive','Negative'))
    
    autolabel(rects1)
    autolabel(rects2)
    plt.show()

feeds = {'AJE':'http://english.aljazeera.net/Services/Rss/?PostingId=2007731105943979989',
         'CNN':'http://rss.cnn.com/rss/cnn_world.rss',
         'BBC':'http://feeds.bbci.co.uk/news/world/rss.xml'}

articles = analyze_rss_feeds(feeds)
plot(articles)
