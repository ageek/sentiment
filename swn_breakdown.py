import pickle
import matplotlib.pyplot as pylab
from pattern.en import wordnet
from pattern.en.wordnet import wn, ADJECTIVE, ADVERB, VERB, NOUN

def count_type(pos):
    dictionaries = {ADJECTIVE : wn.ADJ,
                    ADVERB : wn.ADV,
                    VERB : wn.V,
                    NOUN : wn.N}
    
    positive, negative, neutral = [],[],[]
    for word in dictionaries[pos]:
        word = repr(word)
        word = word[:word.find('(')]
        if word in wordnet.sentiment:
            try:
                synset = wordnet.synsets(word, pos)
            except KeyError:
                continue
            for sense in synset:
                pscore, nscore, oscore = sense.weight
                if pscore > nscore:
                    positive.append(sense)
                elif pscore < nscore:
                    negative.append(sense)
                else:
                    neutral.append(sense)
    return (len(positive), len(negative), len(neutral), len(dictionaries[pos]))
                
def count_sentiments():
    parts_of_speech = [ADJECTIVE, ADVERB, VERB, NOUN]
    
    wordnet.sentiment.load()

    counts = {}

    for p in parts_of_speech:
        counts[p] = count_type(p)

    return counts

def savepiechart(title, labels, fractions, colors):
    pylab.figure(figsize=(4,4))
    ax = pylab.axes([0.1, 0.1, 0.8, 0.8])
    pylab.pie(fractions, labels=labels,
              colors=colors,autopct='%1.1f%%')
    pylab.title(title)
    pylab.savefig('images/'+title+'.png')

counts = {}

try:
    f = open('data/sentimentcounts','r')
    counts = pickle.load(f)
    f.close()
except IOError:
    print 'Creating new count data'
    counts = count_sentiments()
    f = open('data/sentimentcounts','w')
    pickle.dump(counts, f)
    f.close()

for key in counts:
    words = {'JJ' : 'Adjective',
             'VB' : 'Verb',
             'RB' : 'Adverb',
             'NN' : 'Noun'}
    pos, neg, neu, wntotal = counts[key]
    swntotal = float(pos + neg + neu)
    ppos = float(pos) / swntotal
    pneg = float(neg) / swntotal
    pneu = float(neu) / swntotal
    coverage = swntotal / float(wntotal)

    print words[key], 'positive: %.2f%%, negative: %.2f%%, netural: %.2f%%, coverage: %.2f%%' \
          % (100*ppos, 100*pneg, 100*pneu, 100*coverage)

    labels_sentiment = ['Positive', 'Negative', 'Neutral']
    fractions_sentiment = [100*ppos, 100*pneg, 100*pneu]

    savepiechart(words[key] + ' breakdown', labels_sentiment, fractions_sentiment, ['g','r','b'])

    labels_coverage = ['Covered','Not']
    pcov = 100 * coverage
    fractions_coverage = [pcov, 100 - pcov]

    savepiechart(words[key] + ' coverage', labels_coverage, fractions_coverage, ['c','w'])
    
