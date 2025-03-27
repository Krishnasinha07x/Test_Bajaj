import pandas as pd
import re
from datetime import timedelta
from tabulate import tabulate

# Function to compute consecutive absence periods
def compute_absence_streaks(attendance_data):
    df = pd.DataFrame(attendance_data)
    df['entry_date'] = pd.to_datetime(df['date'])
    df.sort_values(by=['student_id', 'entry_date'], inplace=True)

    absence_periods = []

    for student_id, group in df.groupby('student_id'):
        dates = sorted(group['entry_date'].tolist())
        streak_start = dates[0]
        prev_date = streak_start
        streak_count = 1

        for i in range(1, len(dates)):
            if dates[i] == prev_date + timedelta(days=1):
                streak_count += 1
            else:
                absence_periods.append({
                    'student_id': student_id,
                    'start_date': streak_start.strftime('%d-%m-%Y'),
                    'end_date': prev_date.strftime('%d-%m-%Y'),
                    'absence_days': streak_count
                })
                streak_start = dates[i]
                streak_count = 1
            prev_date = dates[i]

        absence_periods.append({
            'student_id': student_id,
            'start_date': streak_start.strftime('%d-%m-%Y'),
            'end_date': prev_date.strftime('%d-%m-%Y'),
            'absence_days': streak_count
        })

    return pd.DataFrame(absence_periods)

# Function to validate email format
def validate_email(email_str):
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*@[a-zA-Z]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email_str))

# Function to merge student info and create notification messages
def merge_student_info(absence_data, student_info):
    student_df = pd.DataFrame(student_info)
    merged_df = absence_data.merge(student_df, on='student_id', how='left')

    merged_df['contact_email'] = merged_df['parent_email'].apply(
        lambda email: email if validate_email(email) else None
    )
    merged_df['notification'] = merged_df.apply(
        lambda row: (
            f"Dear Parent, your child {row['student_name']} missed school "
            f"from {row['start_date']} to {row['end_date']} for {row['absence_days']} days. "
            f"Kindly ensure consistent attendance."
        ) if row['contact_email'] is not None else None,
        axis=1
    )

    merged_df.sort_values(by=['student_id', 'start_date'], inplace=True)
    return merged_df[['student_id', 'start_date', 'end_date', 'absence_days', 'contact_email', 'notification']]

# Sample attendance records
attendance_records = [
    {'student_id': 1, 'date': '2024-03-01'},
    {'student_id': 1, 'date': '2024-03-02'},
    {'student_id': 1, 'date': '2024-03-03'},
    {'student_id': 1, 'date': '2024-03-04'},
    {'student_id': 1, 'date': '2024-03-06'},
    {'student_id': 2, 'date': '2024-03-05'},
    {'student_id': 2, 'date': '2024-03-06'},
    {'student_id': 2, 'date': '2024-03-07'},
    {'student_id': 2, 'date': '2024-03-08'},
    {'student_id': 2, 'date': '2024-03-09'},
]

# Sample student details with Indian names
student_info = [
    {'student_id': 1, 'student_name': 'Aarav Sharma', 'parent_email': 'sharma_aarav@gmail.com'},
    {'student_id': 2, 'student_name': 'Priya Patel', 'parent_email': 'patel.priya@outlook.com'},
    {'student_id': 3, 'student_name': 'Vikram Singh', 'parent_email': 'invalid.email.com'},
]

# Calculate absence streaks
absence_data = compute_absence_streaks(attendance_records)

# First Output: Students with absences exceeding 3 days
extended_absences = absence_data[absence_data['absence_days'] > 3]
extended_absences = extended_absences.astype(str)
extended_absences = extended_absences.rename(columns={
    'start_date': 'absence_start_date',
    'end_date': 'absence_end_date',
    'absence_days': 'total_absent_days'
})

print("Students with Absences Exceeding 3 Consecutive Days:")
print(tabulate(extended_absences[['student_id', 'absence_start_date', 'absence_end_date', 'total_absent_days']].values,
               headers=['student_id', 'absence_start_date', 'absence_end_date', 'total_absent_days'],
               tablefmt='grid',
               stralign='left',
               numalign='left',
               maxcolwidths=[10, 20, 20, 20],
               disable_numparse=True,
               showindex=False))
print("\n")

# Second Output: Detailed report with notifications
detailed_report = merge_student_info(absence_data, student_info)
detailed_report = detailed_report.astype(str)
detailed_report = detailed_report.rename(columns={
    'start_date': 'absence_start_date',
    'end_date': 'absence_end_date',
    'absence_days': 'total_absent_days',
    'contact_email': 'email'
})

print("Comprehensive Absence Report with Notifications:")
print(tabulate(detailed_report.values,
               headers=['student_id', 'absence_start_date', 'absence_end_date', 'total_absent_days', 'email', 'notification'],
               tablefmt='grid',
               stralign='left',
               numalign='left',
               maxcolwidths=[10, 20, 20, 20, 25, 60],
               disable_numparse=True,
               showindex=False))