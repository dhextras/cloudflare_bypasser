import json
import os
import time
from datetime import datetime

import pyautogui
from DrissionPage import ChromiumOptions, ChromiumPage

# Disable the fail-safe
pyautogui.FAILSAFE = False


def bypasser(url, log_dir="logs"):
    """
    Bypass Cloudflare protection and save cookies to a JSON file.

    Args:
        url (str): The URL to access
        log_dir (str): Directory to save log files

    Returns:
        dict: Result of bypass attempt with status and details
    """
    os.makedirs(log_dir, exist_ok=True)

    # Generate a unique log filename based on timestamp and URL
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_url = "".join(c if c.isalnum() else "_" for c in url)
    log_file_path = os.path.join(
        log_dir, f"cloudflare_bypass_{safe_url}_{timestamp}.log"
    )
    cookies_file_path = os.path.join(log_dir, f"cookies_{safe_url}_{timestamp}.json")

    try:
        with open(log_file_path, "w") as log_f, open(
            cookies_file_path, "w"
        ) as cookies_f:
            log_f.write(f"Cloudflare Bypass Attempt for {url} at {timestamp}\n")
            json.dump({}, cookies_f, indent=2)

        options = ChromiumOptions()
        driver = ChromiumPage(addr_or_opts=options)
        driver.get(url)
        time.sleep(5)

        max_retries = 10
        try_count = 0

        with open(log_file_path, "a") as log_f:
            while "just a moment" in driver.title.lower():
                if try_count >= max_retries:
                    log_f.write(
                        f"Failed to bypass Cloudflare after {max_retries} attempts\n"
                    )
                    return {
                        "status": "failed",
                        "message": f"Failed to bypass Cloudflare after {max_retries} attempts",
                        "url": url,
                    }

                log_f.write(
                    f"Attempt {try_count + 1}: Cloudflare protection detected\n"
                )

                try:
                    button = _find_cloudflare_button(driver)

                    if button:
                        # button.click()
                        pyautogui.click()
                        pyautogui.moveTo(424, 470)
                        pyautogui.click()
                        log_f.write("Verification button clicked\n")
                    else:
                        log_f.write("Verification button not found\n")
                        return {
                            "status": "failed",
                            "message": "Verification button not found",
                            "url": url,
                        }

                    for _ in range(30):
                        time.sleep(1)
                        if not "just a moment" in driver.title.lower():
                            break

                    try_count += 1

                except Exception as e:
                    log_f.write(f"Error during bypass attempt: {e}\n")
                    return {"status": "failed", "message": str(e), "url": url}

            # Successful bypass
            cookies_data = driver.cookies()
            cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies_data}
            cookies = {
                "cf_clearance": cookies_dict.get("cf_clearance", None),
                "user_agent": driver.user_agent,
            }

            # Save cookies
            with open(cookies_file_path, "w") as f:
                json.dump(cookies, f, indent=2)

            log_f.write(f"Cloudflare bypass successful for {url}\n")
            return {"status": "success", "cookies": cookies, "url": url}

    except Exception as e:
        with open(log_file_path, "a") as log_f:
            log_f.write(f"Unexpected error in bypass_cloudflare: {e}\n")
        return {"status": "failed", "message": str(e), "url": url}
    finally:
        if "driver" in locals():
            driver.close()


def _find_cloudflare_button(driver):
    """
    Directly / Recursively search for Cloudflare verification button through shadow roots.

    Args:
        driver (ChromiumPage): The Chromium webdriver

    Returns:
        WebElement or None: The Cloudflare verification button
    """

    def search_shadow_root_recursively(element):
        if element.shadow_root:
            if element.shadow_root.child().tag == "iframe":
                return element.shadow_root.child()

            input_ele = element.shadow_root.ele("tag:input")
            if input_ele and not "NoneElement" in str(type(input_ele)):
                return input_ele

        for child in element.children():
            result = search_shadow_root_recursively(child)
            if result and not "NoneElement" in str(type(result)):
                return result

        return None

    eles = driver.eles("tag:input")
    for ele in eles:
        if "name" in ele.attrs.keys() and "type" in ele.attrs.keys():
            if "turnstile" in ele.attrs["name"] and ele.attrs["type"] == "hidden":
                button = (
                    ele.parent()
                    .shadow_root.child()("tag:body")
                    .shadow_root("tag:input")
                )
                if not "NoneElement" in str(type(button)):
                    return button

    body_ele = driver.ele("tag:body")
    button = search_shadow_root_recursively(body_ele)

    return button
