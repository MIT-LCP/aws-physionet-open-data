import pandas as pd
import requests
import yaml
import re, os
import zipfile
import boto3
from botocore import UNSIGNED
from botocore.config import Config

csv_file = './physionet-open-s3-bucket-prefixes.csv'
zip_file_path = 'datasets.zip'

# Directory to save YAML files
yaml_dir = 'datasets'
os.makedirs(yaml_dir, exist_ok=True)


def get_s3_open_bucket_prefixes(bucket_name):
    """
    List the prefixes (directories) in the S3 bucket using boto3 without credentials.

    This function connects to an S3 bucket using anonymous access (no credentials) 
    to retrieve the list of all directory prefixes (CommonPrefixes) in the bucket. 
    The retrieved prefixes are stored in a pandas DataFrame.

    Parameters:
        bucket_name (str): The name of the S3 bucket to be accessed.

    Returns:
        DataFrame: A DataFrame containing the project slugs as a list of directory prefixes.
    """
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))  # No sign request
    
    prefixes = []
    
    # Continuation token for paginating through large result sets
    continuation_token = None
    
    while True:
        # List the objects in the bucket (with '/' as the delimiter)
        if continuation_token:
            result = s3.list_objects_v2(Bucket=bucket_name, Delimiter='/', ContinuationToken=continuation_token)
        else:
            result = s3.list_objects_v2(Bucket=bucket_name, Delimiter='/')
        
        # If there are CommonPrefixes, add the found prefixes to the list
        if 'CommonPrefixes' in result:
            for prefix in result['CommonPrefixes']:
                prefixes.append(prefix['Prefix'])
        
        # Check if there are more results to be listed
        if result.get('IsTruncated'):
            continuation_token = result.get('NextContinuationToken')
        else:
            break

    df = pd.DataFrame([prefix.strip('/') for prefix in prefixes], columns=['project_slug'])
    
    return df


def export_s3_open_bucket_prefixes(df, csv_file):
    """
    Save the list of S3 bucket prefixes to a CSV file.

    This function saves the DataFrame containing project slugs (directory prefixes) 
    into a CSV file for later reference.

    Parameters:
        df (DataFrame): The DataFrame containing project slugs.
        csv_file (str): The file path where the CSV will be saved.
    """
    df.to_csv(csv_file, index=False)
    print(f"CSV file '{csv_file}' created successfully with {len(df)} project slugs.")


def fetch_project_latest_version(project_slug):
    """
    Fetch the latest version of the project from the PhysioNet API.

    This function retrieves the latest version number of a project 
    from the PhysioNet API using its project slug.

    Parameters:
        project_slug (str): The slug of the project (directory name in the bucket).

    Returns:
        str: The latest version number of the project, or None if not found.
    """
    url = f"https://physionet.org/api/v1/project/published/{project_slug}/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            latest_version = data[-1]  # Take the latest version of the project
            return latest_version['version']
    return None


def fetch_project_details(project_slug, project_latest_version):
    """
    Fetch project details from the PhysioNet API.

    This function retrieves the project details, including its name, description, 
    license, and documentation link. It fetches this information using the project slug 
    and the latest project version.

    Parameters:
        project_slug (str): The slug of the project (directory name in the bucket).
        project_latest_version (str): The latest version number of the project.

    Returns:
        dict: A dictionary containing the project's name, description, license, and link.
    """
    url = f"https://physionet.org/api/v1/project/published/{project_slug}/{project_latest_version}/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        
        if len(data) > 0:
            return {
                'name': data['title'],
                'description': re.sub(r'<[^>]+>', '', data['abstract']),
                'license': data.get('license', {}).get('name', 'Open Data Commons Open Database License v1.0'),
                'link': f"https://doi.org/{data.get('doi')}" if data.get('doi') else f"https://physionet.org/content/{project_slug}/"
            }
    return None


def create_yaml_files(df):
    """
    Loop over each project slug and create a YAML file.

    For each project slug in the DataFrame, this function fetches the project details 
    using the PhysioNet API and generates a corresponding YAML file containing 
    metadata about the project.

    Parameters:
        df (DataFrame): The DataFrame containing project slugs.
    """
    for index, row in df.iterrows():
        project_slug = row['project_slug']
        
        # Fetch the latest version of the project
        project_latest_version = fetch_project_latest_version(project_slug)
        
        # Fetch project details
        project_info = fetch_project_details(project_slug, project_latest_version)

        if project_info:
            # Create YAML content
            yaml_content = {
                'Name': project_info['name'],
                'Description': project_info['description'],
                'Documentation': project_info['link'],
                'Contact': "https://physionet.org/about/#contact_us",
                'ManagedBy': "PhysioNet",
                'UpdateFrequency': "Not updated",
                'Tags': ['aws-pds'],
                'License': project_info['license'],
                'Resources': [
                    {
                        'Description': project_info['link'],
                        'ARN': f"arn:aws:s3:::physionet-open/{project_slug}/",
                        'Region': "us-east-1",
                        'Type': "S3 Bucket"
                    }
                ],
                'ADXCategories': 'Healthcare & Life Sciences Data'
            }

            # Save the YAML file
            yaml_file_path = os.path.join(yaml_dir, f"{project_slug}.yaml")
            with open(yaml_file_path, 'w') as yaml_file:
                yaml.dump(yaml_content, yaml_file, default_flow_style=False, sort_keys=False)


def create_zip_file():
    """
    Create a ZIP file containing all YAML files.

    This function zips all the YAML files generated in the specified directory 
    into a single ZIP file for easy distribution.

    Parameters:
        None
    """
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for root, dirs, files in os.walk(yaml_dir):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)

    print(f"YAML files successfully generated and zipped in {zip_file_path}")


def main():
    # Generate metadata for the Open Data Program by retrieving the S3 bucket prefixes 
    # and creating YAML files.
    df_prefixes = get_s3_open_bucket_prefixes('physionet-open')
    # export_s3_open_bucket_prefixes(df_prefixes, csv_file)
    create_yaml_files(df_prefixes)
    # create_zip_file()


if __name__ == "__main__":
    main()
