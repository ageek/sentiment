import datetime
import json
import feedparser
import matplotlib.pyplot as plt
import numpy as np
from pattern.web import URL, Document, HTTP404NotFound, URLError, plaintext

def get_dom(url):
    
    try:
        s_content = URL(url).download(timeout=120, cached=False)
    except (URLError, HTTP404NotFound):
        print "Error downloading article"
        return None

    #for AJE compatibility
    try:
        s_content = s_content.decode('unicode_escape')
    except (UnicodeEncodeError):
        pass
    
    return Document(s_content)

##Works perfectly for AJE
##BBC results may be suspect; so much extra crap on the page
##TODO: write specific scrape functions
def heuristic_scrape(article):
    dom = get_dom(article)
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

##exploits a hidden (and very nice) direct API 
def search_aje(result, term, howmany):    
    SEARCH_PROXY = 'http://ajnsearch.aljazeera.net/SearchProxy.aspx'
    SEARCH_ARGS = '?m=search&c=english&f=english_cluster&s=as_q&q='+term+'&p=0&r='+str(howmany)+'&o=any&t=r&cnt=gsaSearch&target=gsaSearch'
    query = SEARCH_PROXY + SEARCH_ARGS
    dom = get_dom(query)

    #use same format as RSS code to preserve graphing functionality
    result['AJE'] = []
    for resultlink in dom.by_attribute(ctype='c'):
        title = plaintext(resultlink.content)
        link = resultlink.attributes['href']
        content = heuristic_scrape(link)
        score = sentiment(content)
        result['AJE'].append((title, 'NEG' if score < 0 else 'POS'))
        print 'AJE', title, link, 'NEG' if score < 0 else 'POS'
    return result

##unreliable, only works on alternate runs for some reason, probably time lapse
##also rarely returns howmany results
def search_cnn(result, term, howmany):
    RESULTS_URL = 'http://searchapp.cnn.com/cnn-search/query.jsp?query='+term+ \
              '&ignore=article|mixed&start=1&npp='+str(howmany)+'|'+str(howmany)+'|'+str(howmany)+'&s=all&type=all'+ \
              '&sortBy=date&primaryType=mixed&csiID=csi1'

    print "Getting CNN JSON blob"
    dom = get_dom(RESULTS_URL)
    print "Blob retrieved"
    
    #I do not understand this bizarre data structure
    for jscode in dom.by_id('jsCode'):
        search = json.loads(jscode.source())
        
    result['CNN'] = []
    results = search['results']
    titles = []
    for resultset in results:
        for article in resultset:
            title = plaintext(article['title'])
            link = article['url']
            if 'http://' in link and not title in titles: #exludes video, dupes
                content = heuristic_scrape(link)
                score = sentiment(content)
                if len(result['CNN']) < howmany:
                    result['CNN'].append((title, 'NEG' if score < 0 else 'POS'))
                    titles.append(title)
                    print 'CNN', title, link, 'NEG' if score < 0 else 'POS'
                else:
                    print 'too many'
                    break
    return result

def search_bbc(result, term, howmany, rurl, page):
    #convenient text only search
    if not rurl == None and 'www.bbc.co.uk' in rurl:
        query = rurl #for pagination support
    else:
        query = 'http://www.bbc.co.uk/search/news/'+term.lower()+'?text=on'

    dom = get_dom(query)

    if 'BBC' not in result:
        result['BBC'] = []
    
    for a in dom.by_class('title'):
        title = plaintext(a.content)
        link = a.attributes['href']
        content = heuristic_scrape(link)
        score = sentiment(content)
        if len(result['BBC']) < howmany:
            result['BBC'].append((title, 'NEG' if score < 0 else 'POS'))
            print 'BBC', title, link, 'NEG' if score < 0 else 'POS'
            if len(result['BBC']) % 20 == 0 and len(result['BBC']) < howmany: #20 articles per page
                print 'flip'
                next_page = 'http://www.bbc.co.uk/search/news/'+term+ \
                            '?page='+str(page+1)+'&text=on&dir=fd&news='+ \
                            str(len(result['BBC'])+1)+'&news_av=1'
                return search_bbc(result, term, howmany, next_page, page+1)
        else:
            break
    return result     

#from matplotlib examples
def autolabel(rects):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                ha='center', va='bottom')

##[(title, (NEG|POS))]
def plot(articles, term):
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
    plt.title('Comparative sentiment of \''+term+'\' - '+ str(datetime.datetime.now()))
    plt.ylabel('Article count')
    plt.legend((rects1[0],rects2[0]),('Positive','Negative'))
    
    autolabel(rects1)
    autolabel(rects2)
    plt.show()

 
term = raw_input("Search term: ")
count = int(raw_input("How many: "))

#build result dict to same format as RSS version so graphing doesn't change
result = {}

#for some reason, CNN only works on alternate runs
#so get to it first to avoid wasting time on others
result = search_cnn(result, urllib.quote(term), count)
result = search_aje(result, urllib.quote(term), count)
result = search_bbc(result, urllib.quote(term), count, None, 1)

plot(result, term)
