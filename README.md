# AWS Workflow for Open Data Program

This repository contains the code to generate metadata YAML files for the Open Data Program based on Physionet open datasets hosted on PhysioNet's AWS S3 bucket. The script automatically retrieves the prefixes (directories) from the S3 bucket and uses data from the PhysioNet API to create YAML files containing metadata for each project. These YAML files will be used for adding datasets to the Registry of Open Data on AWS (https://registry.opendata.aws/).


## Features

- Fetches prefixes from the `physionet-open` S3 bucket (arn:aws:s3:::physionet-open/) using AWS boto3 (no AWS credentials needed);
- Retrieves metadata for projects using the PhysioNet API;
- Generates .yaml files for each project, including the project's name, description, license, PhysioNet documentation links, and associated S3 bucket information;


## Installation

To set up the project on your local environment:

- Clone the repository:
`git clone https://github.com/MIT-LCP/aws-physionet-open-data.git`
- Navigate into the project directory:
`cd aws-physionet-open-data`
- Install the required dependencies:
`pip install -r requirements.txt`


## Usage

To generate the YAML metadata files, follow these steps:

- From project directory, run the following command to execute the script:
`python metadata-generator.py`

The script will:

- Retrieve the S3 bucket prefixes from the `physionet-open` bucket;
- Fetch the latest project details from the PhysioNet API;
- Generate the YAML metadata files in a folder named `datasets`.

Output:

YAML Files: The script generates a set of .yaml files, each representing a project's metadata.


## Example of Generated YAML

```
Name: MIMIC-IV Clinical Database Demo

Description: The Medical Information Mart for Intensive Care (MIMIC)-IV database
  is comprised of deidentified electronic health records for patients admitted
  to the Beth Israel Deaconess Medical Center. Access to MIMIC-IV is limited to credentialed
  users. Here, we have provided an openly-available demo of MIMIC-IV containing a
  subset of 100 patients. The dataset includes similar content to MIMIC-IV, but
  excludes free-text clinical notes. The demo may be useful for running workshops and
  for assessing whether the MIMIC-IV is appropriate for a study before making
  an access request.

Documentation: https://doi.org/10.13026/dp1f-ex47

Contact: https://physionet.org/about/#contact_us

ManagedBy: '[PhysioNet](https://physionet.org/)'

UpdateFrequency: Not updated

Tags:
- aws-pds

License: Open Data Commons Open Database License v1.0

Resources:
- Description: https://doi.org/10.13026/dp1f-ex47
  ARN: arn:aws:s3:::physionet-open/mimic-iv-demo/
  Region: us-east-1
  Type: S3 Bucket

ADXCategories: Healthcare & Life Sciences Data
```

## Contributing

If you would like to contribute to this project, please create a pull request with your changes. We welcome bug fixes, improvements, and additional features.


## License

This project is licensed under the MIT License - see the LICENSE file for details.


## Contact

For any questions or further assistance, please contact the project maintainers through PhysioNet.
