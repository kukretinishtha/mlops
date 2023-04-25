def remove_collinear_cols(x_data):
    return x_data.drop(['D', 'I'], axis=1)
