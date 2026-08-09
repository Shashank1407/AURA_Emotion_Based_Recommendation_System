import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization, Activation
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau

# --- Configuration ---
IMG_HEIGHT = 48
IMG_WIDTH = 48
BATCH_SIZE = 64
EPOCHS = 60 # Increase this for better results, e.g., 100
NUM_CLASSES = 7 # 7 emotions
TRAIN_DIR = 'data/train/'
TEST_DIR = 'data/test/'
NEW_MODEL_NAME = 'emotion_model_custom.h5'

# --- Data Augmentation ---
# Create more training data by applying random transformations
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

# For the test set, we only rescale the images
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

# --- Build the Advanced CNN Model ---
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

model.summary()

# --- Callbacks for Smarter Training ---
# Save the best model during training
checkpoint = ModelCheckpoint(
    NEW_MODEL_NAME,
    monitor='val_accuracy',
    verbose=1,
    save_best_only=True,
    mode='max'
)

# Reduce learning rate when a metric has stopped improving
reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.1,
    patience=5,
    min_lr=0.00001,
    verbose=1
)

callbacks_list = [checkpoint, reduce_lr]

# --- Compile and Train the Model ---
model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("Starting model training...")
history = model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // BATCH_SIZE,
    epochs=EPOCHS,
    validation_data=test_generator,
    validation_steps=test_generator.samples // BATCH_SIZE,
    callbacks=callbacks_list
)

print(f"\nTraining complete. Best model saved as {NEW_MODEL_NAME}")