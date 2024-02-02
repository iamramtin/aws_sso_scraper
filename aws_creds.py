import getpass
import os
import json
import pyperclip
from pathlib import Path
from playwright.sync_api import Playwright, sync_playwright

# Path to the file to save the credentials to
AWS_CREDENTIALS_FILE = 'auth/aws_credentials.txt'

# List of AWS accounts to get credentials for
ACCOUNTS = ['account1', 'account2', 'account3', 'account4', 'account5']

# Path to the cookies file used to restore the session
COOKIES = 'auth/cookies.json'

# Login to the AWS SSO portal
def login(page, email, password):
    print("Logging in...")
    page.goto('https://synlz.awsapps.com/start/#/')
    page.get_by_placeholder('someone@example.com').click()
    page.get_by_placeholder('someone@example.com').fill(email)
    page.get_by_role('button', name='Next').click()
    page.get_by_placeholder('Password').click()
    page.get_by_placeholder('Password').fill(password)
    page.get_by_role('button', name='Sign in').click()
    page.wait_for_load_state('networkidle')

    # Check the "Don't ask again for 60 days" checkbox if 2FA is enabled
    page.get_by_label("Don't ask again for 60 days").check()

def get_credentials(page, account):
    print("Getting credentials for account:", account)
    page.locator('portal-instance').filter(has_text='{} #'.format(account)).locator('div').nth(1).click()
    page.locator('portal-instance').filter(has_text='{} #'.format(account)).locator('#temp-credentials-button').click()
    page.locator('#hover-copy-env').click()
    page.get_by_text('×').click()
    
    return pyperclip.paste()

def save_credentials(credentials, file_path):
    with open(file_path, 'w') as file:
        for cred in credentials:
            file.write(str(cred) + '\n\n')

def save_cookies(context):
    Path(COOKIES).write_text(json.dumps(context.cookies()))
    print("Saved credentials to:", AWS_CREDENTIALS_FILE)

def load_cookies(context):
    print("Loading cookies...")
    context.add_cookies(json.loads(Path(COOKIES).read_text()))

def run(playwright: Playwright) -> None:
    email = os.getenv("AWS_SS0_EMAIL")
    password = getpass.getpass("Enter your password: ")
    credentials = []
    
    if not email or not password:
        print("Please set the environment variable AWS_SS0_EMAIL and enter your password.")
        return
    
    try:
        if os.path.exists(COOKIES) and os.path.getsize(COOKIES) > 0:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
            load_cookies(context)
            page = context.new_page()
            page.goto('https://synlz.awsapps.com/start#/')
        else:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            login(page, email, password)
        
        page.locator('#app-03e8643328913682').click()
        for account in ACCOUNTS:
            credentials.append(get_credentials(page, account))

        save_cookies(context)
        save_credentials(credentials, AWS_CREDENTIALS_FILE)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        context.close()
        browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)