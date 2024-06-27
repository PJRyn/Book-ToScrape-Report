from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.firefox.service import Service
import re

# Open browser and set up splinter
my_service = Service()
browser = Browser('firefox', service=my_service)

# Go to URL
url = 'https://books.toscrape.com/'
browser.visit(url)

# Arrays for data
titles = []
prices = []
ratings = []
stocks = []

# open browser and go to the website
html = browser.html
soup = BeautifulSoup(html, 'html.parser')
books = soup.find_all('article', class_='product_pod')
# iterate through each page collecting each entry collecting book information
for x in range(1, 50):
    for book in books:
        title = book.h3.a["title"]
        price = book.find("p", class_="price_color").get_text().strip()
        rating = book.p["class"][1]
        stock = book.find("p", class_="instock availability").get_text().strip()
        titles.append(title)
        prices.append(price)
        ratings.append(rating)
        stocks.append(stock)
    if browser.links.find_by_partial_text('next'):
        browser.links.find_by_partial_text('next').click()

# Crate dataframe from scraped data
scrape_df = pd.DataFrame(
                        {'Title':  titles,
                        'Prices':   prices,
                        'Ratings':  ratings,
                        'Stocks':   stocks})
scrape_df

# I took each category listed and make a list
temListOfCategories = ["Travel","Mystery","Historical_Fiction","Sequential_Art","Classics","Philosophy","Romance","Womens_Fiction","Fiction","Childrens","Religion","Nonfiction","Music","Default","Science_Fiction","Sports_and_Games","Add_a_comment","Fantasy","New_Adult","Young_Adult","Science","Poetry","Paranormal","Art","Psychology","Autobiography","Parenting","Adult_Fiction","Humor","Horror","History","Food_and_Drink","Christian_Fiction","Business","Biography","Thriller","Contemporary","Spirituality","Academic","Self_Help","Historical","Christian","Suspense","Short_Stories","Novels","Health","Politics","Cultural","Erotica","Crime"]

# Go back to homepage
browser.visit(url)
# Here we find the URL links to each category
Section = soup.find('ul', class_='nav nav-list')
linksSection = Section.find_all('a')
linksSectionStr = []
for x in linksSection:
    linksSectionStr.append(str(x))
# Now we clean each link so we can easier add it when we seach each category
categoriesLinks = []
for x in range(len(linksSectionStr)):
    linksSectionStr[x] = re.sub(' +', '', linksSectionStr[x])
    linksSectionStr[x] = re.sub('\n', '', linksSectionStr[x])
    linksSectionStr[x] = re.findall(r'"([^"]*)"', linksSectionStr[x])
    categoriesLinks.append(linksSectionStr[x][0])
#Pop the first one since it was "Books" category which contained all books and wasnt needed
categoriesLinks.pop(0)

# Now go through each category and collect the books within them
generaCollection = []
genraTitles = []
for x in range(len(temListOfCategories)):
    browser.visit(url + categoriesLinks[x])
    title1 = []
    page = True
    while page == True:
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        books = soup.find_all('article', class_='product_pod')
        for book in books:
            title = book.h3.a["title"]
            title1.append(title)
        if browser.links.find_by_partial_text('next'):
            browser.links.find_by_partial_text('next').click()
        else:
            page = False
    generaCollection.append(title1)

# Quit out the browser as it is no longer needed
browser.quit()

# Now create a data frame using the categories and titles
categoryDF = pd.DataFrame(columns=['Title','Category'])
for i in range(len(generaCollection)):
    for j in range(len(generaCollection[i])):
        row = pd.DataFrame({'Title':[generaCollection[i][j]], 'Category':[temListOfCategories[i]]})
        categoryDF = pd.concat([categoryDF, row], ignore_index=True)

# Merge this with the other scraped data to add the categories for each book
pd.merge(scrape_df, categoryDF, how='inner', on='Title')

# Export dataframe as a CSV
scrape_df.to_csv("Resources/scrapedBooks.csv",index=False)