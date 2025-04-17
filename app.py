from flask import Flask, render_template, request, jsonify
import pandas as pd
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://nguyenthecong1106:IjfEKO3CtSt1frQl@cluster0.3nhkobx.mongodb.net/?retryWrites=true&w=majority&tls=true")
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
    app.run(debug=True)
