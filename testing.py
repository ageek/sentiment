from pattern.en import wordnet, tag
import os
import re

def sentiment(content):
    
    if len(wordnet.sentiment) == 0:
        wordnet.sentiment.load()
        
    relevant_types = ['JJ', 'VB', 'RB'] #adjectives, verbs, adverbs
    score = 0
    
    synsets = wordnet.synsets
    for word, pos in tag(content):
            if pos in relevant_types:
                try:
                    synset = synsets(word, pos)[0].weight
                except KeyError:
                    #incorrect part of speech tag
                    continue
                positivity, negativity, objectivity = synset
                score = score + (positivity - negativity) * (1 - objectivity)
                
    return score

def normalize(s):
    s = re.sub('\W' ,' ', s).lower()
    return s

def norm(s):
    lines = s.split('\n')
    content = "".join(lines)
    content = re.sub('\W' ,' ', content)
    return content

def meanstdv(x):
    from math import sqrt
    mean, std = 0, 0
    mean = sum(x) / float(len(x))
    dist = sum([(w - mean)**2 for w in x])
    std = sqrt(dist / float(len(x)-1))
    return mean, std

def test(directory, howmany=1000):
##    neg_mean = -1.055849375
##    neg_std = 2.78978505151
##    pos_mean = 0.80045275
##    pos_std = 3.15019581999
    total_mean = -0.1276983125
##    total_std = 3.12805937093
    count = 0
    pos, neg, scores = [], [], []
    for dirpath, dirnames, filenames in os.walk(directory):
        print dirpath
        for name in filenames:
            if count == howmany:
                break
            
            f = open(os.path.join(dirpath,name), 'r')
            content = f.read()
            f.close()
            
            content = norm(content)
            score = sentiment(content)
            
            neg.append(name) if score < total_mean else pos.append(name)
                
            scores.append(score)

            count = count + 1

    print 'positive reviews: %d, negative reviews: %d, total reviews: %d' \
          % (len(pos), len(neg), len(pos)+len(neg))
    print 'highest score was %f' % max(scores)
    print 'lowest score was %f' % min(scores)
    mean, std = meanstdv(scores)
    print 'mean: %f std: %f' % (mean, std)

def testreviews():             
    test('data/reviews/txt_sentoken/neg')
    test('data/reviews/txt_sentoken/pos')
