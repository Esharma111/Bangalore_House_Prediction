# -*- coding: utf-8 -*-
"""HOUSE_PREDICTION_FINAL.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YLcQiclRTKw8cqIZAl8eNC7I8HnUMlq7

Import Libraries
"""

# Commented out IPython magic to ensure Python compatibility.
#Import Libraries
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
# %matplotlib inline
import matplotlib
matplotlib.rcParams["figure.figsize"]=(20,10)

#Load dataset
df1=pd.read_csv("/content/Bengaluru_House_Data (1).csv")

df1.head(6) #Returns first 6 rows , default is 5 when no number is given

df1.shape # returns rows and columns

df1.groupby('area_type')['area_type'].agg('count') #count all objects of same area type

df2=df1.drop(['area_type','society','balcony','availability'],axis='columns')
df2.head()

df2.isnull().sum() #gives which columns have NA values with count , then we will drop those rows if they are small in number compared to the entire size of dataset

df3=df2.dropna()
df3.isnull().sum() # we could also replace na values with median values instead of dropping

"""Columns Dropped"""

df3['size'].unique() #we need to write in one format , either bhk or bedroom so we use create a new column

df3['bhk']=df3['size'].apply(lambda x: int(x.split(' ')[0]))

df3.head()

df3['bhk'].unique()

df3[df3.bhk>20] #no. of bedrooms as 43 was strange , so we'll check

"""There is something weird , a 43 bedroom flat can not have 2400 sq ft. area ,we will correct late"""

df3.total_sqft.unique()

#we see there is a range and we need numbers

def is_float(x):
    try:
        float(x)
    except:
        return False
    return True

df3[~df3['total_sqft'].apply(is_float)].head(10)

"""In 410 , the format is not correct , so we can ignore these rows or do unit conversion"""

def convert_sqft_to_num(x):
    tokens=x.split('-')
    if len(tokens)==2:
        return (float(tokens[0])+float(tokens[1]))/2
    try:
        return float(x)
    except:
        return None

convert_sqft_to_num('2166')

convert_sqft_to_num('34.46Sq. Meter')

# Didn't return anything which is what we want

df4=df3.copy()
df4['total_sqft']=df4['total_sqft'].apply(convert_sqft_to_num)

df4.head()

df4.loc[30]

(2100+2850)/2 #so correct

# By now , handled NAN and cleaned sqft column and also removed some unnecessary features
# Now , we learn feature engineering techniques

df5=df4.copy()
df5['price_per_sqft']=df5['price']*100000/df5['total_sqft'] #price is an importamt feature in real estate
df5.head()

len(df5.location.unique())

# Too many columns , dimensionality curse

df5.location=df5.location.apply(lambda x:x.strip()) #removes extra white spaces
location_stats = df5.groupby('location')['location'].agg('count').sort_values(ascending=False)
location_stats

#the distribution is very uneven

len(location_stats[location_stats<=10]) #to find a threshold

#Since 1052 is a big number , we create a new column

location_stats_less_than_10 = location_stats[location_stats<=10]

location_stats_less_than_10

df5.location = df5.location.apply(lambda x:'other' if x in location_stats_less_than_10 else x)
len(df5.location.unique())

df5.head(10) #notice 10th row

df5[df5.total_sqft/df5.bhk<300].head() #average 1 bhk size is 300 so , the following data is unsual

"""We found some price outliers using price column"""

df6 = df5[~(df5.total_sqft/df5.bhk<300)]
df6.shape

df6.price_per_sqft.describe()

"""We found some more outliers"""

def remove_pps_outliers(df):
    df_out = pd.DataFrame()
    for key , subdf in df.groupby('location'):
        m = np.mean(subdf.price_per_sqft)
        st= np.std(subdf.price_per_sqft)
        reduced_df = subdf[(subdf.price_per_sqft > (m-st)) & (subdf.price_per_sqft <= (m+st))]
        df_out = pd.concat([df_out , reduced_df],ignore_index = True)
    return df_out
df7=remove_pps_outliers(df6)
df7.shape

"""We removed close to 2000 outliers"""

def plot_scatter_chart(df,location):
    bhk2 = df[(df.location == location) & (df.bhk==2)]
    bhk3 = df[(df.location == location) & (df.bhk==3)]
    matplotlib.rcParams['figure.figsize']=(15,10)
    plt.scatter(bhk2.total_sqft,bhk2.price,color = 'blue' , label = '2 BHK', s=50)
    plt.scatter(bhk3.total_sqft,bhk3.price,marker = '+',color = 'green' , label = '3 BHK', s=50)
    plt.xlabel("Total Square Feet Area")
    plt.xlabel("Price Per Square Feet")
    plt.title(location)
    plt.legend()

plot_scatter_chart(df7,"Hebbal")

"""Now we can remove those 2 BHK apartments whose price_per_sqft is less than the mean price_per_sqft of 1 BHK apartment"""

def remove_bhk_outliers(df):
    exclude_indices = np.array([])
    for location , location_df in df.groupby('location'):
        bhk_stats = {}
        for bhk , bhk_df in location_df.groupby('bhk'):
            bhk_stats[bhk] = {
                'mean': np.mean(bhk_df.price_per_sqft),
                'std' : np.std(bhk_df.price_per_sqft),
                'count' : bhk_df.shape[0]
            }
        for bhk,bhk_df in location_df.groupby('bhk'):
            stats = bhk_stats.get(bhk-1)
            if stats and stats['count']>5:
                exclude_indices = np.append(exclude_indices , bhk_df[bhk_df.price_per_sqft < (stats['mean'])].index.values)
    return df.drop(exclude_indices,axis = 'index')

df8 = remove_bhk_outliers(df7)
df8.shape #more data points removed

plot_scatter_chart(df7,"Hebbal")

"""Abnormalities are still present but less in number"""

matplotlib.rcParams["figure.figsize"] = (20,10)
plt.hist(df8.price_per_sqft, rwidth = 0.8)
plt.xlabel("Price Per Square Feet")
plt.ylabel("Count")

"""Now , let's explore the bathroom features"""

df8.bath.unique()

df8[df8.bath>10]

"""Criteria of removing number of bathroom outliers as set by the manager : if no. of bathrooms are more than the no. of bedrooms , then remove it .

"""

plt.hist(df8.bath , rwidth = 0.8)
plt.xlabel("Number of bathrooms")
plt.ylabel("Count")

df8[df8.bath>df8.bhk+2]

df9 = df8[df8.bath<df8.bhk+2]
df9.shape

"""Outlier Detection And Removal is Complete , Now we prepare our data for machine learning (4 finished)"""

df10 = df9.drop(['size','price_per_sqft'],axis = 'columns')

df10.head(3)

"""ML can't interpret text data , so we convert into numeric data using one hot encoding

"""

dummies = pd.get_dummies(df10.location)
dummies.head(3)

df11= pd.concat([df10,dummies.drop('other',axis = 'columns')],axis='columns')
df11.head(3)

df12 = df11.drop('location',axis = 'columns')
df12.head(2)

df12.shape

X = df12.drop('price',axis = 'columns')
X.head()

y=df12.price
y.head()

from sklearn.model_selection import train_test_split
X_train , X_test,y_train,y_test = train_test_split(X,y,test_size=0.2,random_state = 10)

from sklearn.linear_model import LinearRegression
lr_clf = LinearRegression()
lr_clf.fit(X_train,y_train)
lr_clf.score(X_test,y_test)

"""84% is a decent score"""

from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import cross_val_score
cv = ShuffleSplit(n_splits = 5,test_size = 0.2 , random_state = 0 ) #5 fold cross validaton
cross_val_score(LinearRegression(),X,y,cv=cv)
cross_val_score

#read about k4 corss validation . Here the score is near to 80% always , so it's decent

#We don't know if this regression technique is the best to apply here , so we capply others to see which one works best

from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import Lasso
from sklearn.tree import DecisionTreeRegressor

def find_bestmodel_using_gridsearchcv(X,y):
    algos = {'linear_regression' :
             {'model' : LinearRegression() , 'params' :{
                'fit_intercept': [True, False],
                'copy_X': [True, False],
                'positive': [True, False],
                'n_jobs': [-1]
            }} ,
             'lasso':
            {'model':Lasso(),'params':{'alpha':[1,2] , 'selection' : ['random','cyclic'] }} ,
            'decision_tree':
            {'model':DecisionTreeRegressor(),'params':
                            {'criterion':['friedman_mse','poisson'] , 'splitter' : ['best','random'] }}
            }
    scores=[]
    cv = ShuffleSplit(n_splits = 5 , test_size = 0.2 , random_state = 0)
    for algo_name , config in algos.items():
        gs = GridSearchCV(config['model'],config['params'],cv =cv, return_train_score = False)
        gs.fit(X,y)
        scores.append({'model':algo_name,'best_score':gs.best_score_ ,'best_params':gs.best_params_  })

    return pd.DataFrame(scores,columns = ['model','best_score','best_params'])

find_bestmodel_using_gridsearchcv(X,y)

X.columns

def predict_price(location,sqft,bath,bhk):
    loc_index = np.where(X.columns == location)[0][0]

    x= np.zeros(len(X.columns))
    x[0] = sqft
    x[1] = bath
    x[2] = bhk
    if loc_index >=0:
        x[loc_index] = 1
    return lr_clf.predict([x])[0]

np.where(X.columns=='2nd Phase Judicial Layout')[0][0]

predict_price('1st Phase JP Nagar',1000,2,2)

predict_price('1st Phase JP Nagar',1000,3,3) ##something is not right ,less bathrooms and price is more but it could be that this one has more space

predict_price('2nd Stage Nagarbhavi',1000,2,2)

predict_price('2nd Stage Nagarbhavi',10000,3,2)

predict_price('Indira Nagar',1000,2,2)

predict_price('Indira Nagar',1000,3,3)