import tensorflow  as tf
import numpy as np 
import pandas as pd
import cv2
import imutils
from imutils.contours import sort_contours

import tensorflow as tf 
from tensorflow.keras.models import load_model

import matplotlib.pyplot as plt
import matplotlib

model = load_model('./models/second_model.h5')

matplotlib.use('Agg')

def names_label():
    names = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    names = [label for label in names]
    return names 


def prepro_img(path_img):
    gray = cv2.cvtColor(cv2.imread(path_img), cv2.COLOR_BGR2GRAY)
    img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 9)
    img = cv2.Canny(img, 40, 150)
    img = cv2.dilate(img, np.ones((2,2), np.uint8))
    return gray, img

1

def find_contours(img, gray):
    img_copy = img.copy()
    gray = np.array(gray)
    conts = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    conts = imutils.grab_contours(conts)
    conts = sort_contours(conts, method='left-to-right')[0]

    min_w, max_w = 5, 50
    min_h, max_h = 15, 45 
    n = 5
    letters = []
    conts_2 = []
    
    for c in conts:
        (x, y, w, h) = cv2.boundingRect(c)
        if (w >= min_w and w < max_w) and (h >= min_h and h < max_h):
            img_p = gray[y-n : y+h+n,   x-n : x+n+w ]
            cv2.rectangle(img_copy, (x,y), (x+w, h+y), (255,100,0),2)
            img_p = cv2.threshold(img_p, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            img_p = cv2.dilate(img_p, np.ones((2,2), np.uint8 ))
            letters.append(img_p)
            conts_2.append(c)
    plt.imshow(img_copy, cmap='gray');
    return letters, conts_2



def img_prediction(img, model, name_labels):
    img = cv2.resize(img, (28,28))
    img = img.astype('float32')/255.0
    img = np.expand_dims(img, axis=-1)
    img = np.reshape(img, (1,28,28,1))

    prediction = model.predict(img)
    prediction = name_labels[np.argmax(prediction)]

    return prediction

def letter_pred(img, gray):
    names = names_label()
    letters = find_contours(img, gray)[0]
    img_pred = [img_prediction(letter, model, names) for letter in letters]
    question_row = []
    answer_row = []

    for i in range(len(img_pred)):
        if img_pred[i] == 'Z' or img_pred[i] == 'G' or img_pred[i] == '0' or img_pred[i] == 'J' or img_pred[i] == 'T' or img_pred[i] == 'P' or img_pred[i] == 'Q' or img_pred[i] == '8':
            img_pred[i] = img_pred[i].replace('Z', '2')
            img_pred[i] = img_pred[i].replace('G', '6')
            img_pred[i] = img_pred[i].replace('T', '1')
            img_pred[i] = img_pred[i].replace('Q', 'D')
            img_pred[i] = img_pred[i].replace('P', 'D')
            img_pred[i] = img_pred[i].replace('8', 'B')
            img_pred[i] = img_pred[i].replace('0', 'D')
            img_pred[i] = img_pred[i].replace('J', 'A')
            
        if i%2 == 0:
            if img_pred[i] == '4':
                img_pred[i] = img_pred[i].replace('4', 'A')
            answer_row.append(img_pred[i])
        else:
            question_row.append(img_pred[i]) 
    return  answer_row

# x = r'C:\Users\santi\OneDrive - Universidad Pedagogica Nacional\teisis_maestria\tesis_1\images_test\img_001.png'
# x =x.replace('\\', '/')
# gray, img = prepro_img(x)
# answer_row = letter_pred(img, gray)
# print(answer_row)