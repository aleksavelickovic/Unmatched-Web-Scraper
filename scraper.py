import base64
import json
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import undetected_chromedriver as uc

SLEEP_TIME = 25  # Prilagoditi broj shodno brzini vase internet konekcije


def get_matching_requests(browser):
    events = browser.get_log("performance")
    results = []

    for e in events:
        message = json.loads(e["message"])["message"]
        method = message.get("method", "")
        params = message.get("params", {})
        # response = params.get("response", {})
        # status = response.get("statusText")
        # print("STATUS ODGOVORA JE: " + status)

        if method == "Network.responseReceived":
            url = params["response"]["url"]
            if "https://www.umleague.net/api/analytics/getHeroResultsByMap" in url:  # TODO vrati samo uspesne odgovore!
                results.append(params["requestId"])

    return results


def get_response_body(browser, request_id):
    try:
        body = browser.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
        data = body["body"]
        if body.get("base64Encoded", False):
            data = base64.b64decode(data).decode("utf-8")
        return data
    except:
        return None


def test_scrape_page():
    options = uc.ChromeOptions()
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    browser = uc.Chrome(options=options)
    browser.execute_cdp_cmd("Network.enable", {})
    browser.implicitly_wait(10)

    browser.get("https://www.umleague.net/fighterstats")
    sleep(15)

    select_hero_element = browser.find_element(By.ID, "selectHero")
    browser.execute_script("arguments[0].scrollIntoView();", select_hero_element)
    select_hero = Select(select_hero_element)

    for i, option in enumerate(select_hero.options):
        if i >= 2:  ## Zakomentarisati ove dve linije koda
            break  ## Ako je cilj uzeti JSON za sve <option> tagove
        option.click()
        sleep(SLEEP_TIME)

    request_ids = get_matching_requests(browser)

    print(f"Captured {len(request_ids)} API calls")

    for idx, req_id in enumerate(request_ids, start=1):
        body = get_response_body(browser, req_id)
        if body:
            filename = f"hero_results_{idx}.json"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(body)
            print(f"[+] Saved → {filename}")

    browser.quit()
