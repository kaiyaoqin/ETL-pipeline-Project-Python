import pandas as pd
import numpy as np

def merge_all_data(user_health_data_path, supplement_usage_path, experiments_path, user_profiles_path):
    # Load the datasets
    user_health_data = pd.read_csv(user_health_data_path)
    supplement_usage = pd.read_csv(supplement_usage_path)
    experiments = pd.read_csv(experiments_path)
    user_profiles = pd.read_csv(user_profiles_path)

    # Ensure proper data types for date columns
    user_health_data["date"] = pd.to_datetime(user_health_data["date"])
    supplement_usage["date"] = pd.to_datetime(supplement_usage["date"])

    # Merge supplement_usage with experiments to add experiment names
    supplement_usage = pd.merge(supplement_usage, experiments, on="experiment_id", how="left")
    supplement_usage = supplement_usage.rename(columns={"name": "experiment_name"})
    
    # Standardize dosage units and convert dosage to grams by dividing by 1000
    supplement_usage["dosage_grams"] = supplement_usage["dosage"] / 1000

    supplement_usage.drop(columns=["dosage", "dosage_unit"], inplace=True)



    # Merge user_profiles with health data
    user_health_data = pd.merge(user_health_data, user_profiles, on="user_id", how="left")

    # Define user_age_group based on age
    def categorize_age(age):
        if pd.isna(age):
            return "Unknown"
        elif age < 18:
            return "Under 18"
        elif 18 <= age <= 25:
            return "18-25"
        elif 26 <= age <= 35:
            return "26-35"
        elif 36 <= age <= 45:
            return "36-45"
        elif 46 <= age <= 55:
            return "46-55"
        elif 56 <= age <= 65:
            return "56-65"
        else:
            return "Over 65"

    user_health_data["user_age_group"] = user_health_data["age"].apply(categorize_age)
    user_health_data['user_age_group'] = user_health_data['user_age_group'].astype('category')                                                           
    user_health_data.drop(columns=["age"], inplace=True)

    # Combine health data and supplement data into one dataset
    combined_data = pd.merge(user_health_data, supplement_usage, on=["user_id", "date"], how="outer")

    # Fill missing values in supplement data
    combined_data["supplement_name"] = combined_data["supplement_name"].fillna("No intake")
    combined_data["dosage_grams"] = combined_data["dosage_grams"].replace("", np.nan)  # Replace empty strings
    combined_data["dosage_grams"] = combined_data["dosage_grams"].fillna(np.nan)
    combined_data["is_placebo"] = combined_data["is_placebo"].fillna(np.nan)
    combined_data["experiment_name"] = combined_data["experiment_name"].fillna(np.nan)
    
    # Strip the 'h' or 'H' from each value, then convert to float
    combined_data['sleep_hours'] = combined_data['sleep_hours'].str.rstrip('hH').astype('float')
    combined_data['is_placebo'] = combined_data['is_placebo'].astype('bool') 
    
    # Ensure all columns are in the required order
    final_data = combined_data[[
        "user_id", "date", "email", "user_age_group", "experiment_name", 
        "supplement_name", "dosage_grams", "is_placebo", "average_heart_rate", 
        "average_glucose", "sleep_hours", "activity_level"
    ]]

    return final_data


# Data Validation: View datatype of the newly merged dataset 
merged_dataset = merge_all_data('user_health_data.csv', 'supplement_usage.csv', 'experiments.csv', 'user_profiles.csv')

print(merged_dataset.dtypes)
merged_dataset