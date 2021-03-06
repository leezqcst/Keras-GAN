import numpy as np
from keras.models import Model 
from keras.layers import Input, Dense, BatchNormalization, Activation, Deconv2D, Reshape, UpSampling2D

def basic_gen(input_shape, img_shape, nf=128, scale=4, FC=[], use_upsample=False):
    dim, h, w = img_shape 

    img = Input(input_shape)
    x = img
    for fc_dim in FC: 
        x = Dense(fc_dim)(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)

    x = Dense(nf*2**(scale-1)*(h/2**scale)*(w/2**scale))(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = Reshape((nf*2**(scale-1), h/2**scale, w/2**scale))(x)

    for s in range(scale-2, -1, -1):
        # up sample can elimiate the checkbroad artifact
        # http://distill.pub/2016/deconv-checkerboard/
        if use_upsample:
            x = UpSampling2D()(x)
            x = Conv2D(nf*2**s, (3,3), padding='same')(x)
        else:
            x = Deconv2D(nf*2**s, (3, 3), strides=(2, 2), padding='same')(x) 
        x = BatchNormalization()(x)
        x = Activation('relu')(x)

    if use_upsample:
        x = UpSampling2D()(x)
        x = Conv2D(dim, (3, 3), padding='same')(x)
    else:
        x = Deconv2D(dim, (3, 3), strides=(2, 2), padding='same')(x) 

    x = Activation('tanh')(x)

    return Model(img, x)



def fc_gen(input_shape, img_shape, filters=[1024, 512, 256]):
    i = Input(input_shape)
    x = i

    for f in filters:
        x = Dense(f)(x)
        x = Activation('relu')(x)
    x = Dense(np.prod(img_shape))(x)
    x = Activation('sigmoid')(x)
    x = Reshape(img_shape)(x)
    return Model(i, x)


