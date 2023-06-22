#!/usr/bin/env python3

import requests 
from bs4 import BeautifulSoup 
from playwright.sync_api import Playwright, sync_playwright
import os

# Get the country name and zip code from the user
country_name = input("Enter the country name: ")
zip_code = input("Enter the zip code: ")

# Define the URLs to scrape for proxies
urls = [f'https://www.us-proxy.org/{zip_code}-proxy-list.html', f'https://hidemy.name/en/proxy-list/?country={country_name}', 'https://proxyscrape.com/free-proxy-list']

# Define the headers to fake our request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

# Define the function to scrape the proxies
def scrape_proxies(playwright: Playwright, url):
    # Launch the browser
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Set the headers
    page.set_extra_http_headers(headers)
    
    # Navigate to the URL
    page.goto(url)
    
    # Get the table with the proxies
    if url.startswith('https://www.us-proxy.org/'):
        table = page.query_selector('#proxylisttable')
        rows = table.query_selector_all('tr')
        cells = [row.query_selector_all('td') for row in rows]
        proxies = [f'{cell[0].inner_text()}:{cell[1].inner_text()}' for cell in cells if len(cell) > 0]
    elif url.startswith('https://hidemy.name/'):
        table = page.query_selector('#content-section-2')
        rows = table.query_selector_all('tr')
        cells = [row.query_selector_all('td') for row in rows]
        proxies = [f'{cell[0].inner_text()}:{cell[1].inner_text()}' for cell in cells if len(cell) > 0]
    elif url.startswith('https://proxyscrape.com/'):
        table = page.query_selector('#table3')
        rows = table.query_selector_all('tr')
        cells = [row.query_selector_all('td') for row in rows]
        proxies = [f'{cell[0].inner_text()}:{cell[1].inner_text()}' for cell in cells if len(cell) > 0]
    
    # Close the browser
    browser.close()
    
    # Return the proxies
    return proxies

# Define the function to test the proxies
def test_proxies(proxies):
    working_proxies = []
    for proxy in proxies:
        try:
            response = requests.get('https://httpbin.org/ip', proxies={'http': proxy, 'https': proxy}, timeout=10)
            if response.status_code == 200:
                working_proxies.append(proxy)
        except:
            pass
    return working_proxies

# Scrape the proxies
all_proxies = []
with sync_playwright() as playwright:
    for url in urls:
        proxies = scrape_proxies(playwright, url)
        all_proxies.extend(proxies)

# Test the proxies
working_proxies = test_proxies(all_proxies)

# Create the proxy result folder if it doesn't exist
if not os.path.exists('proxy result'):
    os.makedirs('proxy result')

# Define the file path for the output
file_path = 'proxy result/proxygd.txt'

# Write the working proxies to the file
with open(file_path, 'w') as file:
    for proxy in working_proxies:
        file.write(proxy + '\n')
