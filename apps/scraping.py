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

    # Scrape latest news
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
        # if df has two columns do not use header or borders in html.  site recently updated.
        if len(df.columns)==2:
            df.columns=['Description', 'Mars']
            df.set_index('Description', inplace=True)
            df.index.name = None
            df_html = df.to_html(header=False, classes='table-striped table-hover table-condensed table-responsive', justify='center', border=0)
        # else assumes three columns returned in df (originally what was returned from site).  use header and borders in html table.
        else:
            df.columns=['Description', 'Mars', 'Earth']
            df.set_index('Description', inplace=True)
            df.index.name = None
            df_html = df.to_html(classes='table-striped table-hover table-condensed table-responsive', justify='center')
        
        # return the html
        return df_html

    # Scrape Mars Hemisphere images and titles
    
    # function to pull Mars Hemishpheres
    def mars_hemishpheres(browser):
        
        # Visit URL
        url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
        browser.visit(url)
        # Add wait time for page to load
        browser.is_element_present_by_xpath("//div[@class='description']/a/h3", wait_time=1)
        
        mars_hemi_list = []     
        
        # function to scrape images and title
        def scrape_hemi(index_num):
                
            # click on link for hemishpere site
            browser.find_by_xpath("//div[@class='description']/a/h3")[index_num].click()
            # add wait
            browser.is_element_present_by_css("img.wide-image", wait_time=1)
                
            # Parse the resulting html with soup
            html = browser.html
            img_soup = BeautifulSoup(html, 'html.parser')
                
            # Get the title for the image
            title = img_soup.select_one('h2.title').get_text()
                
            # Find the relative image url for full image
            img_url_rel_full = img_soup.select_one('img.wide-image').get("src")
                
            # Use the base URL to create an absolute URL
            img_url_full = f'https://astrogeology.usgs.gov{img_url_rel_full}'
                
            # Find the relative image url for thumb image
            img_thumb_rel = img_soup.select_one('img.thumb').get("src")
                
            # Use the base URL to create an absolute URL
            img_thumb = f'https://astrogeology.usgs.gov{img_thumb_rel}'
            
            # Go back to site
            browser.back()
            # Optional delay for loading the page
            browser.is_element_present_by_xpath("//div[@class='description']/a/h3", wait_time=1)
            
            hemi_results = {"index": index_num, "title": title, "img_url": img_url_full, "img_thumb": img_thumb}
         
            return mars_hemi_list.append(hemi_results)
            
        # Add try/except for error handling
        try:
            # run scape_hemi function for four hemisphere images and titles
            for index_num in range(0,4):
                scrape_hemi(index_num)

        except BaseException as e:
            print(str(e))
            traceback.print_exc()
            return None

        return mars_hemi_list

    # set news title and paragraph variables
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "mars_hemispheres": mars_hemishpheres(browser),
      "last_modified": dt.datetime.now()
    }
 
    # quit the splinter browser
    browser.quit()

    return data

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
