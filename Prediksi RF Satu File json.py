#import pandas as pd
import pickle
#from sklearn.model_selection import train_test_split
#from sklearn.ensemble import RandomForestClassifier
#from sklearn.metrics import accuracy_score
#from sklearn import metrics

import json
#from sklearn.preprocessing import LabelEncoder
from dateutil import parser
from sklearn.preprocessing import LabelEncoder
import pandas as pd
from sklearn.metrics import accuracy_score
import os.path

    
# memasukkan dataset
#data = json.loads("".join(open('Dataset UJICOBA.json').readlines()))
data_asal = json.loads("".join(open('daerah.json').readlines()))

  
# memasukkan dataset
data = json.loads("".join(open('Dataset UJICOBA.json').readlines()))

variable = [
            'created_at',
            'kelas',
            'usia',
            'kelamin',
            'tinggi',
            'berat',
            'jilbab',
            'ac',
            'durasi_ac',
            'durasi_kipas',
            'mata_pelajaran',
            'asal',
            'lama_dijogja',
            'indoor',
            'outdoor',
            'jawaban',
           ]

#Ngedapetin nilai data dari data json (data_awal) dengan cara data['jawab']
data_bersih = [] 
for data_i in data["jawab"]:
    item = []
    for key in variable:
        item.append(data_i[key])
    
    #Cuma ngambil data yang gak None    
    if all(item[:8] + item[10:]):
        data_bersih.append(item)

#Hasil data bersih, nilai per sensor mau dikelompokkin antara indoor dan outdoor

#Data indoor dan outdoor
field=["field%s" %i for i in range(1,7)]

for a in data_bersih:
    data_indoor=a[13]
    #print(data_indoor)
    data_outdoor=a[14]
    
    data_indoor_kelompok=[]
    data_outdoor_kelompok=[]

    #Karena datanya dengan parameter field 1-7, soo
    for b in field:
        data_indoor_kelompok.append(data_indoor[b])
        data_outdoor_kelompok.append(data_outdoor[b])
    
    #Ngeganti elemen data bersih, yang awalnya masih field jadi udah 
    a[13]=data_indoor_kelompok
    a[14]=data_outdoor_kelompok
    
#    
data_dict = []
for a in data_bersih:
    data_single = {}
    for idx, key in enumerate(variable):
        data_single[key] = a[idx]
    
    data_dict.append(data_single)


#Nge ganti nama biar jelas nama sensor apa aja dan jawabannya apa aja, jadi dipecah ga dikelompokkin lagi untuk
#sensor dan juga untuk jawaban
sensor_indoor = ['rh', 'co2', 'ta', 'tg', 'ws', 'li']
sensor_outdoor = ['data1', 'data2', 'data3', 'data4', 'data5', 'data6']
jawab = ['sensasi', 'kepuasan', 'preferensi', 'penerimaan']
# print(data_dict)
for data_dic in data_dict:
    for sensor_name, sensor_value in zip(sensor_indoor, data_dic['indoor']):
        data_dic["in_"+sensor_name] = float(sensor_value)
    for sensor_name, sensor_value in zip(sensor_outdoor, data_dic['outdoor']):
        data_dic["out_"+sensor_name] = float(sensor_value)
    for jawab_name, jawab_value in zip(jawab, data_dic['jawaban']):
        data_dic[jawab_name] = jawab_value
    del data_dic['indoor']
    del data_dic['outdoor']
    del data_dic['jawaban']
    
#Data final yang udah dibersihin dari data kosong dan udah dikonfigurasi ulang
data_final = data_dict


#STEP 2 PRE PROCESSING
# memasukkan data

#data_bersih = json.loads("".join(open('data_bersih.json').readlines()))
data_bersih = data_final
data_asal = json.loads("".join(open('daerah.json').readlines()))

# Encoding data - One Hot Encoding
#Encode untuk ac dan kipas
#3 untuk tidak ac dan tidak kipas
#2 - untuk kipas saja
#1 - untuk ac dan kipas
#0 - untuk ac saja
ac = [variable['ac'] for variable in data_bersih]
ac_kipas = LabelEncoder().fit_transform(ac)

#Encode untuk jenis kelamin
#0 - untuk laki-laki
#1 - untuk perempuan
kelamin = [variable["kelamin"] for variable in data_bersih]
j_kelamin = LabelEncoder().fit_transform(kelamin)

#Encode untuk daerah asal, udah ada data dari daerah.json, antara sejuk atau hangat
#0 - untuk sejuk
#1 - untuk hangat
asal = [variable["asal"] for variable in data_bersih]
daerah = [0 if item == data_asal["sejuk"] else 1 for item in asal]

# Identifikasi
#1 untuk senin - Biru Putih
#2 untuk selasa - Biru Putih
#3 untuk rabu - Batik
#4 untuk kamis - Batik
#5 untuk jumat - Pramuka
#6 untuk sabtu - Pramuka



datetime = [i["created_at"] for i in data_bersih] # clo berdasar hari
no_hari = [parser.parse(i).strftime("%w") for i in datetime]

#Konstanta insulasi termal berdasarkan ASHRAE, liat di data.xlsx
laki = ["0","0.6","0.6","0.54","0.54","0.65","0.65"]
perempuan_tanpajilbab = ["0","0.59","0.59","0.53","0.53","0.64","0.64"]
perempuan_berjilbab = ["0","0.73","0.73","0.64","0.64","0.82","0.82"]

clo = [] # insulasi termal
for h, item in zip(no_hari, data_bersih):
    h = int(h)
    if item['kelamin'] == 'L':
        clo.append(laki[h])
    else:
        if item['jilbab'] == 'ya':
            clo.append(perempuan_berjilbab[h])
        else:
            clo.append(perempuan_tanpajilbab[h])
            
jadwal = [variable["mata_pelajaran"] for variable in data_bersih]
ruang = [pelajaran["ruang"] for pelajaran in jadwal]

df = pd.read_json(json.dumps(data_bersih))
df["kelas"] = ruang
df["kelamin"] = j_kelamin
df["jilbab"] = clo
df["ac"] = ac_kipas
df["asal"] = daerah

# pemisahan kelas
data_R15 = df[df["kelas"] == 'R15']
data_R33 = df[df["kelas"] == 'R33']
data_R40 = df[df["kelas"] == 'R40']

print("jumlah data R15 =", len(data_R15))
print("jumlah data R33 =", len(data_R33))
print("jumlah data R40 =", len(data_R40))

# # simpan data siap pakai
#data_R33.to_csv('r33.csv')
#data_R40.to_csv('r40.csv')

#try:    
    #Kumpulin data
    #Data personal
    
data_prediksi=[data_R15,data_R33,data_R40]
personal = ['usia','kelamin','tinggi','berat','jilbab']
latar_belakang=['ac','durasi_ac','durasi_kipas','asal','lama_dijogja']
sensor_indoor=['in_rh','in_co2','in_ta','in_tg','in_ws','in_li']
sensor_outdoor=['out_data1','out_data2','out_data3','out_data4','out_data5','out_data6']

sensasi = personal+latar_belakang+sensor_indoor+sensor_outdoor
#kenyamanan = personal+
output_akhir_prediksi=[]
no_ruang='0'
model=False
for data_saturuang in data_prediksi:
    #Milih model nya, soalnya beda ruang, beda modell
    if len(data_saturuang)!=0:
        no_ruang=data_saturuang["kelas"].iloc[0]
    
    elif len(data_saturuang)==0:
        print('data kosong')
        
        
    if no_ruang=='R33':
        print('masuk r33')
        model=os.path.exists('r33_model_sensasi.pkl') and os.path.exists('r33_model_kenyamanan.pkl') and os.path.exists('r33_model_kenyamanan.pkl')
        if model==True:
            with open('r33_model_sensasi.pkl', 'rb') as sensasi:
                r33_model_RF_sensasi = pickle.load(sensasi)
                
            with open('r33_model_kenyamanan.pkl', 'rb') as kenyamanan:
                r33_model_RF_kenyamanan = pickle.load(kenyamanan)
            
            with open('r33_model_penerimaan.pkl', 'rb') as penerimaan:
                r33_model_RF_penerimaan = pickle.load(penerimaan)
            model_RF_sensasi=r33_model_RF_sensasi
            model_RF_kenyamanan=r33_model_RF_kenyamanan
            model_RF_penerimaan=r33_model_RF_penerimaan
            
        else:
            pass
        
    
    elif no_ruang=='R15':
        print('masuk r15')
        model=os.path.exists('r15_model_sensasi.pkl') and os.path.exists('r15_model_kenyamanan.pkl') and os.path.exists('r15_model_kenyamanan.pkl')
        if model==True:
            with open('r15_model_sensasi.pkl', 'rb') as sensasi:
                r15_model_RF_sensasi = pickle.load(sensasi)
                
            with open('r15_model_kenyamanan.pkl', 'rb') as kenyamanan:
                r15_model_RF_kenyamanan = pickle.load(kenyamanan)
            
            with open('r15_model_penerimaan.pkl', 'rb') as penerimaan:
                r15_model_RF_penerimaan = pickle.load(penerimaan)
            
            model_RF_sensasi=r15_model_RF_sensasi
            model_RF_kenyamanan=r15_model_RF_kenyamanan
            model_RF_penerimaan=r15_model_RF_penerimaan
        else:
            pass
        
            
    
    elif no_ruang=='R40':
        print('masuk r40')
        model=os.path.exists('r40_model_sensasi.pkl') and os.path.exists('r40_model_kenyamanan.pkl') and os.path.exists('r40_model_kenyamanan.pkl')
        if model==True:
            with open('r40_model_sensasi.pkl', 'rb') as sensasi:
                r40_model_RF_sensasi = pickle.load(sensasi)
                
            with open('r40_model_kenyamanan.pkl', 'rb') as kenyamanan:
                r40_model_RF_kenyamanan = pickle.load(kenyamanan)
            
            with open('r40_model_penerimaan.pkl', 'rb') as penerimaan:
                r40_model_RF_penerimaan = pickle.load(penerimaan)
            
            model_RF_sensasi=r40_model_RF_sensasi
            model_RF_kenyamanan=r40_model_RF_kenyamanan
            model_RF_penerimaan=r40_model_RF_penerimaan
        
        else:
            pass
    
    
    
    if model==True: 
        
        #Prediksi Sensasi
        data_sensasi = data_saturuang.loc[:,personal+latar_belakang+sensor_indoor+sensor_outdoor]
        survei_sensasi = data_saturuang.loc[:,'sensasi']
        prediksi_sensasi = model_RF_sensasi.predict(data_sensasi)
        akurasi_sensasi=accuracy_score(survei_sensasi, prediksi_sensasi)
        #Update data prediksi sensasi
        data_saturuang_update = data_saturuang.copy()
        data_saturuang_update['Prediksi Sensasi']=prediksi_sensasi
        
        
        #Prediksi kenyamanan
        data_kenyamanan = data_saturuang_update.loc[:,personal+['Prediksi Sensasi']]
        survei_kenyamanan = data_saturuang.loc[:,'kepuasan']
        prediksi_kenyamanan = model_RF_kenyamanan.predict(data_kenyamanan)
        akurasi_kenyamanan=accuracy_score(survei_kenyamanan, prediksi_kenyamanan)
        #Update data prediksi kenyamanan
        data_saturuang_update['Prediksi Kenyamanan']=prediksi_kenyamanan
        
        
        #Prediksi penerimaan
        data_penerimaan=data_saturuang_update.loc[:,personal+['Prediksi Sensasi']+['Prediksi Kenyamanan']]
        survei_penerimaan = data_saturuang.loc[:,'penerimaan']
        prediksi_penerimaan = model_RF_penerimaan.predict(data_penerimaan)
        akurasi_penerimaan=accuracy_score(survei_penerimaan, prediksi_penerimaan)

        #Update data
        data_saturuang_update['Prediksi Penerimaan']=prediksi_penerimaan
        
        output_akhir_prediksi.append(data_saturuang_update)
        
        
        
    elif model==False:
        print("Ga ada model")
            
       
