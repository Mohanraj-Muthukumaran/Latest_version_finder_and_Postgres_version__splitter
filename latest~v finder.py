from urllib.request import urlopen as uReq
import urllib.error 
from bs4 import BeautifulSoup as soup
import pandas as pd

print("Note: For better results use 'Camel_Case' words and instead of ' ' use '_'. ")
search = input('Name of the Software: ')
url = "https://en.wikipedia.org/wiki/"+search.replace(" ","_")
# opening the connection
try:
    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()

    page_soup = soup(page_html,"html.parser")

    info_table = page_soup.find('table',class_="infobox vevent")

    try:
        df = pd.read_html(str(info_table))

        for i in range(int(len(df[0][0]))):
            if 'Stable release(s) [±]' in str(df[0][0][i]):
                print("The Available Stable Version is: "+df[0][1][i+1])
            elif 'Stable release' in str(df[0][0][i]):
                print("The Available Stable Version is: "+df[0][1][i])
            if 'Website' in str(df[0][0][i]):
                print("For More Info Visit: "+df[0][1][i])       

    except:
        print("No Such Software Found! or Try with Proper Name of the Software!")
    

except urllib.error.URLError as e:
    print("Oops!.. Something went wrong! or No Internet Connection!")
    print("Hint: For better results use full software name in 'Camel_Case' words and instead of ' ' use '_'. ")
    

