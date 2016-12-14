import gensim
import re
from data_process import process

def get_positions():
    position_dic, position_counter, top_person, positions_set, frame = process()
    model=gensim.models.Word2Vec.load('output_word.model')
    new_positions_dict = {}
    model=gensim.models.Word2Vec.load('output_word.model')
    category_list = ['software','product', 'consultant','analyst', 'accounting','manufacturing','sports','banking','fundraiser','fashion','information',
                     'operation', 'market', 'reporter', 'sales', 'finance', 'hr', 'public','technology','business']
    count = 0
    for word in positions_set:
        old_word = word
        new_position = ''
        word = re.sub('[^0-9a-zA-Z]+', ' ', word)
        word_ist = word.split()
        max_similarity = 0
        for i in word_ist:
            for j in category_list:
                simi = 0
                try:
                    simi = model.similarity(i.lower(), j)
                except:

                    continue
                if simi >= max_similarity:
                    max_similarity = simi
                    new_position = j
        if new_position not in category_list:
            new_position = 'other'
            count += 1
        new_positions_dict[old_word] = new_position
    # print count
    print new_positions_dict

    return new_positions_dict

get_positions()
