import PySimpleGUI as sg
import pandas as pd
import numpy as np
import pickle
import sqlite3
from sklearn.ensemble import RandomForestClassifier

# Sample data for training
data = {
    'age': [63, 37, 41, 56, 57],
    'sex': [1, 1, 0, 1, 0],
    'cp': [1, 2, 1, 1, 0],
    'trestbps': [145, 130, 130, 120, 120],
    'chol': [233, 250, 204, 236, 354],
    'fbs': [1, 0, 0, 0, 0],
    'restecg': [0, 1, 0, 1, 0],
    'thalach': [150, 187, 172, 178, 163],
    'exang': [0, 0, 0, 0, 1],
    'oldpeak': [2.3, 3.5, 1.4, 0.8, 0.6],
    'slope': [0, 0, 2, 2, 2],
    'ca': [0, 0, 0, 0, 0],
    'thal': [1, 2, 2, 2, 3],
    'target': [1, 1, 1, 1, 0]
}

df = pd.DataFrame(data)
X = df.drop('target', axis=1)
y = df['target']

# Train a RandomForest model
model = RandomForestClassifier()
model.fit(X, y)

# Save the model
with open('heart_disease_model.pkl', 'wb') as file:
    pickle.dump(model, file)

# Load the model
with open('heart_disease_model.pkl', 'rb') as file:
    model = pickle.load(file)

# Connect to SQLite database and create table if not exists
conn = sqlite3.connect('heart_disease_data.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS heart_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    age INTEGER,
    sex INTEGER,
    cp INTEGER,
    trestbps INTEGER,
    chol INTEGER,
    fbs INTEGER,
    restecg INTEGER,
    thalach INTEGER,
    exang INTEGER,
    oldpeak REAL,
    slope INTEGER,
    ca INTEGER,
    thal INTEGER,
    prediction TEXT,
    probability REAL
)
''')

conn.commit()
conn.close()

# Define the GUI layout
layout = [
    [sg.Text('Heart Disease Risk Prediction')],
    [sg.Text('Age'), sg.Input(key='-AGE-', size=(10, 1))],
    [sg.Text('Sex (0 or 1)'), sg.Input(key='-SEX-', size=(10, 1))],
    [sg.Text('Chest Pain Type (0-3)'), sg.Input(key='-CP-', size=(10, 1))],
    [sg.Text('Resting Blood Pressure'), sg.Input(key='-TRESTBPS-', size=(10, 1))],
    [sg.Text('Serum Cholesterol'), sg.Input(key='-CHOL-', size=(10, 1))],
    [sg.Text('Fasting Blood Sugar (0 or 1)'), sg.Input(key='-FBS-', size=(10, 1))],
    [sg.Text('Resting Electrocardiographic Results (0-2)'), sg.Input(key='-RESTECG-', size=(10, 1))],
    [sg.Text('Maximum Heart Rate Achieved'), sg.Input(key='-THALACH-', size=(10, 1))],
    [sg.Text('Exercise Induced Angina (0 or 1)'), sg.Input(key='-EXANG-', size=(10, 1))],
    [sg.Text('ST Depression Induced by Exercise'), sg.Input(key='-OLDPEAK-', size=(10, 1))],
    [sg.Text('Slope of Peak Exercise ST Segment (0-2)'), sg.Input(key='-SLOPE-', size=(10, 1))],
    [sg.Text('Number of Major Vessels Colored by Fluoroscopy (0-4)'), sg.Input(key='-CA-', size=(10, 1))],
    [sg.Text('Thalassemia (0-3)'), sg.Input(key='-THAL-', size=(10, 1))],
    [sg.Button('Predict'), sg.Button('Exit')],
    [sg.Text('', size=(50, 1), key='-RESULT-')]
]

# Create the window
window = sg.Window('Heart Disease Risk Prediction', layout)

# Event loop
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == 'Predict':
        # Retrieve input values
        input_data = {
            'age': [float(values['-AGE-'])],
            'sex': [float(values['-SEX-'])],
            'cp': [float(values['-CP-'])],
            'trestbps': [float(values['-TRESTBPS-'])],
            'chol': [float(values['-CHOL-'])],
            'fbs': [float(values['-FBS-'])],
            'restecg': [float(values['-RESTECG-'])],
            'thalach': [float(values['-THALACH-'])],
            'exang': [float(values['-EXANG-'])],
            'oldpeak': [float(values['-OLDPEAK-'])],
            'slope': [float(values['-SLOPE-'])],
            'ca': [float(values['-CA-'])],
            'thal': [float(values['-THAL-'])]
        }

        # Convert input data to DataFrame
        input_df = pd.DataFrame(input_data)

        # Predict
        prediction = model.predict(input_df)
        prediction_proba = model.predict_proba(input_df)

        # Update GUI with results
        result_text = f"Prediction: {'Yes' if prediction[0] == 1 else 'No'}\n"
        result_text += f"Probability of Heart Disease: {prediction_proba[0][1]:.2f}"
        window['-RESULT-'].update(result_text)

        # Save the prediction to the database
        conn = sqlite3.connect('heart_disease_data.db')
        c = conn.cursor()

        c.execute('''
            INSERT INTO heart_data (
                age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, prediction, probability
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            input_df['age'][0], input_df['sex'][0], input_df['cp'][0], input_df['trestbps'][0], input_df['chol'][0],
            input_df['fbs'][0], input_df['restecg'][0], input_df['thalach'][0], input_df['exang'][0], input_df['oldpeak'][0],
            input_df['slope'][0], input_df['ca'][0], input_df['thal'][0], 'Yes' if prediction[0] == 1 else 'No', prediction_proba[0][1]
        ))

        conn.commit()
        conn.close()

window.close()
