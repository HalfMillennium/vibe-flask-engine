import csv
import pandas as pd

writer = csv.writer(open('xgb_imputed_semi_bin.csv', 'w'))
data_1 = pd.read_csv('audio_mood_class_xgboost.csv', encoding='utf-8')
raw = data_1.iloc[:,:].values
count = 0
writer.writerow(['artist','title','energy','liveness','tempo','speechiness','acousticness','instrumentalness','time_signature','danceability','key', 'duration_ms','loudness','valence','mode','genre_1','genre_2','genre_3','mood_1'])

sad = ['Brooding', 'Melancholy', 'Somber']
energetic = ['Energizing', 'Upbeat', 'Lively', 'Rowdy', 'Fiery', 'Empowering', 'Urgent']

for r in raw:
    pr = True
    for val in r:
        if not val or val == "nan":
            pr = False
            count = count + 1
            continue

    # if any value NULL, don't bother printing
    if(pr):
        if(r[-1] in sad):
            r[-1] = 'Sad'
        elif(r[-1] in energetic):
            r[-1] = 'Energetic'
        writer.writerow(r)

print("File writing: Success.\n")
print("Raw length:",count)