# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 15:56:57 2016

@author: mengyaoz
"""

import pandas as pd
import numpy as np
import scipy.sparse as sp
import sklearn
import sklearn.svm
from collections import Counter

def read_skill_and_position(df):
    df = df.dropna(subset=['positions', 'skills', 'endorsements'])
    position_dic = {}
    positions_total = []
    top_skill_num = 0
    
    for index, row in df.iterrows():
        positions = row['positions'][:-1].split(",")
        skills = row['skills'][:-1].split(",")
        skills = [skill.lower() for skill in skills if skill]
        if len(skills) > top_skill_num:
            top_person = index
            top_skill_num = len(skills)
        positions_total.extend(positions)
        for position in positions:
            if position_dic.has_key(position):
                position_dic[position.strip()] += Counter(skills)
            else:
                position_dic[position.strip()] = Counter(skills)
    position_counter = Counter(positions_total)
    return position_dic, position_counter, top_person
        

class SkillModel:
    
    '''Initialize skill with training data'''
    def __init__(self, df):
        df = df.dropna(subset=['positions', 'skills', 'endorsements'])
        all_skills = set()
        all_positions = set()
        all_skills_list = []
        all_positions_list = []
        i = 0
        for index, row in df.iterrows():
            if row['skills'] and row['endorsements']:
                i += 1
                skills = row['skills'][:-1].lower().split(",")
                skills = [skill for skill in skills if skill != '']
                positions = row['positions'].lower().split(",") 
                positions = [position for position in positions if position != '']        
                all_skills |= set(skills)
                all_positions |= set(positions)
                all_skills_list.extend(list(set(skills)))
                all_positions_list.extend(list(set(positions)))

        all_skills = list(all_skills)
        self.all_skills = all_skills
        
        skill_counts = Counter(all_skills_list)
        idf = np.array([skill_counts[skill] for skill in all_skills])        
        idf = np.log(i * 1.0/idf)
        
        self.idf = idf
        
        all_positions = list(all_positions)
        self.position_counts = Counter(all_positions_list)
        self.all_positions = all_positions         
      
    '''Skill and endorsement list to se-ipf matrix'''
    def skill_tfidf(self, df, idf = True):
        df = df.dropna(subset=['positions', 'skills', 'endorsements'])
        skill_bag = []
        not_in = []
        for index, row in df.iterrows():
            if row['skills'] and row['endorsements']:             
                skills = row['skills'][:-1].lower().split(",")
                endorsements = row['endorsements'][:-1].split(",")
                skill_endor = []
                
                for i in range(np.min([len(skills),len(endorsements)])):                  
                    if skills[i] != '' and skills[i] in self.all_skills:
                        if(endorsements[i] == '99+'):
                            skill_endor.append((skills[i], 100))
                        else:
                            skill_endor.append((skills[i], int(endorsements[i])))
                    if skills[i] != '' and skills[i] not in self.all_skills:   
                        not_in.append(skills[i])
                        
                skill_bag.append(skill_endor)
            else:
                print row
                
        rows = []
        cols = []
        data = []
        i = 0
        for skill_endors in skill_bag:
            skills = [skill for skill, endor in skill_endors]
            endorses = [endor for skill, endor in skill_endors]
            col = [self.all_skills.index(skill) for skill in skills]
            row = np.ones(len(col)) * i
            rows.extend(row)
            cols.extend(col)
            data.extend(endorses)
            i += 1
            
        tfidf = sp.coo_matrix((data,(rows,cols)),shape=(i,len(self.all_skills)))  

        n = len(self.all_skills)
        if idf:
            tfidf = tfidf * sp.spdiags(self.idf, 0, n, n)        
        return tfidf, self.all_skills, not_in        
        pass
    
    '''Position list to label index'''
    def get_label(self, df):
        df = df.dropna(subset=['positions', 'skills', 'endorsements'])
        labels = []
        for index, row in df.iterrows():
            positions = row['positions'][:-1].lower().split(",") 
            positions = [position for position in positions if position != '']
            labels.append([self.all_positions.index(pos) for pos in positions])
          
        return labels, self.all_positions
       
    '''Position list to ad-hoc label'''
    def get_label_hot(self, df):
        df = df.dropna(subset=['positions', 'skills', 'endorsements'])
        
        rows = []
        cols = []
        data = []
        i = 0
        for index, row in df.iterrows():
            positions = row['positions'].lower().split(",") 
            positions = [position for position in positions if position != '']
            positions = set(positions)
            col = [self.all_positions.index(pos) for pos in positions]
            row = np.ones(len(col)) * i
            d = np.ones(len(col))
            rows.extend(row)
            cols.extend(col)
            data.extend(d)
            i += 1            
            
        labels = sp.coo_matrix((data,(rows,cols)),shape=(i,len(self.all_positions))) 
        return labels.astype('int'), self.all_positions
    
    '''Matrix that replicat input skills for each positions so that each input has only one label'''
    def skill_tfidf_single_label(self, df):
        df = df.dropna(subset=['positions', 'skills', 'endorsements'])
        skill_position_bag = []
        all_skills = set()
        all_positions = set()
        
        for index, row in df.iterrows():
            if row['skills'] and row['endorsements']:             
                skills = row['skills'][:-1].lower().split(",")
                endorsements = row['endorsements'][:-1].split(",")
                positions = row['positions'][:-1].lower().split(",") 
                positions = [position for position in positions if position != '']
                all_positions |= set(positions)
                all_skills |= set(skills)
                skill_endor = []
                for i in range(np.min([len(skills),len(endorsements)])):
                    if skills[i] != '':
                        if(i >= len(endorsements)):
                            print i, len(endorsements), row, range(np.min([len(skills),len(endorsements)]))
                        if(endorsements[i] == '99+'):
                            skill_endor.append((skills[i], 100))
                        else:
                            skill_endor.append((skills[i], int(endorsements[i])))
                skill_position_bag.append((skill_endor, positions))
                
            else:
                print row
                
        all_skills.remove('')
        all_skills = list(all_skills)
        all_positions = list(all_positions)
        idf = np.zeros(len(all_skills))
        rows = []
        cols = []
        data = []
        labels = []
        i = 0
        for skill_endors, positions in skill_position_bag:
            skills = [skill for skill, endor in skill_endors]
            endorses = [endor for skill, endor in skill_endors]
            col = [all_skills.index(skill) for skill in skills]
            ################## Replicate for Multiple Positions ? Make sense ? #######################
            for position in positions:
                row = np.ones(len(col)) * i
                idf[col] += 1
                rows.extend(row)
                cols.extend(col)
                data.extend(endorses)
                labels.append(all_positions.index(position))
                i += 1
            
        tfidf = sp.coo_matrix((data,(rows,cols)),shape=(i,len(all_skills)))  
        idf = np.log(i * 1.0/idf)
        
        n = len(idf)
        tfidf = tfidf * sp.spdiags(idf, 0, n, n)        
        return tfidf, labels, all_skills, all_positions
    
'''Self-defined naive bayes model (still to be modified)'''
class MNaiveBayes:
    def __init__(self, X, y):

        self.X = X
        self.y = y
        #self.reg = reg
        self.p = np.zeros([X.shape[1], y.shape[1]])
    
    def train(self, alpha = 1, niters=100, learning_rate=1, verbose=False):
        
        #k = self.y.shape[1]
        word_counts = self.X.transpose().dot(self.y)
        print word_counts.todense()
        word_counts_temp = word_counts
        
        word_counts_temp.data = word_counts.data + alpha
        #print self.X.todense()
        ones = sp.coo_matrix(np.ones(self.X.shape[1]),shape=(1,self.X.shape[1]))
        all_word_counts = np.log(ones.dot(word_counts_temp).toarray()[0] + alpha)
        #r_all_word_counts = 1.0 / (all_word_counts.todense() + alpha)        
        word_counts = np.log(word_counts.todense() + alpha)
        self.p = word_counts - all_word_counts

        pass
            
    
    def predict(self, X):
        y_pred = []
        for x in X:
            ps = np.asarray(x.dot(self.p))[0]
            ps[ps==0] = -float('inf')
            #print ps
            ind = np.argpartition(ps, -5)[-5:]
            p = ps[ind] #/ sum(ps)
            y_pred.append(zip(ind,p))
        return ps, y_pred
        pass

'''Generate word frequency for word cloud based on conditional probabilities'''   
def generate_text(model, skills, positions):
    estimators = model.estimators_
    top_number = 200
    word_counts = {}
    est_idx = 0
    for estimator in estimators:
        
        prob = estimator.feature_log_prob_[1]
        #prob = estimator.coef_
        ind = np.argpartition(-prob, top_number)[:top_number]
        top_prob = prob[ind]      
        min_top_prob = np.min(top_prob)
        top_prob = top_prob - min_top_prob
        top_prob = np.exp(top_prob);
        word_counts[positions[est_idx]] = []
        for i in range(top_number):
            word_counts[positions[est_idx]].append((skills[ind[i]],int(top_prob[i] * 1000)))
            
        est_idx += 1
    return word_counts    
    

'''main'''
df_full = pd.read_csv("clean_positions_2.csv").dropna(subset=['positions', 'skills', 'endorsements'])
print "finish loading"
P = np.random.permutation(len(df_full))
n = len(P) / 10 * 8
df_train2 = df_full.ix[P[:n]]
df_test2 = df_full.ix[P[n:]]
sm3 = SkillModel(df_train2)
tf3, all_s3, not_in2 = sm3.skill_tfidf(df_train2)
labels3, all_p3 = sm3.get_label_hot(df_train2)
tf_test3, all_s_t3, not_in3 = sm3.skill_tfidf(df_test2)
labels_test3, all_p_t3 = sm3.get_label_hot(df_test2)
print "finish model"

import time
from sklearn.multiclass import OneVsRestClassifier as OC
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import OrthogonalMatchingPursuit
from sklearn.metrics import classification_report

start = time.time()
oc3 = OC(MultinomialNB())
#oc3 = OC(SVC(kernel='linear', probability=True))
oc3.fit(tf3, labels3)
end = time.time()
print "Train in {} seconds".format(end - start)
y_pred = oc3.predict(tf_test3)
report_nb = classification_report(labels_test3, y_pred)

print report_nb
import pickle
with open('classifier_nb_tf.pkl', 'wb') as output:
    pickle.dump(oc3, output, pickle.HIGHEST_PROTOCOL)
with open('model_nb_tf.pkl', 'wb') as output:
    pickle.dump(sm3, output, pickle.HIGHEST_PROTOCOL)

word_counts = generate_text(oc3, all_s3, all_p3)

'''Simple prediction test'''
my_test = pd.DataFrame()
my_test['skills'] = ['java,python,programming,visual studio,']
my_test['endorsements'] = ['1,1,1,1,']
my_test['positions'] = ['']
my_tf, all_s_t2, not_in_my = sm3.skill_tfidf(my_test)
my_labels, all_p_t2 = sm3.get_label_hot(my_test)
my_pred = oc3.predict(my_tf)

