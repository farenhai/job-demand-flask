from flask import Flask, render_template, request, jsonify
import pandas as pd
from pymongo import MongoClient
import os


app = Flask(__name__)

# Connect to MongoDB Atlas
MONGO_URI = "mongodb+srv://nguyenthecong1106:IjfEKO3CtSt1frQl@cluster0.3nhkobx.mongodb.net/job_demand_db?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI, tls=True, serverSelectionTimeoutMS=5000)

db = client['job_demand_db']
collection = db['april_prediction']

# Convert Mongo collection to DataFrame
df = pd.DataFrame(list(collection.find({}, {'_id': 0})))

@app.route('/')
def index():
    provinces = df['workingLocations'].unique()
    return render_template('index.html', provinces=provinces)

@app.route('/get_pie_chart_data', methods=['POST'])
def get_pie_chart_data():
    province = request.json['province']
    filtered_df = df[df['workingLocations'] == province]
    total = filtered_df['April_Prediction'].sum()
    pie_data = filtered_df[['job_major', 'April_Prediction']].copy()
    pie_data['percentage'] = (pie_data['April_Prediction'] / total * 100).round(2)

    data = {
        'labels': pie_data['job_major'].tolist(),
        'values': pie_data['April_Prediction'].tolist(),
        'percentages': pie_data['percentage'].tolist()
    }
    return jsonify(data)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Render will set PORT env var
    app.run(host='0.0.0.0', port=port)

