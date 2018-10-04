from keras.utils import to_categorical
import numpy as np
import time
from models import model


# Load train and test data
labels = 'keyword noise voice'.split()
X_train = np.array([])
y_train = np.array([])
# X_val = np.array([])
# y_val = np.array([])
# X_test = np.array([])
# y_test = np.array([])

for i, label in enumerate(labels):
    train_path = 'data/featurized/training/{}_16k.npy'.format(label)
    # val_path = 'data/featurized/validation/{}_16k.npy'.format(label)
    # test_path = 'data/featurized/testing/{}_16k.npy'.format(label)

    category = labels.index(label)

    x_train_data = np.load(train_path)
    y_train_data = np.full(x_train_data.shape[0], fill_value=category)
    # x_val_data = np.load(val_path)
    # y_val_data = np.full(x_val_data.shape[0], fill_value=category)
    # x_test_data = np.load(test_path)
    # y_test_data = np.full(x_test_data.shape[0], fill_value=category)

    if X_train.size > 0:
        X_train = np.vstack((X_train, x_train_data))
        y_train = np.append(y_train, y_train_data)
        # X_val = np.vstack((X_val, x_val_data))
        # y_val = np.append(y_val, y_val_data)
        # X_test = np.vstack((X_test, x_test_data))
        # y_test = np.append(y_test, y_test_data)
    else:
        X_train = x_train_data
        y_train = y_train_data
        # X_val = x_val_data
        # y_val = y_val_data
        # X_test = x_test_data
        # y_test = y_test_data


X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], X_train.shape[2], 1)
y_train = to_categorical(y_train)
# X_val = X_val.reshape(X_val.shape[0], X_val.shape[1], X_val.shape[2], 1)
# y_val = to_categorical(y_val)
# X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], X_test.shape[2], 1)
# y_test = to_categorical(y_test)



# Model
model = model()

# model.summary()

model.fit(X_train, y_train, batch_size=50, epochs=50, verbose=1)#, validation_data=(X_val, y_val))

# print(model.evaluate(X_test, y_test))

model.save('models/model_{}.h5'.format(round(time.time())))

