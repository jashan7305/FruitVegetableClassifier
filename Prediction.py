import os
import json
import numpy as np
# from PIL import Image

model_name = "FruitClassification.h5"

with open(os.path.join("data","index_to_label.json"), "r") as f:
    index_to_label = json.load(f)

if model_name == "FruitClassification.h5":

    from keras.models import load_model
    from keras.applications.mobilenet_v2 import preprocess_input
    from keras.preprocessing.image import img_to_array

    model = load_model(os.path.join("models",model_name))
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    def predict_image(img):
        img = img.resize((224, 224))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        prediction = model.predict(img_array)
        class_index = np.argmax(prediction, axis=1)[0]
        label = index_to_label[str(class_index)]
        return label
    
else:
    
    pass

# trial_img = Image.open(data_dir + "\\test\\apple\\Image_1.jpg")
# predict_image(trial_img)



