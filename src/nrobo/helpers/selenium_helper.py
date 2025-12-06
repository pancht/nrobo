import subprocess


def update_selenium_dependencies():
    subprocess.run(["pip", "install", "-U", "selenium", "webdriver-manager"], check=True)
    print("✅ Updated Selenium and webdriver-manager.")
