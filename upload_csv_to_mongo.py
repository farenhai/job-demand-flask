from pymongo import MongoClient
import pandas as pd

print("🚀 Script started...")

try:
    # Connect to MongoDB
    print("🔌 Connecting to MongoDB Atlas...")
    client = MongoClient("mongodb+srv://nguyenthecong1106:IjfEKO3CtSt1frQl@cluster0.3nhkobx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    
    db = client['job_demand_db']
    collection = db['april_prediction']
    print("✅ Connected!")

    # Load CSV
    print("📂 Reading CSV...")
    df = pd.read_csv('data/final_df_1104_rounded.csv')
    print(f"✅ Loaded CSV with {len(df)} rows")

    # Upload
    print("📤 Uploading to MongoDB...")
    collection.insert_many(df.to_dict(orient='records'))
    print("🎉 Upload complete!")

except Exception as e:
    print("❌ Error occurred:", e)
