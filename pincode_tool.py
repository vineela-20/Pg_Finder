import subprocess
from playwright.sync_api import sync_playwright

subprocess.run(
    ["python", "-m", "playwright", "install", "chromium"],
    check=True
)

import re

def search_google_maps(pincode):
    with sync_playwright() as p:
        # OPEN BROWSER
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400,"height": 900})
        # OPEN GOOGLE MAPS
        try:
            page.goto(
                "https://www.google.com/maps",
                wait_until="domcontentloaded",
                timeout=60000
            )
        except PlaywrightTimeoutError:
            #print("Google Maps navigation timed out.")
            # Sometimes Maps has actually opened even
            # though Playwright reports a timeout.
            #print("Current URL:", page.url)
            if "google.com/maps" not in page.url:
                browser.close()
                return
        #print("Google Maps opened")
        # =============================================
        # SEARCH BOX
        search_box = page.locator('input[role="combobox"][name="q"]')
        search_box.wait_for(
        state="visible",
        timeout=30000
        )
        # =============================================
        # SEARCH PINCODE
        search_box.fill(f"PG near {pincode}")
        search_box.press("Enter")
        # Wait for Google Maps results
        page.wait_for_timeout(5000)
        # =============================================
        # RESULTS FEED
        
        
    
        results_feed = page.locator('div[role="feed"]')

        try:
            results_feed.wait_for(
                state="visible",
                timeout=60000
            )
        except Exception:
            print("Results feed not found.")
            print("Current URL:", page.url)

            page.screenshot(path="maps_error.png", full_page=True)

            return []

        # =============================================
        # STORE ALL RESULTS
        # =============================================

        all_results = {}

        previous_total = 0

        no_new_results_count = 0

        # =============================================
        # SCROLL RESULTS
        # =============================================

        for scroll in range(30):

            #print(f"\n========== SCROLL {scroll + 1} ==========")

            cards = results_feed.locator(
                'div[role="article"]'
            )

            card_count = cards.count()

            #print("Cards currently in DOM:",card_count)

            # =========================================
            # EXTRACT CURRENT CARDS
            # =========================================

            for i in range(card_count):

                try:

                    card = cards.nth(i)

                    # =================================
                    # NAME
                    # =================================

                    name = ""

                    name_locator = card.locator(
                        'a[href*="/maps/place/"]'
                    )

                    if name_locator.count() > 0:

                        name = (
                            name_locator
                            .first
                            .get_attribute(
                                "aria-label"
                            )
                            or ""
                        )

                    if not name:

                        continue

                    # =================================
                    # UNIQUE PLACE LINK
                    # =================================

                    place_link = ""

                    if name_locator.count() > 0:

                        place_link = (
                            name_locator
                            .first
                            .get_attribute(
                                "href"
                            )
                            or ""
                        )

                    unique_key = (
                        place_link
                        if place_link
                        else name
                    )

                    # =================================
                    # SKIP DUPLICATES
                    # =================================

                    if unique_key in all_results:

                        continue

                    # =================================
                    # CARD TEXT
                    # =================================

                    text = card.inner_text()

                    # =================================
                    # RATING
                    # =================================

                    rating = ""

                    rating_locator = card.locator(
                        'span[role="img"][aria-label*="stars"]'
                    )

                    if rating_locator.count() > 0:

                        rating_label = (
                            rating_locator
                            .first
                            .get_attribute(
                                "aria-label"
                            )
                            or ""
                        )

                        rating_match = re.search(
                            r"(\d+(?:\.\d+)?)",
                            rating_label
                        )

                        if rating_match:

                            rating = (
                                rating_match
                                .group(1)
                            )

                    # =================================
                    # PHONE
                    # =================================
                    phone=""
                    phone_match = re.search(r'(?<!\d)(?:0\d{5}\s\d{5}|[6-9]\d{9})(?!\d)', text)

                    if phone_match:
                        phone = phone_match.group(0).strip()
                    else:
                        phone = "Phone number not available"
                    # =================================
                    # WEBSITE
                    # =================================

                    website = "No"

                    website_locator = card.locator(
                        'a[aria-label*="Website"], '
                        'a[data-value="Website"]'
                    )

                    if website_locator.count() > 0:

                        website = "Yes"

                    # =================================
                    # ADDRESS
                    # =================================



                    address = ""

                    lines = [
                        line.strip()
                        for line in text.split("\n")
                        if line.strip()
                    ]

                    address_keywords = [
                        "road",
                        "rd",
                        "street",
                        "layout",
                        "nagar",
                        "cross",
                        "sector",
                        "phase",
                        "bengaluru",
                        "bangalore",
                        "560"
                    ]

                    for line in lines:

                        lower_line = line.lower()

                        # Ignore obvious fields

                        if name.lower() in lower_line:
                            continue

                        if "star" in lower_line:
                            continue

                        if "open" in lower_line:
                            continue

                        if "closed" in lower_line:
                            continue

                        if "website" in lower_line:
                            continue

                        if "directions" in lower_line:
                            continue

                        if lower_line == "call":
                            continue

                        if any(
                            keyword in lower_line
                            for keyword in address_keywords
                        ):

                            address = line
                            break

                    # =================================
                    # SAVE RESULT
                    # =================================

                    all_results[unique_key] = {

                        "Name": name,

                        "Phone": phone,

                        "Rating": rating,

                        "Website": website,

                        "Address": address
                    }

                

                except Exception as e:

                    print(
                        f"Error processing card {i}:",
                        e
                    )

            # =========================================
            # CURRENT TOTAL
            # =========================================

            current_total = len(
                all_results
            )


            # =========================================
            # SCROLL DOWN
            # =========================================

            results_feed.evaluate(
                """
                (element) => {
                    element.scrollTop =
                        element.scrollHeight;
                }
                """
            )

            '''print("Scrolling...")'''

            page.wait_for_timeout(3000)

            # =========================================
            # CHECK FOR NEW RESULTS
            # =========================================

            if current_total == previous_total:

                no_new_results_count += 1

            else:

                no_new_results_count = 0

            previous_total = current_total

            # =========================================
            # STOP CONDITION
            # =========================================

            if no_new_results_count >= 3:
                break
        # =============================================
        # FINAL RESULT COUNT
        # =============================================
        
        browser.close()
        return all_results        
        

        

        




