# %%
import requests
import json
import pandas as pd

# %%
def model_predict(data_original):
    
    data = data_original.copy()    
    data = data.fillna('N/A')

    # Specific conversion for numeric columns that need to be displayed as integers (no decimals)
    columns_to_convert = ['Veteran status', 'Work authorization', 'Disability', 'Ethnicity']
    for col in columns_to_convert:
        if col in data.columns:
            data[col] = data[col].apply(lambda x: str(int(x)) if x != 'N/A' else 'N/A')

    # Format GPA with two decimal places
    if 'GPA' in data.columns:
        data['GPA'] = data['GPA'].apply(lambda x: f"{x:.2f}" if x != 'N/A' else 'N/A')
    
    data = data.to_dict(orient='records')
    # Serialize the input data to JSON
    dataset = json.dumps(data)
    
    # Define the headers for JSON content type
    headers = {'Content-Type': 'application/json'}
    
    # Call the first API - resume scorer
    resume_url = 'https://jennjwang.pythonanywhere.com'
    resume_response = requests.post(resume_url, data=dataset, headers=headers)
    
    if not resume_response.ok:
        print("Error:", resume_response.status_code)
        return None
    
    try:
        resume_response_data = json.loads(resume_response.text)
        resume_predictions = json.loads(resume_response_data['prediction'])
        resume_score_map = {item['applicant_id']: item['score'] for item in resume_predictions}
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return None
    

    # Update the input data with the resume score
    for applicant in data:
        applicant_id = str(applicant['Applicant ID'])
        applicant['Resume score'] = resume_score_map.get(applicant_id, 0)
    
    # Serialize the updated data for the next API call
    updated_dataset = json.dumps(data)    

    # Call the second API - candidate scorer
    candidate_url = 'https://heonlee.pythonanywhere.com'
    candidate_response = requests.post(candidate_url, data=updated_dataset, headers=headers)
    
    if not candidate_response.ok:
        print("Error:", candidate_response.status_code)
        return None
    
    try:
        candidate_response_data = json.loads(candidate_response.text)
        final_predictions = json.loads(candidate_response_data['prediction'])
        final_score_map = {item['applicant_id']: item['prediction'] for item in final_predictions}
    except json.JSONDecodeError as e:
        print("Error decoding JSON for the second API:", e)
        return None
    
    
    for applicant in data:
        applicant_id = str(applicant['Applicant ID'])
        applicant['Interview prediction'] = final_score_map.get(applicant_id, 0)
        
    results = pd.DataFrame(data)
    results['GPA'] = results['GPA'].astype(float)
    results['Resume score'] = results['Resume score'].astype(float)
    results['Interview prediction'] = results['Interview prediction'].astype(int)
    
    return results

def score_predict(data_original):

    data = data_original.copy()    
    data = data.fillna('N/A')

    # Specific conversion for numeric columns that need to be displayed as integers (no decimals)
    columns_to_convert = ['Veteran status', 'Work authorization', 'Disability', 'Ethnicity']
    for col in columns_to_convert:
        if col in data.columns:
            data[col] = data[col].apply(lambda x: str(int(x)) if x != 'N/A' else 'N/A')

    # Format GPA with two decimal places
    if 'GPA' in data.columns:
        data['GPA'] = data['GPA'].apply(lambda x: f"{x:.2f}" if x != 'N/A' else 'N/A')
    
    data = data.to_dict(orient='records')
    # Serialize the input data to JSON
    dataset = json.dumps(data)
    
    # Define the headers for JSON content type
    headers = {'Content-Type': 'application/json'}
    
    # Call the first API - resume scorer
    resume_url = 'https://jennjwang.pythonanywhere.com'
    resume_response = requests.post(resume_url, data=dataset, headers=headers)
    
    if not resume_response.ok:
        print("Error:", resume_response.status_code)
        return None
    
    try:
        resume_response_data = json.loads(resume_response.text)
        resume_predictions = json.loads(resume_response_data['prediction'])
        resume_score_map = {item['applicant_id']: item['score'] for item in resume_predictions}
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return None
    
    for score in resume_predictions:
        pos_pred = float(score['score'])/10
        neg_pred = 1 - pos_pred

        return [pos_pred, neg_pred]


