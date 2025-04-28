from flask import Flask, render_template, request, jsonify
import pandas as pd
from pymongo import MongoClient
import os
import json

app = Flask(__name__)

# Connect to MongoDB Atlas
MONGO_URI = "mongodb+srv://nguyenthecong1106:IjfEKO3CtSt1frQl@cluster0.3nhkobx.mongodb.net/job_demand_db?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI, tls=True, serverSelectionTimeoutMS=5000)

db = client['job_demand_db']
collection = db['april_prediction']

# Convert Mongo collection to DataFrame
df = pd.DataFrame(list(collection.find({}, {'_id': 0})))

# Build a nested dict: province → { job_major → April_Prediction }
province_job_dict = (
    df
    .groupby('workingLocations')
    .apply(lambda g: dict(zip(
        g['job_major'],
        g['April_Prediction'].astype(int)
    )))
    .to_dict()
)

# (Optional) write it out for inspection
with open('province_job_demand.json', 'w', encoding='utf-8') as f:
    json.dump(province_job_dict, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    provinces = df['workingLocations'].unique()
    job_majors = df['job_major'].unique()
    return render_template('index.html', provinces=provinces, job_majors=job_majors)

@app.route('/get_pareto_data', methods=['GET','POST'])
def get_pareto_data():
    if request.method == 'GET':
        return "POST only", 400

    province  = request.json.get('province')
    job_major = request.json.get('job_major','Tất cả')

    # --- specific‐job branch: look up April_Prediction from our dict ---
    if job_major != 'Tất cả':
        row = df[
            (df['workingLocations'] == province) &
            (df['job_major']       == job_major)
        ]
        months = ["Tháng 1","Tháng 2","Tháng 3","Tháng 4"]
        if not row.empty:
            vals = [
              float(row.iloc[0]['January']),
              float(row.iloc[0]['February']),
              float(row.iloc[0]['March']),
              int  (row.iloc[0]['April_Prediction'])
            ]
        else:
            vals = [0,0,0,0]

        return jsonify({
            'type'     : 'series',
            'location' : province,
            'job_major': job_major,
            'months'   : months,
            'values'   : vals
        })

    # --- "all majors" branch: build bar‐chart data from our dict ---
    majors_dict = province_job_dict.get(province, {})
    labels = list(majors_dict.keys())
    values = list(majors_dict.values())

    return jsonify({
        'type': 'pareto',
        'labels': labels,
        'values': values
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
