import base64
import json
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import undetected_chromedriver as uc

SLEEP_TIME = 25  # Prilagoditi broj shodno brzini vase internet konekcije


def get_matching_requests(browser):
    requests = browser.get_log("performance")  # Spisak svih HTTP zahteva
    results = []

    for request in requests:
        message = json.loads(request["message"])["message"]  # Deserijalizacija
        method = message.get("method", "")
        params = message.get("params", {})
        # response = params.get("response", {})
        # status = response.get("statusText")
        # print("STATUS ODGOVORA JE: " + status)

        if method == "Network.responseReceived":  # Uzimamo samo HTTP odgovore, ne i zahteve
            url = params["response"][
                "url"]  # Ako se URL zahteva poklapa sa linijom dole, uzecemo ga u obzir (ovako filtriramo zahteve tako da uzmemo samo one koji se dese kada promenimo combobox
            if "https://www.umleague.net/api/analytics/getHeroResultsByMap" in url:  # TODO vrati samo uspesne odgovore!
                results.append(params["requestId"])

    return results


def get_response_body(browser, request_id):
    body = browser.execute_cdp_cmd("Network.getResponseBody",
                                   {"requestId": request_id})  # CDP komanda za hvatanje tela odgovora
    data = body["body"]  # body koji komanda vraca je zapravo JSON sa dodatnim podacima,
    # pa nam treba specificno polje body

    if body.get("base64Encoded", False):
        data = base64.b64decode(data).decode("utf-8")  # Dekodiramo body iz cega god je kodirano (Bice da njihov backend
        # vraca body enkodiran pomocu Brotli algoritma)
    return data


def test_scrape_page():
    options = uc.ChromeOptions()  # Osnovne Chromium opcije
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})  # Belezimo sve performance logove

    browser = uc.Chrome(options=options)  # Instanciramo Chromium webDriver
    browser.execute_cdp_cmd("Network.enable", {})  # Omogucavamo CDP (Chrome Devtools Protocol)
    browser.implicitly_wait(10)  # webDriver po default-u ceka 10 sekundi na izvrsenje komande

    browser.get("https://www.umleague.net/fighterstats")
    sleep(15)  # Cekamo malo duze da se ucita stranica

    select_hero_element = browser.find_element(By.ID, "selectHero")
    browser.execute_script("arguments[0].scrollIntoView();", select_hero_element)
    select_hero = Select(select_hero_element)

    for i, option in enumerate(select_hero.options):
        if i >= 2:  ## Zakomentarisati ove dve linije koda
            break  ## Ako je cilj uzeti JSON za sve <option> tagove
        option.click()
        sleep(SLEEP_TIME)

    requestIds = get_matching_requests(browser)

    for requestNo, requestId in enumerate(requestIds, start=1):
        body = get_response_body(browser, requestId)
        filename = f"hero_results_{requestNo}.json"
        with open(filename, "w", encoding="utf-8") as f:  # Upisujemo body HTTP response-a u fajl
            f.write(body)
        print(f"Sacuvan JSON:  {filename}")

    browser.quit()
