import time
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


URL = "https://www.upwork.com/ab/profiles/search/?category_uid=531770282580668418&page=1&top_rated_plus=yes"
driver = webdriver.Chrome(executable_path="chromedriver")
driver.get(URL)
time.sleep(15)
driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
time.sleep(5)

while True:
    last_scroll_height = driver.execute_script("return document.documentElement.scrollHeight")
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    time.sleep(2)
    new_scroll_height = driver.execute_script("return document.documentElement.scrollHeight")
    if new_scroll_height == last_scroll_height:
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "next-icon")))
            if not next_button.is_displayed():
                break
            next_button.click()
            time.sleep(2)
        except (NoSuchElementException, TimeoutException):
            break


soup = BeautifulSoup(driver.page_source, 'html.parser')

freelancers_data = []

data = soup.find_all('div', {'class': 'up-card-section up-card-hover'})

for freelancer in data:
    name = freelancer.find('div', {"class": "identity-name"}).text.strip()
    role = freelancer.find('p', {'class': 'my-0 freelancer-title'}).text.strip()
    country = freelancer.find('span', {'class': 'd-inline-block vertical-align-middle'}).text.strip()
    hourly_rate = freelancer.find('div', {'data-qa': 'rate'}).text.strip()
    earned_amount = freelancer.find('span', {'data-test': 'earned-amount-formatted'})
    total_earns = earned_amount.text.strip() if earned_amount else ""
    job_success_score = freelancer.find('span', {'class': 'up-job-success-text'}).text.strip()\
        .replace('\n', '').replace('            ', '')
    badge = freelancer.find('span', {'class': 'status-text d-flex top-rated-badge-status'}).text.strip()
    bio = freelancer.find('div', {'class': 'up-line-clamp-v2 clamped'}).text.strip()
    company_name_elem = freelancer.find('div', {'class': 'd-flex align-items-center up-btn-link'})
    company_name = company_name_elem.text.strip() if company_name_elem else ""
    company_earn_elem = freelancer.find('div', {'class': 'ml-10 agency-box-stats'})
    company_earn = company_earn_elem.text.strip() if company_earn_elem else ""
    profile_links = soup.find_all('div', {'class': 'd-flex justify-space-between align-items-start'})
    split_data = str(profile_links).split()
    sliced_data = split_data[9:10]
    split_sliced_data = sliced_data[0].split("=")
    final = split_sliced_data[1]
    final = final.replace('"', '')
    profile_link = 'https://www.upwork.com/freelancers/' + final
    company_links = soup.find_all(
        'div', {'class': 'cfe-ui-freelancer-tile-agency-box-legacy mt-5 mt-10 agency-box-legacy--link'})
    split_data = str(company_links).split(" ")
    sliced_data = split_data[5:6]
    split_sliced_data = sliced_data[0].split('=')
    sliced_split_sliced_data = split_sliced_data[1:]
    cleaned_data = sliced_split_sliced_data[0].strip('[]').strip('"')
    company_link = 'https://www.upwork.com/agencies/' + cleaned_data
    raw_htmls = freelancer.prettify()

    freelancer_data = {
        "Name": name,
        "Role": role,
        "Country": country,
        "Profile_Link": profile_link,
        "Hourly_Rate": hourly_rate,
        "Total_Earned": total_earns,
        "Job_Success_Score": job_success_score,
        "Badge": badge,
        "Bio": bio,
        "Company_Name": company_name,
        "Company_Earn": company_earn,
        "Raw_HTML": raw_htmls,
        "Company_Link": company_link
    }

    freelancers_data.append(freelancer_data)

driver.quit()

for freelancer_data in freelancers_data:
    print(freelancer_data)


filename = 'freelancers_data20.csv'
with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Name', 'Role', 'Country', 'Profile_Link', 'Hourly_Rate', 'Total_Earned', 'Job_Success_Score',
                  'Badge', 'Bio', 'Company_Name', 'Company_Earn', 'Raw_HTML', 'Company_Link']

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(freelancers_data)

print(f"Data saved to {filename}")
