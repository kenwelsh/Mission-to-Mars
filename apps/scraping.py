# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import traceback
from IPython.display import HTML

def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)

    def mars_news(browser):
        
        # Visit the mars nasa news site
        url = 'https://mars.nasa.gov/news/'
        browser.visit(url)

        # Optional delay for loading the page
        browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

        # set up the HTML parser
        html = browser.html
        news_soup = BeautifulSoup(html, 'html.parser')
        
        # Add try/except for error handling
        try:
            slide_elem = news_soup.select_one('ul.item_list li.slide')

            # Use the parent element to find the first `a` tag and save it as `news_title`
            news_title = slide_elem.find("div", class_='content_title').get_text()

            # Use the parent element to find the paragraph text
            news_paragraph = slide_elem.find('div', class_="article_teaser_body").get_text()

        except AttributeError:
            return None, None

        return news_title, news_paragraph

    # Image Scraping
    def featured_image(browser):
        # Visit URL
        url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
        browser.visit(url)

        # Find and click the full image button
        full_image_elem = browser.find_by_id('full_image')
        full_image_elem.click()

        # Find the more info button and click that
        browser.is_element_present_by_text('more info', wait_time=1)
        more_info_elem = browser.links.find_by_partial_text('more info')
        more_info_elem.click()

        # Parse the resulting html with soup
        html = browser.html
        img_soup = BeautifulSoup(html, 'html.parser')

        try:
            # Find the relative image url
            img_url_rel = img_soup.select_one('figure.lede a img').get("src")

        except AttributeError:
            return None

        # Use the base URL to create an absolute URL
        img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

        return img_url

    # Scrape Mars Facts

    def mars_facts():
        # Add try/except for error handling
        try:
            # use 'read_html" to scrape the facts table into a dataframe
            df = pd.read_html('http://space-facts.com/mars/')[0]
            
        except BaseException as e:
            print(str(e))
            traceback.print_exc()
            return None

        # Assign columns and set index of dataframe
        # if statement to handle if scrape returns two columns.  site recently updated.
        if len(df.columns)==2:
            df.columns=['Description', 'Mars']
            df.set_index('Description', inplace=True)
            df.index.name = None
            df_html = df.to_html(header=False, classes='table-striped table-hover table-condensed table-responsive', justify='center', border=0)
        else:
            df.columns=['Description', 'Mars', 'Earth']
            df.set_index('Description', inplace=True)
            df.index.name = None
            df_html = df.to_html(classes='table-striped table-hover table-condensed table-responsive', justify='center')
        
        # convert the dataframe to html
        return df_html

    # set news title and paragraph variables
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "last_modified": dt.datetime.now()
    }
    
    # quit the splinter browser
    browser.quit()

    return data

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
