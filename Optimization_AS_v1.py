# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 21:00:50 2019

@author: SinghA19
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 15:43:12 2019

@author: SinghA19
"""
import pandas as pd
import itertools
stdSKU = [
      ['50',2000],
      ['100', 1000],
      ['180', 2500],
      ['230', 4000],
      ['350', 500],
      ['460', 4000],
      ['500', 4000]]
# Create a DF to store the Sizes
sku = pd.DataFrame(pd.DataFrame(data=stdSKU)[0])
sku.columns = ['Size']
#Number of Sizes in the dataset
lengthS = sku.size

#Create an initial combination of n-1 sizes. 
#TODO-1: Need to add a for loop to create n-1 to 1 combinations of sizes. Right now, just did it for Length(SKU)-1
iter = pd.DataFrame(data =list(itertools.combinations(sku['Size'], lengthS-1)))

#Create combination of sizes with n-1 SKUs
sku['key'] = 1
iter['key'] = 1
df = pd.merge(sku,iter,on='key').drop('key',axis=1)
sku = sku.drop('key', axis=1)

#Take the transpose of the STD sku sizes
skut = sku.T 
#Reset name of the columns
df.columns = sku.T.values.tolist()

#Create a dataframe with all the permutations of the sizes
df3 = pd.DataFrame()
for index,row in df.iterrows():
    df2 = pd.DataFrame(list(itertools.permutations(list(df.iloc[index]))))
    df3 = pd.concat([df3, df2], axis=0)

#TODO-2: The column names need to be characters. I have hardcoded the names here, but they should ideally 
    #change when the length of the SKU dataframe. 
df3.columns = ['size1','size2','size3','size4','size5','size6','size7']
df3 = df3.apply(pd.to_numeric)
sku = sku.apply(pd.to_numeric)
#Apply constraints on the columns to get the final Dataset
for index,row in sku.iterrows():
    df3 = df3[(df3.iloc[:,index] >= sku.iloc[index,0]) & (df3.iloc[:,index] < sku.iloc[index,0]+100)]

df3 = pd.DataFrame.drop_duplicates(df3)

#TODO-3: Remove the base case scenario from the dataframe 3 where all sizes stay the same as standard sizes
    #Using something like this  df3 = df3[df3 != skut]
    
#TODO-4: Once we have the final df3, multiply corresponding sizes by the target, and then
    #take the sum of the columns to give a waste for each Row. Every row will denote waste for 1 Scenario. 
    #We can then find the Minimum waste by comparing the values. 
    
##------------------------------------------#