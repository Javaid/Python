## Taxes UPS store crawler 

This code will work in two steps
- Crawl and store all the links into link table
- Grab the store links one by one from Link table and insert the UPS Store information into the ups_details table

#Sequence of Execution 
- getLinks()
- getDetails()

Import the required libraries
```python

import requests
from bs4 import BeautifulSoup
import mysql.connector
import re
```
## Connect with Database (mySQL)
```python
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="yellowpages"
)
mycursor = mydb.cursor()

```
## The getLinks() and saveLinks() functions will get all the links and store into links table
```python
def getLinks():
    URL = 'https://locations.theupsstore.com/tx'
    page = requests.get( URL )
    soup = BeautifulSoup( page.content, 'html.parser' )
    ups_lis = soup.find_all( 'li', class_='Directory-listItem' )
    for li in ups_lis:
        numbers = li.find( 'span' ).text.strip()
        pattern = re.compile( r'\s+' )
        numbers = numbers.replace( '(', '' ).replace( ')', '' )
        total = re.sub( pattern, '', numbers )
        if total == "1":
            link1 = li.find( 'a' )['href'].strip()
            link1 = "https://locations.theupsstore.com/" + link1.replace( "../tx/", '' )
            saveLinks( link1 )
        else:
            href = li.find( 'a' )['href'].strip()
            link = "https://locations.theupsstore.com/" + href.replace( "../tx/", '' )
            page = requests.get( link )
            soup = BeautifulSoup( page.content, 'html.parser' )
            second_page_links = soup.find_all( 'div', class_='Teaser-link' )
            for links in second_page_links:
                link = "https://locations.theupsstore.com/tx/" + links.find( 'a' )['href'].strip().replace( "../tx/",
                                                                                                            '' )
                saveLinks( link )


```

```python
def saveLinks(link):
    sql = 'insert into links(link, site) values(%s, %s)'
    val = [(link, 'ups')]
    mycursor.executemany( sql, val )
    mydb.commit()
```
## The saveDetails() and getDetails() functions will grab and save the Store's details into the ups_detail table e.g. UPS Name, Addres, phone no etc.
```python
def saveDetails(ups_name, ups_address,ups_additional_dir,ups_phone, ups_fax,ups_email):
    sql = "insert into ups_details ( ups_name, ups_address,ups_additional_dir,ups_phone, ups_fax,ups_email) values(%s, %s,%s, %s,%s, %s)"
    val = [(ups_name, ups_address,ups_additional_dir,ups_phone, ups_fax,ups_email)]
    mycursor.executemany( sql, val )
    mydb.commit()

```
```python

def getDetails(link):
    page = requests.get( link )
    soup = BeautifulSoup( page.content, 'html.parser' )
    ups_name = soup.find( 'h2', class_='Heading--3' ).text
    ups_address = soup.find( 'address', class_="c-address" ).text
    if soup.find( 'div', class_="NAP-additionalDirections" ):
        ups_additional_dir = soup.find( 'div', class_="NAP-additionalDirections" ).text
    else:
        ups_additional_dir=""
    ups_phone = soup.find( 'span', id="telephone" ).text
    ups_fax = soup.find( 'span', class_="c-phone-number-span" ).text
    ups_email = soup.find( 'div', class_="NAP-emailWrapper" ).text.replace("Email:", "")
    saveDetails( ups_name, ups_address, ups_additional_dir, ups_phone, ups_fax, ups_email )

```
## Functions calling
```python

# getLinks()
mycursor.execute("SELECT * FROM links")
myresult = mycursor.fetchall()

for x in myresult:
    link = (x[1])
    id =str( x[0])
    print(id + ":" + link)
    getDetails( link )

