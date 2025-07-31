from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import csv

# Constants
filename = 'saved_search.csv'

def initialize_selenium():
    driver = webdriver.Chrome()
    driver.implicitly_wait(3)

    return driver

def land_main_page(driver):
    url = "https://www.amazon.com.mx"
    driver.get(url)

def search_product(driver, search):
    my_element = driver.find_element('id','twotabsearchtextbox')
    my_element.send_keys(search + Keys.ENTER)

def get_all_elements_in_page(driver):
    elements = driver.find_elements(By.XPATH, '//div[@role="listitem"]')

    return elements

def get_product_info(element):

    elements_per_product = element.text.split('\n')

    product = {}
    for x in elements_per_product:
        if 'vendido' in x.lower():
            continue
        elif 'patrocinado' in x.lower():
            continue
        elif 'amazon' in x.lower():
            continue
        else:
            product['name'] = x
            break
            
    for x in elements_per_product:
        if '$' in x:
            product['price'] = x
            break
            
    for x in elements_per_product:
        if '/' in x:
            x = x[:-1]
            product['price_per_unit'] = x
            break
    
    try:
        img = element.find_element(By.XPATH, './/img[contains(@class, "s-image")]')
        img_url = img.get_attribute('src')
        product['image_url'] = img_url
    except:
        print('no image url found')

    try:
        product_url = element.get_attribute("data-asin")
        product_url =  'https://www.amazon.com.mx/dp/' + product_url
        product['product_url'] = product_url
    except:
        print('no product url found')

    return product

def save_products_to_csv(products):
    try:
        products_old = []
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                products_old.append(row)
        
        products_old.extend(products)

        if products_old:
            with open(filename, 'w') as file:
                fieldnames = ['name', 'price', 'price_per_unit', 'image_url', 'product_url']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(products_old)
        else:
            print('nothing new to write')

    except Exception as e:
        print(e)
        print('creating new csv...')
        with open(filename, 'w') as file:
            fieldnames = ['name', 'price', 'price_per_unit', 'image_url', 'product_url']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)

def main():
    page = 1
    search = 'miel'

    driver = initialize_selenium()
    land_main_page(driver)
    search_product(driver, search)


    while True:
        print('page:', page)
        time.sleep(5)
        elements = get_all_elements_in_page(driver)
        products_new = []
        for element in elements:
            product = get_product_info(element)
            products_new.append(product)

        save_products_to_csv(products_new)

        try:
            next_btn = driver.find_element(By.XPATH, '//a[contains(@class,"s-pagination-next") and not(contains(@aria-disabled,"true"))]')
            next_btn.click()
            page += 1
        except:
            print("No more pages. Done.")
            break

    driver.quit()

if __name__ == '__main__':
    main()
    # products_old = []
    # with open(filename, 'r') as file:
    #     reader = csv.DictReader(file)
    #     for row in reader:
    #         products_old.append(row)

    # #products_old.extend([])
    # print(len(products_old))
