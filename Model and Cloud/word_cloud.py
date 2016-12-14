#!/usr/bin/env python
"""
Masked wordcloud
================
Using a mask you can generate wordclouds in arbitrary shapes.
Reference: https://github.com/amueller/word_cloud
"""

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from worldcloud import WordCloud

def draw_skill_cloud(mask_image, word_counts, store_path):
    alice_mask = np.array(Image.open())

    stopwords = set()
    
    for pos in word_counts:
        
        wc = WordCloud(background_color="white", max_words=2000, mask=alice_mask,
                       stopwords=stopwords)
        # generate word cloud
        wc = wc.generate_from_frequencies(word_counts[pos])
        
        # store to file
        wc.to_file(store_path + str(pos) + ".png")
        
        # show
        plt.title(pos)
        plt.imshow(wc)
        plt.axis("off")


draw_skill_cloud("D:\\Alice.png", word_counts, "D:\\")