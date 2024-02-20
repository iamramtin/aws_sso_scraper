# AWS SSO Credentials Fetcher

## Description
This script automates the process of fetching AWS temporary credentials from the AWS SSO portal and saving them to a file. It uses Playwright, a Python library for automating browser interactions, to navigate the AWS SSO portal and extract the credentials.

## Features
- Fetch AWS temporary credentials for multiple AWS accounts from the AWS SSO portal.
- Save the fetched credentials to a specified file.
- Supports headless mode for running the script without launching a browser window.
- Allows customization of login email, AWS SSO credentials file path, and list of AWS accounts to fetch credentials for.

## Requirements
- Python 3.x
- Playwright Python library (`pip install playwright`)

## Usage
1. Ensure you have Python installed on your system.
2. Install the required dependencies.
3. Run the script with the following command:

python aws_creds.py --headless --email <your_AWS_SSO_email> --credentials <path_to_credentials_file> --accounts <comma_separated_list_of_AWS_accounts>

## Command Line Parameters
- `--headless`: Optional flag to run the script in headless mode (defaults to true).
- `--email`: Email address for AWS SSO login.
- `--credentials`: Required parameter specifying the path to the AWS credentials file.
- `--accounts`: Required parameter specifying a list of AWS account names.

## Author
Ramtin Mesgari