import getpass
import os
import json
import argparse
from pathlib import Path
from playwright.sync_api import Playwright, sync_playwright

# Path to the cookies file used to restore the session
COOKIES = "auth/cookies.json"

def parse_arguments():
    parser = argparse.ArgumentParser(description="Get AWS credentials from the AWS SSO portal")
    parser.add_argument("--headless", action="store_true", help="Whether to run in headless mode")
    parser.add_argument("--email", type=str, required=True, help="Email address for AWS SSO login")
    parser.add_argument("--credentials", type=str, required=True, help="Path to AWS credentials file")
    parser.add_argument("--accounts", nargs="*", required=True, type=str, help="List of AWS accounts")

    args = parser.parse_args()

    try:
        if not args.email:
            raise ValueError("Email argument is required.")
        
        if not args.credentials:
            raise ValueError("Credentials argument is required.")

        if not args.accounts:
            raise ValueError("At least one AWS account is required.")

        print("\nHeadless:", args.headless)
        print("Email:", args.email)
        print("Credentials:", args.credentials)
        print("Accounts:", args.accounts)
        print()
    except Exception as e:
        print("An error occurred while parsing command-line arguments:", e)
        exit(1)
    
    return args


def get_credentials(page, account):
    print("Getting credentials for account:", account)
    page.locator("portal-instance").filter(has_text="{} #".format(account)).locator("div").nth(1).click()
    page.locator("portal-instance").filter(has_text="{} #".format(account)).locator("#temp-credentials-button").click()

    credential_text = page.locator("#cli-cred-file-code").inner_text()
    page.get_by_text("×").click()

    return credential_text


def save_credentials(credentials, file_path):
    with open(file_path, "w") as file:
        for cred in credentials:
            file.write(str(cred) + "\n\n")

    print("Saved credentials to:", file_path)


def load_cookies(context, page, email, password):
    print("Loading cookies...")
    context.add_cookies(json.loads(Path(COOKIES).read_text()))


def save_cookies(context):
    Path(COOKIES).write_text(json.dumps(context.cookies()))


def login(page, email, password):
    print("Navigating to AWS SSO portal...")
    page.goto("https://synlz.awsapps.com/start/#/")
    page.wait_for_load_state("networkidle")

    try:
        email_field = page.locator('input[placeholder="someone@example.com"]')
        if email_field:
            email_field.click()
            email_field.fill(email)
    except:
        pass
    
    try:
        password_field = page.locator('input[placeholder="Password"]')
        if password_field:
            print("Logging in...")
            password_field.click()
            password_field.fill(password)
            page.get_by_role("button", name="Sign in").click()
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("domcontentloaded")
    except:
        pass

    # Check the "Don't ask again for 60 days" checkbox if 2FA is enabled
    try:
        checkbox = page.get_by_label("Don't ask again for 60 days", timeout=10000)
        if checkbox:
            print("Verifying 2FA...")
            checkbox.check()
    except:
        pass

    page.goto("https://synlz.awsapps.com/start#/")
    
    
def run(playwright: Playwright, args) -> None:
    email = args.email
    password = getpass.getpass("Enter your password:\n")
    
    if not password:
        print("Please enter your password and try again.")
        return
    
    try:
        browser = playwright.chromium.launch(headless=args.headless)
        context = browser.new_context()
        page = context.new_page()

        if os.path.exists(COOKIES) and os.path.getsize(COOKIES) > 0:
            load_cookies(context, page, email, password)

        login(page, email, password)
        
        page.locator("#app-03e8643328913682").click()
        credentials = [get_credentials(page, account) for account in args.accounts]

        save_cookies(context)
        save_credentials(credentials, args.credentials)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        context.close()
        browser.close()


if __name__ == "__main__":
    args = parse_arguments()
    with sync_playwright() as playwright:
        run(playwright, args)
