import re
import json
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
company = 'Accenture Federal Services Locations'

script = """
function addGlobalStyle(css) {
    var head, style;
    head = document.getElementsByTagName('head')[0];
    if (!head) { return; }
    style = document.createElement('style');
    style.type = 'text/css';
    style.innerHTML = css;
    head.appendChild(style);
}

addGlobalStyle("#HardsellOverlay {display:none !important;}");
addGlobalStyle("body {overflow:auto !important; position: initial !important}");

window.addEventListener("scroll", event => event.stopPropagation(), true);
window.addEventListener("mousemove", event => event.stopPropagation(), true);
"""

employer_page_url = f"https://www.glassdoor.com/searchsuggest/typeahead?numSuggestions=8&source=GD_V2&version=NEW&rf=full&fallback=token&input={company}"
driver.get(employer_page_url)
employer_page_source = driver.page_source
soup = BeautifulSoup(employer_page_source, 'html.parser')

pre_tag = soup.find('pre')
if pre_tag:
    json_data = json.loads(pre_tag.text)

    if json_data and isinstance(json_data, list) and len(json_data) > 0:
        first_item = json_data[0]
        employer = first_item.get('suggestion', '')
        employerId = first_item.get('employerId', '')

page = 1
parsing = True

while parsing:
    url = f'https://www.glassdoor.com/Reviews/{employer}-Reviews-E{employerId}_P{page}.htm?filter.iso3Language=eng&filter.employmentStatus=REGULAR&filter.employmentStatus=PART_TIME&filter.employmentStatus=CONTRACT&filter.employmentStatus=INTERN&filter.employmentStatus=FREELANCE'
    driver.get(url)

    driver.implicitly_wait(5)
    driver.execute_script(script)
    html = driver.page_source
    match = re.search(r'apolloState":\s*({.+?})};', html)

    if match:
        data_json = match.group(1)
        data_dict = json.loads(data_json)

        data = data_dict
        employer_reviews_query = None
        for key, value in data['ROOT_QUERY'].items():
            if 'employerReviewsRG' in key:
                employer_reviews_query = value
                break
        if employer_reviews_query:
            reviews = employer_reviews_query.get('reviews', [])

            for review in reviews:
                date_of_review = review['reviewDateTime']
                pros = review['pros']
                cons = review['cons']
                current_or_former_employee = "Former Employee" if not review['isCurrentJob'] else "Current Employee"
                time_employed = review['lengthOfEmployment']
                location = review['location']
                advice_to_management = review['advice']
                recommend = review['ratingRecommendToFriend']

            button = driver.find_element(By.CSS_SELECTOR, ".nextButton[data-test='pagination-next']")
            if button.is_enabled():
                page += 1
            else:
                parsing = False

    else:
        print("JSON data not found in the HTML.")
        break


driver.quit()
