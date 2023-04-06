# import Neccesary modules
import os
import cv2
import pyttsx3
import argparse
import numpy as np
import joblib
np.random.seed(2019)

from report_gen import Generate_Report
from datetime import date
import sqlite3

import matplotlib.pyplot as plt 

from tensorflow.keras.preprocessing import image
from keras.models import Model, load_model
from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input, decode_predictions

import warnings
warnings.filterwarnings('ignore')


model = VGG16(weights='imagenet', include_top=True)



# Read Image through Command Line Arguments
ap = argparse.ArgumentParser()
ap.add_argument('-l', '--list', help='delimited list input', type=str)
args = ap.parse_args()
params = [str(item) for item in args.list.split(',')]

'''ap.add_argument("-i", "--input", required=True,
	help="path to input Image")
args = vars(ap.parse_args())

#load Image Path
img_path=args["input"]'''

img_path = 'Testdata/'+params[0]



# Predict the Class of Image
print(img_path)
img = image.load_img(img_path, target_size=(224, 224))
img = image.img_to_array(img)
img = np.expand_dims(img, axis=0)
img = preprocess_input(img)

#Feature Extraction
model = Model(inputs=model.input, outputs=model.get_layer('fc2').output)
fc2_features = model.predict(img)


X = np.load('X.npy')
y = np.load('y1.npy')
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
lda = LDA(n_components=4)
X = lda.fit_transform(X, y)
fc2_features = lda.transform(fc2_features)



# define Classes List
Class=['No DR','Mild DR','Moderate DR','Severe DR','Proliferative DR']


model_name = 'Multi_HANet.h5'
model = joblib.load(model_name)

pred = model.predict(fc2_features)
print('Class: ',Class[int(pred)])

engine = pyttsx3.init();
#cv2.putText(img_disp1,str(Class[int(pred)]),(5, 25),cv2.FONT_HERSHEY_SIMPLEX,0.7, (0, 0, 255), 2)


name = params[1]
mobile = params[2]
gender = params[3]
age = params[4]
sc = int(pred)

if int(pred)>0:
    dr_test = 'DR Positive'
else:
    dr_test = 'DR Negative'

dr_severity = Class[int(pred)]

Date = date.today().strftime("%b-%d-%Y")

conn = sqlite3.connect('Diabetic Retinopathy.db')
with conn:
	cursor=conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS DR_Patients_Details (Scan TEXT,Full_Name TEXT,Mobile_No TEXT,Gender TEXT,Age TEXT,DR_Test TEXT,DR_Severity TEXT,Test_Date TEXT)')
cursor.execute('INSERT INTO DR_Patients_Details (Scan,Full_Name,Mobile_No,Gender,Age,DR_Test,DR_Severity,Test_Date) VALUES(?,?,?,?,?,?,?,?)',(img_path,name,mobile,gender,age,dr_test,dr_severity,Date))
conn.commit()

Generate_Report(name,gender,age,mobile,sc,sc,img_path)

engine.say("Severity Level of DR is "+Class[int(pred)]);
engine.runAndWait() ;
image = cv2.imread(img_path, 1)
plt.axis('off')
plt.title(Class[int(pred)]) 
plt.imshow(image) 
plt.show() 



#file_name = "{}.png".format(os.getpid())
#cv2.imwrite("Outputs\\"+file_name, img_disp1)
#cv2.waitKey(0)
#cv2.destroyAllWindows()




