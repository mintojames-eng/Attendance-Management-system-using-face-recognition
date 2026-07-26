# ==========================================
# ROLE 2: EDA AND INSIGHT LEAD
# ==========================================
# Responsibilities: 
# - Exploratory Data Analysis (EDA) on student and attendance data.
# - Statistical modeling and generating visual insights.
# - Validating dataset quality and class balances.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pymongo import MongoClient

# Configure aesthetic visual themes
sns.set_theme(style="darkgrid")
plt.style.use("dark_background")

def fetch_data_for_analysis():
    """Mock fetching data or fetch from live MongoDB for analysis."""
    # Since we might not have live DB stats, we will simulate the DataFrame
    # based on the schema of the app's attendance logs
    
    # Simulating data that the system would normally collect
    np.random.seed(42)
    dates = pd.date_range(start="2026-06-01", end="2026-07-25", freq="D")
    
    data = []
    departments = ['Computer Science', 'IT', 'AI & ML', 'Data Science']
    for d in dates:
        # Simulate attendance records per day
        for dept in departments:
            present = np.random.randint(20, 50)
            absent = 50 - present
            data.append({"Date": d, "Department": dept, "Status": "Present", "Count": present})
            data.append({"Date": d, "Department": dept, "Status": "Absent", "Count": absent})
            
    df = pd.DataFrame(data)
    return df

def perform_eda(df):
    """Run comprehensive exploratory data analysis."""
    print("--- Dataset Overview ---")
    print(df.info())
    print("\\n--- Summary Statistics ---")
    print(df.describe())
    
    # Extract only present records to observe attendance trends
    present_df = df[df['Status'] == 'Present']
    
    # 1. Overall Attendance Trend over time
    plt.figure(figsize=(14, 6))
    sns.lineplot(data=present_df, x='Date', y='Count', hue='Department', marker='o')
    plt.title('Daily Attendance Trends by Department')
    plt.ylabel('Number of Present Students')
    plt.xlabel('Date')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('attendance_trends.png')
    print("Saved attendance_trends.png")
    
    # 2. Distribution of Attendance Rates
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=present_df, x='Department', y='Count', palette="Set2")
    plt.title('Distribution of Present Students per Department')
    plt.savefig('attendance_distribution.png')
    print("Saved attendance_distribution.png")
    
    # 3. Bar Chart of Total Attendance per Department
    agg_df = present_df.groupby('Department')['Count'].sum().reset_index()
    plt.figure(figsize=(10, 6))
    sns.barplot(data=agg_df, x='Department', y='Count', palette="viridis")
    plt.title('Total Attendance Count by Department')
    plt.ylabel('Total Present Students')
    plt.savefig('attendance_bar_chart.png')
    print("Saved attendance_bar_chart.png")
    
    # 4. Overall Present vs Absent Ratio
    total_agg = df.groupby('Status')['Count'].sum()
    plt.figure(figsize=(7, 7))
    plt.pie(total_agg, labels=total_agg.index, autopct='%1.1f%%', colors=['#ff9999','#66b3ff'], startangle=90)
    plt.title('Total Present vs Absent Ratio across all sessions')
    plt.savefig('present_absent_ratio.png')
    print("Saved present_absent_ratio.png")

def main():
    print("Starting EDA & Insight Generation...")
    df = fetch_data_for_analysis()
    perform_eda(df)
    print("Insights successfully generated as visualization images.")

if __name__ == "__main__":
    main()
