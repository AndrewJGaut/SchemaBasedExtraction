#!/usr/bin/env python
# coding: utf-8

# In[1]:


import xlrd

hypernyms = xlrd.open_workbook('hypernyms_dataset.xlsx')
HypM = hypernyms.sheet_by_index(0)
HypF = hypernyms.sheet_by_index(1)

negatives = xlrd.open_workbook('negatives_dataset.xls')
NegM = negatives.sheet_by_index(0)
NegF = negatives.sheet_by_index(1)


# In[2]:


print('hypernym male rows: ', HypM.nrows)
print('hypernym female rows: ', HypF.nrows)


# In[3]:


print('negative male rows: ', NegM.nrows)
print('negative female rows: ', NegF.nrows)


# In[4]:


# number of male hypernym sentences

hypM = 0

for row in range(1, HypM.nrows):
    first = HypM.cell_value(row, 0)
    if (first != ''):
        continue
    else:
        for i in range(1, 5):
            if (HypM.cell_value(row,i) != ''):
                hypM += 1
                
print("total # of sentences in hypernym male dataset: ", hypM)


# In[5]:


# number of female hypernym sentences

hypF = 0

for row in range(1, HypF.nrows):
    first = HypF.cell_value(row, 0)
    if (first != ''):
        continue
    else:
        for i in range(1, 5):
            if (HypF.cell_value(row,i) != ''):
                hypF += 1
                
print("total # of sentences in hypernym female dataset: ", hypF)


# In[6]:


# number of male negative sentences

negM = 0

for row in range(1, NegM.nrows):
    first = NegM.cell_value(row, 0)
    if (first != ''):
        continue
    else:
        if (NegM.cell_value(row,1) != ''):
            negM += 1
                
print("total # of sentences in negative male dataset: ", negM)


# In[7]:


# number of female negative sentences

negF = 0

for row in range(1, NegF.nrows):
    first = NegF.cell_value(row, 0)
    if (first != ''):
        continue
    else:
        if (NegF.cell_value(row,1) != ''):
            negF += 1
                
print("total # of sentences in negative female dataset: ", negF)


# In[8]:


totalSentences = hypM + hypF + negM + negF

print('total # of sentences', totalSentences)

print('\nusing train-dev-test split of .80-.10-.10')
print('train: ~',0.8*totalSentences)
print('development: ~',0.1*totalSentences)
print('test: ~',0.1*totalSentences)


# In[27]:


# creating dictionary
# key: entity
# value: number of sentences associated w/ that entity

dictHM = dict()
sheet = HypM
entityCount = 0

for row in range(1, sheet.nrows):
    entityCount = 0
    entity = sheet.cell_value(row, 0)
    if (entity == ''):
        continue
    else:
        index = row + 1
#         print(index)
        while (sheet.cell_value(index, 0) == ''):
            for i in range(1,5):
                if (sheet.cell_value(index, i) != ''):
                    entityCount += 1
            index += 1
        dictHM[entity] = entityCount
        
print(dictHM)




'''
function to split get the dictionary
'''
def split(dataset_path):
    dataset = xlrd.open_workbook(dataset_path)
    sheet = dataset.sheet_by_index(0)

    dictHM = dict()
    entityCount = 0

    i = 1
    while i < sheet.nrows:

        # first, get the number of rows until next entity
        curr_row = i + 1
        while (curr_row < sheet.nrows and sheet.cell_value(curr_row, 0) == ""):
            curr_row += 1
        entity_rows = curr_row - i

        # now, get entity name
        e1 = sheet.cell_value(i, 0)
        print("CURR NAME: " + e1)

        # now, get sentence counts for the entity
        prev_i = i
        i += 1
        while (i < prev_i + entity_rows and i < sheet.nrows):
            for j in range(1, sheet.ncols):
                if sheet.cell_value(i, j) != "":
                    if e1 not in dictHM:
                        dictHM[e1] = 1
                    else:
                        dictHM[e1] += 1
            i += 1

    print(dictHM)
