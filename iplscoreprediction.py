# -*- coding: utf-8 -*-
"""IPLScorePrediction

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rzEJVfJ-1W43U9KDUhJIxB8cPxOe-utW
"""

import pandas as pd
df=pd.read_csv("ipl.csv")
df.head()

df['venue'].value_counts()

df['batsman'].value_counts()

df.columns

df['bat_team'].value_counts()

ActiveTeams=['Kolkata Knight Riders', 'Chennai Super Kings', 'Rajasthan Royals',
                    'Mumbai Indians', 'Kings XI Punjab', 'Royal Challengers Bangalore',
                    'Delhi Daredevils', 'Sunrisers Hyderabad']

df=df[(df['bat_team'].isin (ActiveTeams)) & (df['bowl_team'].isin (ActiveTeams))]
df.head()

df['bat_team'].value_counts()

df=pd.get_dummies(df,columns=['bat_team','bowl_team'])
df.head()

df.drop(['striker','non-striker','mid'],axis=1,inplace=True)

df=df[df['overs']>5.0]

df.head()

df.columns

final_df=df[['date','bat_team_Chennai Super Kings', 'bat_team_Delhi Daredevils', 'bat_team_Kings XI Punjab',
              'bat_team_Kolkata Knight Riders', 'bat_team_Mumbai Indians', 'bat_team_Rajasthan Royals',
              'bat_team_Royal Challengers Bangalore', 'bat_team_Sunrisers Hyderabad',
              'bowl_team_Chennai Super Kings', 'bowl_team_Delhi Daredevils', 'bowl_team_Kings XI Punjab',
              'bowl_team_Kolkata Knight Riders', 'bowl_team_Mumbai Indians', 'bowl_team_Rajasthan Royals',
              'bowl_team_Royal Challengers Bangalore', 'bowl_team_Sunrisers Hyderabad',
              'overs', 'runs', 'wickets', 'runs_last_5', 'wickets_last_5', 'total']]

final_df.head()

from datetime import datetime
final_df['date']=final_df['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))

df=pd.get_dummies(df,columns=['venue'], drop_first=True)
df.head()

from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')
stopwords=set(stopwords.words('english'))

df['comb'] = df['batsman'] + ' ' + df['bowler']
df.drop(columns=['batsman','bowler'],axis=1, inplace=True)
df['comb'] = df['comb'].str.lower()
df.head()

from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
from tqdm.auto import tqdm
import numpy as np

comb = list(df['comb'])
tfidf = TfidfVectorizer(lowercase=False, )
X=tfidf.fit_transform(comb)
print(X.shape)
# dict key:word and value:tf-idf score
word2tfidf = dict(zip(tfidf.get_feature_names(), tfidf.idf_))
print(word2tfidf)
nlp = spacy.load('en_core_web_sm')

vecs1 = []

for i in tqdm(list(df['comb'])):
    combdata = nlp(i) 
    # 384 is the number of dimensions of vectors 
    mean_vec1 = np.zeros([len(comb), len(combdata[0].vector)])
    for word1 in combdata:
        # word2vec
        vec1 = word1.vector
        # fetch df score
        try:
            idf = word2tfidf[str(word1)]
        except:
            idf = 0
        # compute final vec
        mean_vec1 += vec1 * idf
    mean_vec1 = mean_vec1.mean(axis=0)
    vecs1.append(mean_vec1)
df['comb_feats_m'] = list(vecs1)

df.head()

df1=df.drop(['comb'],axis=1)
df2=pd.DataFrame(df1.comb_feats_m.tolist(),index=df1.index)

df2.head()



df3=pd.concat([df1,df2],axis=1)
df3.drop(['comb_feats_m'],axis=1)
df3.head()
df3.shape

df3.columns

X_train = final_df.drop(labels='total', axis=1)[final_df['date'].dt.year <= 2016]
X_test = final_df.drop(labels='total', axis=1)[final_df['date'].dt.year >= 2017]

y_train = final_df[final_df['date'].dt.year <= 2016]['total'].values
y_test = final_df[final_df['date'].dt.year >= 2017]['total'].values

X_train.drop(labels='date', axis=True, inplace=True)
X_test.drop(labels='date', axis=True, inplace=True)



from sklearn.linear_model import LinearRegression
regressor = LinearRegression()
regressor.fit(X_train,y_train)

y_predreg=regressor.predict(X_test)

from sklearn import metrics
import numpy as np
print('MAE:', metrics.mean_absolute_error(y_test, y_predreg))
print('MSE:', metrics.mean_squared_error(y_test, y_predreg))
print('RMSE:', np.sqrt(metrics.mean_squared_error(y_test, y_predreg)))

from sklearn import svm

regr=svm.SVR(kernel='rbf')
regr.fit(X_train,y_train)

y_pred=regr.predict(X_test)

print('MAE:', metrics.mean_absolute_error(y_test, y_pred))
print('MSE:', metrics.mean_squared_error(y_test, y_pred))
print('RMSE:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))

from sklearn.linear_model import Lasso
from sklearn.model_selection import GridSearchCV

lasso=Lasso()
parameters={'alpha':[1e-15,1e-10,1e-8,1e-3,1e-2,1,5,10,20,30,35,40]}
lasso_regressor=GridSearchCV(lasso,parameters,scoring='neg_mean_squared_error',cv=5)

lasso_regressor.fit(X_train,y_train)
print(lasso_regressor.best_params_)
print(lasso_regressor.best_score_)

pred_lasso=lasso_regressor.predict(X_test)

print('MAE:', metrics.mean_absolute_error(y_test, pred_lasso))
print('MSE:', metrics.mean_squared_error(y_test, pred_lasso))
print('RMSE:', np.sqrt(metrics.mean_squared_error(y_test, pred_lasso)))

import pickle
filename = 'IPLScorePrediction.pkl'
pickle.dump(lasso_regressor, open(filename, 'wb'))

IPLScorePredictionPickle=pickle.load(open('IPLScorePrediction.pkl','rb'))
predictions_score=IPLScorePredictionPickle.predict(X_test)
metrics.r2_score(y_test, pred_lasso)

df_match=pd.read_csv('matches.csv')
df_match.head()

df_win=df_match['team1']+ df_match['team2']
df_win.head()

subsetDataFrame = df_match[df_match['team1'] == df_match['winner']]
subsetDataFrame['winner']=1
subsetDataFrame.head()

subsetDataFrame2 = df_match[df_match['team2'] == df_match['winner']]
subsetDataFrame2['winner']=0

subsetDataFrame2.head()

df_concat = pd.concat([subsetDataFrame, subsetDataFrame2], axis=0)
df_concat.head()

df_concat.tail()

df_winner=df_concat['winner']
df_winner.head()
df_team2=df_match['team2']
df_team1=df_match['team1']

df_win=pd.concat([df_team1,df_team2,df_winner], axis=1)
df_win.head()

ActiveTeams=['Kolkata Knight Riders', 'Chennai Super Kings', 'Rajasthan Royals',
                    'Mumbai Indians', 'Kings XI Punjab', 'Royal Challengers Bangalore',
                    'Delhi Daredevils', 'Sunrisers Hyderabad']

df_win=df_win[(df_win['team1'].isin (ActiveTeams)) & (df_win['team2'].isin (ActiveTeams))]
df_win.head()

df_win=pd.get_dummies(df_win,columns=['team1','team2'])

df_win.head()

df_win.columns

final_df_win=df_win[['team1_Chennai Super Kings', 'team1_Delhi Daredevils',
       'team1_Kings XI Punjab', 'team1_Kolkata Knight Riders',
       'team1_Mumbai Indians', 'team1_Rajasthan Royals',
       'team1_Royal Challengers Bangalore', 'team1_Sunrisers Hyderabad',
       'team2_Chennai Super Kings', 'team2_Delhi Daredevils',
       'team2_Kings XI Punjab', 'team2_Kolkata Knight Riders',
       'team2_Mumbai Indians', 'team2_Rajasthan Royals',
       'team2_Royal Challengers Bangalore', 'team2_Sunrisers Hyderabad', 'winner']]
final_df_win.head()

final_df_win.isnull().sum()

final_df_win.dropna(inplace=True)

final_df_win.isnull().sum()

X=final_df_win.iloc[:,:-1]
y=final_df_win.iloc[:,-1]
X.head()

from sklearn.model_selection import train_test_split

train_x,test_x,train_y,test_y=train_test_split(X,y,test_size=0.3,random_state=0)

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV

tuned_param=[{'C':[10^-4,10^-2,10^0,10^2,10^4]}]
model=GridSearchCV(LogisticRegression(),tuned_param,scoring='f1',cv=5)

model.fit(train_x,train_y)

print(model.best_estimator_)
print(model.best_params_)

y_prediction=model.predict(test_x)

from sklearn import metrics
print('MAE:', metrics.mean_absolute_error(test_y, y_prediction))
print('MSE:', metrics.mean_squared_error(test_y, y_prediction))

import pickle

pickle.dump(Logreg,open('WinnerPrediction.pkl','wb'))

WinnerPredictionPickle=pickle.load(open('WinnerPrediction.pkl','rb'))
predictions=WinnerPredictionPickle.predict(test_x)
metrics.r2_score(test_y, predictions)