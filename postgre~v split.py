import os
from urllib.request import urlopen as uReq
import urllib.error
from bs4 import BeautifulSoup as soup
import pandas as pd
import json

versions = {
    
}

# Connecting the sqlite3 database
import sqlite3
from sqlite3 import Error

con = sqlite3.connect('postgre_versions.db')
print('connected....')
cursorObj = con.cursor()

url_downloads = "https://www.postgresql.org/ftp/source/";
url_majorversions = "https://www.postgresql.org/support/versioning/";

# Global arrays of dictionary
minor_versions_array = []
major_versions_array = []
major_versions = []
supported_versions = []

major_version_count = 0
# opening the connection
try:
    uClient = uReq(url_downloads)
    downloads_html = uClient.read()
    uClient = uReq(url_majorversions)
    all_versions_html = uClient.read()
    uClient.close()

    download_page_soup = soup(downloads_html, "html.parser")
    major_version_page_soup = soup(all_versions_html, "html.parser")

    all_version_table = download_page_soup.find_all(id="pgContentWrap")
    major_version_table = major_version_page_soup.find_all("table")

    try:
        # Truncating the table
        sql = ''' DELETE FROM major_versions '''
        cursorObj.execute(sql)
        con.commit()

        print("Major versions table truncated....\n")
        # major versions details
        df_major_versions = pd.read_html(str(major_version_table))
        # major versions count
        major_version_count = int(len(df_major_versions[0]["Version"]))
        #initialising the json array
        versions['major_versions'] = []
        for i in range(int(len(df_major_versions[0]["Version"]))):
            version_name = df_major_versions[0]["Version"][i]
            version_url = url_downloads + "v" + str(version_name) + "/";
            # majorversions array
            major_versions.append("v" + str(version_name))
            version_minor = df_major_versions[0]["Current minor"][i]
            version_first_release = df_major_versions[0]["First Release"][i]
            version_final_release = df_major_versions[0]["Final Release"][i]
            version_supported = df_major_versions[0]["Supported"][i]
            if str(df_major_versions[0]["Supported"][i]) == "Yes":
                supported_versions.append(str(version_name))
            # updating the json array of major_version
            versions['major_versions'].append({
                "id": str(i),
                "name" : str(version_name),
                "current minor": str(version_minor),
                "download url": str(version_url),
                "first release": str(version_first_release),
                "final release": str(version_final_release),
                "supported": str(version_supported)
            })
            version_details = [version_name, version_minor, version_url, version_first_release, version_final_release,
                               version_supported]
            print(version_details)
            major_versions_array.append(version_details)
            sql = ''' INSERT INTO major_versions(id,version_name,current_minor,download,first_release,final_release,support) VALUES(?,?,?,?,?,?,?) '''
            cursorObj.execute(sql, (
                i + 1, version_name, version_minor, version_url, version_first_release, version_final_release,
                version_supported))
        # Major Version
        # commiting the changes
        con.commit()
        print('\nChanges commited in major versions table.....\n')

        # minor version details
        df_downloads = pd.read_html(str(all_version_table))
        # Truncating the table
        sql = ''' DELETE FROM minor_versions '''
        cursorObj.execute(sql)
        con.commit()
        print("Minor versions table truncated....\n")
        # initialising the json array
        versions['minor_versions'] = []
        # Ignores the parent directorys
        for i in range(int(len(df_downloads[0][0]))):
            if i == 0:
                continue
            # version_name
            version = df_downloads[0][0][i];
            if(int((version.split(".")[0])[1:])<=9):
                if(float(version[1:4]) >= float(supported_versions[len(supported_versions)-1])):
                    version_support = "Yes"
                else: 
                    version_support = "No"
            else:
                if(float(version[1:5]) >= float(supported_versions[len(supported_versions)-1])):
                    version_support = "Yes"
                else: 
                    version_support = "No"    
            # version_url
            version_download_url = url_downloads + version + "/";
            
            if version in major_versions:
                continue
            else:
                # Getting details of the versions one by one
                try:
                    uClient = uReq(version_download_url)
                    version_html = uClient.read()
                    uClient.close()
                except:
                    print("Error in Version Details picking!")
                
                version_page_soup = soup(version_html, "html.parser")
                version_date_table = version_page_soup.find_all(id="pgFtpContent")
                current_version_dates = pd.read_html(str(version_date_table))
                
                # version_date
                version_date = current_version_dates[0][1][1]
                
                # creating a temperory array 
                current_version_details = [version, version_download_url, version_date,version_support]
                print(current_version_details)
                
                # Appending to the minor_versions_array
                minor_versions_array.append(current_version_details)
                cursorObj.execute(''' SELECT COUNT(*) FROM minor_versions''')
                count = cursorObj.fetchone()[0]
                # Pushing into json array
                versions['minor_versions'].append({
                    "id": str(count+1),
                    "name": str(version),
                    "download url": str(version_download_url),
                    "release date": str(version_date),
                    "support": str(version_support)
                })
                sql = ''' INSERT INTO minor_versions(id,version_name,final_release,download,support) VALUES(?,?,?,?,?)'''
                cursorObj.execute(sql, (count + 1, version, version_date, version_download_url,version_support))
                con.commit()
        print('\nChanges commited in minor versions table....\n')
    except:
        pass
except urllib.error.URLError as e:
    print("Error in page request!")

with open('postgre_versions_json.json', 'w') as outfile:
    json.dump(versions, outfile)
# Closing the connection
con.close()
print("json file and database updated!....")