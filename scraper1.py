import requests, re, shutil, pymysql
from bs4 import BeautifulSoup 
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys 
import time 
  
#url of the page we want to scrape 
rooturl = "http://185.121.204.150/ChethamLibrary/#/search?TitCollectionTitle=Belle%20Vue%20Gardens"
imroot = "/path/to/store/images"
  
# initiating the webdriver. Parameter includes the path of the webdriver. 
driver = webdriver.Chrome('/usr/local/bin/chromedriver')  


def im_dl(im_url):
    filename = imroot+im_url.split("=")[-1]+".jpg"
    r = requests.get(im_url, stream = True)
    if r.status_code == 200:
        r.raw.decode_content = True
        with open(filename,'wb') as f:
            shutil.copyfileobj(r.raw, f)      
        print('Image sucessfully Downloaded: ',filename)
    else:
        print('Image Couldn\'t be retreived')


def scrapePage(url):
    print("scraping", url)
    driver.get(url)  
    time.sleep(5)   
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    metadata = {}
    imgs = soup.find_all('img', {"class":"img-responsive"})
    imgkeys = []
    for im in imgs:
        ikey = im['src'].split('&')[2].split('=')[1]
        if ikey not in imgkeys:
            imgkeys.append(ikey)
    for imk in imgkeys:
        if 'Images' in metadata:
            metadata['Images'].append("http://185.121.204.150/ChethamLibrary/php/request.php?request=Multimedia&method=fetch&key="+imk)
        else:
            metadata['Images'] = ["http://185.121.204.150/ChethamLibrary/php/request.php?request=Multimedia&method=fetch&key="+imk]
    p_divs = soup.find_all('p', {'class':'ng-binding ng-scope'})
    if p_divs !=None:
        for p in p_divs:
            if 'Subject' in metadata:
                metadata["Subject"].append(p.text.strip())
            else:
                metadata["Subject"] = [p.text.strip()]
    txt_divs = soup.find('div', {'class' : 'resultcontent'})
    vals = txt_divs.find_all('span')
    spans = ["Title", "Summary", "Date", "Notes"]
    for v in vals:
        vtxt = v.text
        vtxt = vtxt.replace('\n', '')
        if ":" in vtxt:
            if vtxt.split(':')[0] in spans:
                if vtxt.split(':')[1] != ' ':
                    content = re.findall(r'"([^"]*)"', vtxt.split(':')[1])
                    if len(content) > 0:
                        content = content[0]
                    else:
                        content = vtxt.split(':')[1]
                    metadata[vtxt.split(':')[0]] = content.strip()
    return metadata

def scrapeRoot(rooturl):
    driver.get(rooturl)   
    time.sleep(5)  
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    link_divs = soup.find_all('div', {'class' : 'row result ng-scope'})
    for ld in link_divs:
        link = ld.find_all('a')
        for l in link:
            item_url = ("http://185.121.204.150/ChethamLibrary/"+l['href'])
            pg_data = scrapePage(item_url)
            #add pg_data to db (to-do)
            print(pg_data)
            #to download images:
            #for im in pg_data['Images']:
            #   im_dl(im)


scrapeRoot(rooturl)
driver.close() # closing the webdriver
