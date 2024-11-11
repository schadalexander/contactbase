import pandas as pd
import streamlit as st
import os
import openai
import re

def clean_company_name(company_name):
    # Use OpenAI API to clean company names
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = f"Clean the following company name so it can be used in emails. Output ONLY the cleaned company name, nothing else. Example: \"ATLAS Media GmbH\" becomes \"Atlas Media\" and \"HIT Feinkost Spezialitäten\" becomes \"Hit\": {company_name}"
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=50
    )
    cleaned_name = response.choices[0].message['content'].strip()
    return cleaned_name

def clean_job_title(job_title):
    # Use OpenAI API to clean job titles
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = f"Clean the following job titel so it can be used in the following email: \"Hallo, ich habe gesehen, dass Sie als JOBTITEL einiges an Erfahrung gesammelt haben\". Output ONLY the cleaned company name in german, nothing else: {job_title}"
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=50
    )
    cleaned_title = response.choices[0].message['content'].strip()
    return cleaned_title

def process_csv(file_path, delete_duplicates, delete_no_salutation, clean_company_names, clean_job_titles):
    # Load the CSV file
    df = pd.read_csv(file_path, sep=';')
    initial_row_count = len(df)

    # Step 1: Remove duplicate rows based on the 'E-Mail-Adresse' column
    if delete_duplicates:
        if 'E-Mail-Adresse' in df.columns:
            df = df.drop_duplicates(subset='E-Mail-Adresse')
        else:
            st.warning("Column 'E-Mail-Adresse' not found.")

    # Step 2: Remove rows that do not contain a salutation (e.g., 'Anrede' column)
    if delete_no_salutation:
        if 'Anrede' in df.columns:
            df = df[df['Anrede'].notna()]
        else:
            st.warning("Column 'Anrede' not found.")

    # Step 3: Clean company names if required
    if clean_company_names:
        if 'Firmenname' in df.columns:
            df['Cleaned_Firmenname'] = df['Firmenname'].apply(lambda x: clean_company_name(x) if pd.notna(x) else x)
        else:
            st.warning("Column 'Firmenname' not found.")

    # Step 4: Clean job titles if required
    if clean_job_titles:
        if 'Jobtitel' in df.columns:
            df['Cleaned_Jobtitel'] = df['Jobtitel'].apply(lambda x: clean_job_title(x) if pd.notna(x) else x)
        else:
            st.warning("Column 'Jobtitel' not found.")

    final_row_count = len(df)
    rows_removed = initial_row_count - final_row_count

    return df, rows_removed

# Streamlit App
def main():
    st.title("ContactBase - Dealfront Optimizer")
    st.write("Lade eine Dealfront Liste hoch und erhalte eine bereinigte Liste zurück.")

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        # Options to apply
        delete_duplicates = st.checkbox("Delete duplicate rows based on personal email address")
        delete_no_salutation = st.checkbox("Delete rows without a salutation")
        clean_company_names = st.checkbox("Clean company names for email usage")
        clean_job_titles = st.checkbox("Clean job titles for email usage")

        if st.button("Process File"):
            output_path = 'processed_contacts.csv'  # Save to current working directory
            df_processed, rows_removed = process_csv(uploaded_file, delete_duplicates, delete_no_salutation, clean_company_names, clean_job_titles)
            df_processed.to_csv(output_path, index=False, sep=';')
            st.success(f"Processed file saved to: {output_path}")
            st.info(f"Number of rows removed: {rows_removed}")
            st.write(df_processed)

if __name__ == "__main__":
    main()
