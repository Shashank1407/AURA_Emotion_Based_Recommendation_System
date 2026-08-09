import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization, Activation
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
# --- NEW BALANCING --- Import necessary libraries
import numpy as np
from sklearn.utils.class_weight import compute_class_weight
import os

# --- Configuration ---
IMG_HEIGHT = 48
IMG_WIDTH = 48
BATCH_SIZE = 64
EPOCHS = 75 # Increased epochs for better learning with weights
NUM_CLASSES = 7
TRAIN_DIR = 'data/train/'
TEST_DIR = 'data/test/'
NEW_MODEL_NAME = 'emotion_model_balanced.h5'

# --- Data Augmentation ---
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=25,
    shear_range=0.2,
    zoom_range=0.2,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)
test_datagen = ImageDataGenerator(rescale=1./255)

# --- Load Data from Directories ---
train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    color_mode='grayscale',
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True
)

test_generator = test_datagen.flow_from_directory(
    TEST_DIR,
    color_mode='grayscale',
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)

# --- NEW BALANCING --- Calculate Class Weights to handle imbalanced data
class_labels = list(train_generator.class_indices.keys())
print("Class Labels:", class_labels)

# Count images in each class
class_counts = [len(os.listdir(os.path.join(TRAIN_DIR, label))) for label in class_labels]
print("Image counts per class:", dict(zip(class_labels, class_counts)))

# Calculate weights
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_generator.classes),
    y=train_generator.classes
)
class_weights_dict = dict(enumerate(class_weights))
print("Calculated Class Weights:", class_weights_dict)


# --- Build the Advanced CNN Model ---
# (The model architecture is the same as before)
print("Building the model...")
model = Sequential()
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
# Flatten and Dense layers
model.add(Flatten())
model.add(Dense(256))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(Dropout(0.5))
# Output layer
model.add(Dense(NUM_CLASSES, activation='softmax'))

# --- Callbacks ---
checkpoint = ModelCheckpoint(NEW_MODEL_NAME, monitor='val_accuracy', verbose=1, save_best_only=True, mode='max')
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=5, min_lr=0.00001, verbose=1)
callbacks_list = [checkpoint, reduce_lr]

# --- Compile and Train the Model ---
model.compile(optimizer=Adam(learning_rate=0.001), loss='categorical_crossentropy', metrics=['accuracy'])

print("Starting balanced model training...")
history = model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // BATCH_SIZE,
    epochs=EPOCHS,
    validation_data=test_generator,
    validation_steps=test_generator.samples // BATCH_SIZE,
    callbacks=callbacks_list,
    # --- NEW BALANCING --- Apply the calculated weights here!
    class_weight=class_weights_dict
)

print(f"\nTraining complete. Best balanced model saved as {NEW_MODEL_NAME}")
