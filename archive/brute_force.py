#GRIDSEARCH
import itertools

def get_unique_widths(array):
    '''Takes array of numbers, returns sorted list of unique values'''
    return(np.sort(array.unique()))

#Get unique skus
sku = pd.DataFrame({'Size': get_unique_widths(dat_23['std_width_mm'])})

#Number of Sizes in the dataset
length_sku = sku.size

#Create an initial combination of n-1 sizes. 
#TODO-1: Need to add a for loop to create n-1 to 1 combinations of sizes. Right now, just did it for Length(SKU)-1
iter_df = pd.DataFrame(data =list(itertools.combinations(sku['Size'], length_sku-1)))

#Create combination of sizes with n-1 SKUs
sku['key'] = 1
iter_df['key'] = 1
df = pd.merge(sku,iter_df,on='key').drop('key',axis=1)
sku = sku.drop('key', axis=1)

#Reset name of the columns
df.columns = sku['Size'] #sku.T.values.tolist()

#Create a dataframe with all the permutations of the sizes
import time
start = time.time()
df3 = pd.DataFrame()
for index,row in df.iterrows():
    df2 = pd.DataFrame(list(itertools.permutations(list(df.iloc[index]))))
    df3 = pd.concat([df3, df2], axis=0)
time.time() - start

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