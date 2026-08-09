import tensorflow as tf
from tensorflow.keras import backend as K
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization, Activation
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
import numpy as np
from sklearn.utils.class_weight import compute_class_weight
import os

# --- NEW: Self-Contained Focal Loss Function ---
# We define the function ourselves to avoid broken external libraries.
def categorical_focal_loss(gamma=2.0, alpha=0.25):
    """
    Implementation of Focal Loss from the paper in multiclass classification
    """
    def focal_loss_fixed(y_true, y_pred):
        # Clip the prediction value to prevent NaN's and Inf's
        epsilon = K.epsilon()
        y_pred = K.clip(y_pred, epsilon, 1. - epsilon)

        # Calculate Cross Entropy
        cross_entropy = -y_true * K.log(y_pred)

        # Calculate Focal Loss
        loss = alpha * K.pow(1 - y_pred, gamma) * cross_entropy
        
        # Sum the losses in mini_batch
        return K.sum(loss, axis=1)
    return focal_loss_fixed
# --- End of new function ---

# --- Configuration ---
IMG_HEIGHT = 48
IMG_WIDTH = 48
BATCH_SIZE = 64
EPOCHS = 100
NUM_CLASSES = 7
TRAIN_DIR = 'data/train/'
TEST_DIR = 'data/test/'
NEW_MODEL_NAME = 'emotion_model_robust.h5' # New name for our best model

# --- Data Augmentation ---
train_datagen = ImageDataGenerator(rescale=1./255, rotation_range=25, shear_range=0.2, zoom_range=0.2, width_shift_range=0.2, height_shift_range=0.2, horizontal_flip=True, fill_mode='nearest')
test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(TRAIN_DIR, color_mode='grayscale', target_size=(IMG_HEIGHT, IMG_WIDTH), batch_size=BATCH_SIZE, class_mode='categorical', shuffle=True)
test_generator = test_datagen.flow_from_directory(TEST_DIR, color_mode='grayscale', target_size=(IMG_HEIGHT, IMG_WIDTH), batch_size=BATCH_SIZE, class_mode='categorical', shuffle=False)

# --- Class Weights ---
class_weights = compute_class_weight(class_weight='balanced', classes=np.unique(train_generator.classes), y=train_generator.classes)
class_weights_dict = dict(enumerate(class_weights))
print("Calculated Class Weights:", class_weights_dict)

# --- Deeper Model Architecture ---
print("Building the robust, deeper model...")
model = Sequential()
# [Block 1 to 4 and Dense layers are the same as before]
# Block 1
model.add(Conv2D(64, (3, 3), padding='same', input_shape=(IMG_WIDTH, IMG_HEIGHT, 1)))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
# Block 2
model.add(Conv2D(128, (5, 5), padding='same'))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
# Block 3
model.add(Conv2D(256, (3, 3), padding='same'))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
# Block 4
model.add(Conv2D(512, (3, 3), padding='same'))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
# Flatten and Dense layers
model.add(Flatten())
model.add(Dense(256))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(Dropout(0.5))
# Output layer
model.add(Dense(NUM_CLASSES, activation='softmax'))
model.summary()

# --- Callbacks ---
checkpoint = ModelCheckpoint(NEW_MODEL_NAME, monitor='val_accuracy', verbose=1, save_best_only=True, mode='max')
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=5, min_lr=0.00001, verbose=1)
callbacks_list = [checkpoint, reduce_lr]

# --- Compile and Train ---
model.compile(
    optimizer=Adam(learning_rate=0.001),
    # --- Using our self-contained function ---
    loss=categorical_focal_loss(gamma=2.0, alpha=0.25),
    metrics=['accuracy']
)

print("Starting robust model training...")
history = model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // BATCH_SIZE,
    epochs=EPOCHS,
    validation_data=test_generator,
    validation_steps=test_generator.samples // BATCH_SIZE,
    callbacks=callbacks_list,
    class_weight=class_weights_dict
)

print(f"\nTraining complete. Best robust model saved as {NEW_MODEL_NAME}")
