import csv
import pandas as pd

writer = csv.writer(open('data_imputed_binned.csv', 'w'))
data_1 = pd.read_csv('music_data_imputed.csv', encoding='utf-8')

raw = data_1.iloc[:,:].values
happy = ['Romantic','Energizing','Sensual','Empowering','Upbeat','Excited','Sophisticated']
sad = ['Brooding','Yearning','Somber','Melancholy','Serious','Stirring']
angry = ['Aggressive','Gritty','Urgent','Defiant','Rowdy','Fiery']
peaceful = ['Peaceful','Sentimental','Tender','Cool','Sensual','Other']

for r in raw:
    pr = True
    for val in r:
        if(val == None or val == 'remove'):
            pr = False

    # if any value NULL, don't bother printing
    if(pr):
        if(r[-1] in happy):
            r[-1] = 'happy'
        elif(r[-1] in sad):
            r[-1] = 'sad'
        elif(r[-1] in angry):
            r[-1] = 'angry'
        elif(r[-1] in peaceful):
            r[-1] = 'peaceful'
        writer.writerow(r)
