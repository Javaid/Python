import requests
from bs4 import BeautifulSoup
import mysql.connector
import re

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="yellowpages"
)
mycursor = mydb.cursor()


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


def saveLinks(link):
    sql = 'insert into links(link, site) values(%s, %s)'
    val = [(link, 'ups')]
    mycursor.executemany( sql, val )
    mydb.commit()

def saveDetails(ups_name, ups_address,ups_additional_dir,ups_phone, ups_fax,ups_email):
    sql = "insert into ups_details ( ups_name, ups_address,ups_additional_dir,ups_phone, ups_fax,ups_email) values(%s, %s,%s, %s,%s, %s)"
    val = [(ups_name, ups_address,ups_additional_dir,ups_phone, ups_fax,ups_email)]
    mycursor.executemany( sql, val )
    mydb.commit()

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

# getLinks()
mycursor.execute("SELECT * FROM links")
myresult = mycursor.fetchall()

for x in myresult:
    link = (x[1])
    id =str( x[0])
    print(id + ":" + link)
    getDetails( link )
