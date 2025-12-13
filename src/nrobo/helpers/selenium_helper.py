import subprocess

from selenium.common import JavascriptException


def update_selenium_dependencies():
    subprocess.run(["pip", "install", "-U", "selenium", "webdriver-manager"], check=True)
    print("✅ Updated Selenium and webdriver-manager.")


def _safe_ready_state(driver):
    try:
        return driver.execute_script("return document.readyState")
    except JavascriptException:
        return None
    except Exception:
        return None
