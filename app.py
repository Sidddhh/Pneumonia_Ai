from flask import Flask, render_template, request, url_for
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os
from create_db import insert_patients, get_all_patients

app = Flask(__name__)
model = load_model("model/best_vgg_model.keras")

# Ensure uploads folder exists
os.makedirs('static/uploads', exist_ok=True)

@app.route('/')
def home():
    patients = get_all_patients()
    return render_template('home.html', patients=patients)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        age = int(request.form['age'])  # Updated: getting age instead of DOB
        city = request.form['city']
        state = request.form['state']
        pincode = request.form['pincode']
        xray_date = request.form['xray_date']
        mobile = request.form['mobile']
        email = request.form['email']

        file = request.files['xray']
        if file.filename == '':
            return "No selected file."

        if file:
            filename = file.filename
            img_path = os.path.join('static/uploads', filename)
            file.save(img_path)

            img = image.load_img(img_path, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0) / 255.0

            prediction = model.predict(img_array)[0][0]
            label = "Pneumonia" if prediction > 0.5 else "Normal"
            confidence = round(float(prediction if prediction > 0.5 else 1 - prediction) * 100, 2)

            insert_patients(name, lastname, age, city, state, pincode, xray_date, mobile, email, filename, label)

            return render_template('register.html', result=f"{label} ({confidence}%)", image=filename)

    return render_template('register.html', result=None)


@app.route('/patients', methods=['GET'])
def patient():
    query = request.args.get('query', '').lower()
    all_data = get_all_patients()
    
    if query:
        filtered = []
        for row in all_data:
            name = f"{row[1]} {row[2]}".lower()  # First name + Last name
            mobile = row[7]
            if query in name or query in mobile:
                filtered.append(row)
        return render_template('patients.html', data=filtered, query=query)
    
    return render_template('patients.html', data=all_data, query='')




if __name__ == '__main__':
    app.run(debug=True)
