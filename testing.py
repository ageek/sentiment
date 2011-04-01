from pattern.en import parse, split, wordnet, tag
import os
import re

def sentiment(content):
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


def norm(s):
    lines = s.split('\n')
    content = "".join(lines)
    content = re.sub('\W' ,' ',content)
    return content

neg_mean = -1.055849375
neg_std = 2.78978505151
pos_mean = 0.80045275
pos_std = 3.15019581999
total_mean = -0.1276983125
total_std = 3.12805937093

wordnet.sentiment.load()

def meanstdv(x):
    from math import sqrt
    n, mean, std = len(x), 0, 0
    for a in x:
        mean = mean + a
    mean = mean / float(n)
    for a in x:
        std = std + (a - mean)**2
    std = sqrt(std / float(n-1))
    return mean, std

def test(d):
    for dirpath, dirnames, filenames in os.walk(d):
        print dirpath
        count = 0
        for name in filenames:
            f = open(os.path.join(dirpath,name), 'r')
            try:
                content = f.read()
                content = norm(content)
                score = sentiment(content)
                if score < total_mean:
                    neg.append(name)
                else:
                    pos.append(name)
                scores.append(score)
            except ValueError as e:
                print name, e
                break
            finally:
                f.close()
                
pos, neg, scores = [], [], []
test('data/reviews/txt_sentoken/neg')                         
print 'positive reviews: %d, negative reviews: %d, total reviews: %d' % (len(pos), len(neg), len(pos)+len(neg))
print "highest score was %f" % max(scores)
print "lowest score was %f" % min(scores)
mean, std = meanstdv(scores)
print mean, std

pos, neg, scores = [], [], []
test('data/reviews/txt_sentoken/pos')                         
print 'positive reviews: %d, negative reviews: %d, total reviews: %d' % (len(pos), len(neg), len(pos)+len(neg))
print "highest score was %f" % max(scores)
print "lowest score was %f" % min(scores)
mean, std = meanstdv(scores)
print mean, std
    
