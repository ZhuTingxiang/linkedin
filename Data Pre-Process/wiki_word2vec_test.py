# # -*- coding: utf-8 -*-
import gensim
from gensim.models import Phrases
from gensim.corpora import WikiCorpus
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
# from nltk.corpus import stopwords
from stop_words import get_stop_words
import os
import logging
# import jieba
import re
import multiprocessing
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# logging information
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logging.root.setLevel(level=logging.INFO)

# get input file, text format
inp = sys.argv[1]
input = open(inp, 'r')
output = open('output_word.seq', 'w')

# filtered_words = [word for word in word_list if word not in stopwords.words('english')]
# #
# if len(sys.argv) < 2:
#     print(globals()['__doc__'] % locals())
#     sys.exit(1)
stop_words = get_stop_words('en')
print stop_words

# read file and separate words
for line in input.readlines():
    line=line.strip('\n')
    new_line = ''


    for i in line.split(' '):
        if i.isalpha():
            if i.lower() not in stop_words:
                new_line += i.lower() + ' '
    output.write(new_line)

output.close()
output= open('output_word.seq', 'r')

# # initialize the model
# # size = the dimensionality of the feature vectors
# # window = the maximum distance between the current and predicted word within a sentence
# # min_count = ignore all words with total frequency lower than this.
# bigram = Phrases(LineSentence(output), min_count=1, threshold=2)
# # print(list(bigram[LineSentence(output)]))
# # bigram_transformer = gensim.models.Phrases(bigram)
# model = Word2Vec(bigram[LineSentence(output)], size=100,window=3, min_count=5,workers=multiprocessing.cpu_count())
model = Word2Vec(LineSentence(output), size=100, window=3, min_count=5,workers=multiprocessing.cpu_count())

# # save model
model.save('output_word.model')
model.save_word2vec_format('output_word.vector', binary=False)

# test
model=gensim.models.Word2Vec.load('output_word.model')
vocab = list(model.vocab.keys())
# print vocab[:10]
# print "----"
# print model.most_similar('engineering')
# print "----"
print model.similarity('engineer', 'consultant')
#
# for i in x:
#     print "Word: {}\t Similarity: {}".format(i[0], i[1])

# model = gensim.models.Word2Vec.load("output.model")
# print model.similarity("software enginner","software engineering")


