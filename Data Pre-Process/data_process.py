import pandas as pd
from collections import Counter
from gensim.models import word2vec
import sklearn.cluster
import distance
import numpy as np
import editdistance
import csv
from itertools import dropwhile


def read_data(path_list):
    list_ = []
    for file_ in path_list:
        df = pd.read_csv(file_,index_col=None, header=0)
        list_.append(df)
    frame = pd.concat(list_)

    # print frame.dtypes
    return frame



def read_skill_and_position(df):
    df = df.dropna(subset=['positions', 'skills'])
    position_dic = {}
    positions_total = []
    top_skill_num = 0

    for index, row in df.iterrows():
        positions = row['positions'][:-1].split(",")
        skills = row['skills'][:-1].split(",")
        skills = [skill.lower() for skill in skills if skill]
        if len(skills) > top_skill_num:
            top_person = index
            # print row
            top_skill_num = len(skills)
            # print index
            # print top_skill_num
        positions_total.extend(positions)
        for position in positions:
            if position_dic.has_key(position):
                position_dic[position.strip()] += Counter(skills)
            else:
                position_dic[position.strip()] = Counter(skills)
    positions_set = set(positions_total)
    position_counter = Counter(positions_total)
    # print "num of positions:", len(set(position_counter))
    # print positions_set
    return position_dic, position_counter, top_person, positions_set


def process():
    path_list = ['dump_profiles_1.csv','dump_profiles_2.csv','dump_profiles_3.csv',
             'dump_profiles_4.csv','dump_profiles_5.csv','dump_profiles_6.csv',
             'dump_profiles_7.csv','dump_profiles_8.csv','dump_profiles_9.csv',
                 'dump_profiles_10.csv','dump_profiles_11.csv','dump_profiles_12.csv',
                 'dump_profiles_13.csv',
             'dump_profiles_14.csv','dump_profiles_15.csv','dump_profiles_16.csv',
             'dump_profiles_17.csv','dump_profiles_18.csv','dump_profiles_19.csv']
    # get dataframe of all data
    frame = read_data(path_list)
    # print "head",frame.head(5)
    # print frame.shape

    position_dic, position_counter, top_person, positions_set= read_skill_and_position(frame)
    popular_words = sorted(position_counter, key = position_counter.get, reverse = True)
    df = pd.DataFrame(popular_words, columns=["positions"])
    df.to_csv('positions.csv', index=False)



    top_10 = popular_words[:100]
    # print top_10
    all_skills =[]
    for key, skills in position_dic.items():
        all_skills.extend(skills)
    all_skills = Counter(all_skills)
    skills_set = set(all_skills)

    # print len(set(all_skills))
    top_skills = sorted(all_skills, key = all_skills.get, reverse = True)
    # print top_skills
    # print len(skills_set)
    #
    # print top_skills[:100]
    # print position_dic, position_counter, top_person, positions_set
    # print frame.head()

    return position_dic, position_counter, top_person, positions_set, frame


process()




# if __name__ == "__main__":
#     main()
#

