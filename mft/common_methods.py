def normalise_data(scaler, series):
    return scaler.transform(series.reshape(-1, 1))


def denormalise_data(scaler, series):
    return scaler.inverse_transform(series.reshape(-1, 1))


def load_pickle(file_path: str):
    from pickle import load

    return load(open('knowledge/models/' + file_path + '.pkl', 'rb'))
