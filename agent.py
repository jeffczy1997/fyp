from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import Input
from tensorflow.keras.layers import Dropout, Conv2D, Flatten, Dense, Concatenate, Reshape, GlobalMaxPool2D

def create_model():
    x_input = Input(shape=(9, 7, 1), name="move")
    x = Conv2D(filters=10, kernel_size=3, activation="softsign")(x_input)
    x = Conv2D(filters=20, kernel_size=3, activation="softsign")(x)
    x = Conv2D(filters=200, kernel_size=3, activation="softsign")(x)
    # x = Conv2D(filters=256, kernel_size=3, activation="softsign", padding="same")(x)
    # x = Conv2D(filters=512, kernel_size=3, activation="softsign", padding="same")(x)
    # x = Conv2D(filters=1024, kernel_size=3, activation="softsign", padding="same")(x)
    # x = Conv2D(filters=2048, kernel_size=3, activation="softsign", padding="same")(x)
    # x = Conv2D(filters=4096, kernel_size=3, activation="softsign", padding="same")(x)
    # x = Conv2D(filters=8192, kernel_size=3, activation="softsign", padding="same")(x)

    # y_input = Input(shape=(1, 1, 1), name="action")
    # y = Conv2D(filters=256, kernel_size=1, activation="softsign", padding="same")(y_input)
    # # y = Conv2D(filters=16, kernel_size=1, activation="softsign")(y)
    # # y = Conv2D(filters=2048, kernel_size=1, activation="softsign", padding="same")(y)
    # # y = Conv2D(filters=3840, kernel_size=1, activation="softsign", padding="same")(y)
    # # y = Reshape((5, 3, 256))(y)
    # y = GlobalMaxPool2D()(y)

    # z = Concatenate()([x, y])

    z = Dropout(0.2)(x)

    z = Flatten()(z)

    z = Dense(units=200, activation="softsign")(z)
    z = Dense(units=200, activation="softsign")(z)

    z = Dense(units=1, activation="softsign")(z)

    model = Model(inputs=[x_input], outputs=[z])
    model.compile(optimizer=Adam(lr=0.001), loss='mse', metrics=['accuracy'])

    return model