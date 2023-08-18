import pickle
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense, Dropout
from pandas import read_csv
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from numpy import array, repeat, isnan
from itertools import product
from numpy import Inf
from os import path, makedirs

ROOT_DIR = path.dirname(path.dirname(path.abspath(__file__)))

forecasting_time = '5m'

for service in ['adservice', 'cartservice', 'checkoutservice', 'currencyservice', 'frontend', 'productcatalogservice',
                'recommendationservice', 'shippingservice']:
    bm = Inf

    df = read_csv(ROOT_DIR + '/database/ob/' + service + '/' + forecasting_time + '/train.csv')
    data_list = ['pods', 'cpu', 'memory', 'rt', 'tp']

    df_for_training = df[data_list].astype(float)

    scaler = MinMaxScaler()
    scaler = scaler.fit(df_for_training)
    df_for_training_scaled = scaler.transform(df_for_training)

    if not path.isdir(ROOT_DIR + '/knowledge/models/ob/' + service + '/' + forecasting_time + '/'):
        makedirs(ROOT_DIR + '/knowledge/models/ob/' + service + '/' + forecasting_time + '/')

    pickle.dump(scaler, open(ROOT_DIR + '/knowledge/models/ob/' + service + '/' + forecasting_time + '/scaler.pkl', 'wb'))

    # Split of data
    trainX = []
    trainY = []

    if forecasting_time == '1m':
        n_future = 1
        n_past = 20
    elif forecasting_time == '3m':
        n_future = 1
        n_past = 7
    else:
        n_future = 1
        n_past = 4

    for i in range(n_past, len(df_for_training_scaled) - n_future + 1):
        trainX.append(df_for_training_scaled[i - n_past:i, 0:df_for_training.shape[1]])
        trainY.append(df_for_training_scaled[i + n_future - 1:i + n_future, 0])

    trainX, trainY = array(trainX), array(trainY)

    split = int(len(trainX) * 0.70)

    testX = trainX[split:, :, :]
    testY = trainY[split:, :]

    trainX = trainX[0:split, :, :]
    trainY = trainY[0:split, :]

    # Hyper-Parameters
    batch_size = [64, 128]
    epochs = [1, 2, 4, 8, 10, 200]
    hidden_layers = [2, 3, 4, 5, 6]
    learning_rate = [0.05, 0.01, 0.001]
    number_of_units = [50, 75, 100]

    hyper_param = list(product(batch_size, epochs, hidden_layers, learning_rate, number_of_units))
    for b, e, h, l, u in hyper_param:
        model = Sequential()

        for _ in range(0, h):
            model.add(
                LSTM(u, activation='relu', input_shape=(trainX.shape[1], trainX.shape[2]), return_sequences=True))

        model.add(LSTM(u, activation='relu', return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(trainY.shape[1]))
        opt = tf.keras.optimizers.Adam(learning_rate=l)
        model.compile(optimizer=opt, loss='mean_squared_error')
        history = model.fit(trainX, trainY, epochs=e, batch_size=b, validation_split=0.1, verbose=0)

        prediction = model.predict(testX, verbose=0)

        prediction_copies = repeat(prediction, df_for_training.shape[1], axis=-1)
        prediction_testY = repeat(testY, df_for_training.shape[1], axis=-1)

        if not isnan(prediction).any():
            accurracy = mean_squared_error(prediction, testY)

            if accurracy < bm:
                print('MSE: ', accurracy)
                bm = accurracy
                model.save(ROOT_DIR + '/knowledge/models/ob/' + service + '/' + forecasting_time + '/model.h5')
