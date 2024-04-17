import urllib.request
from bs4 import BeautifulSoup
import urllib

pic_searches = ['tuber+magnatum']
for pic_search in pic_searches:
    url = str(r'https://commons.wikimedia.org/w/api.php?action=query&prop=images|categories&+generator=search&gsrsearch=File:') + str(pic_search) + str('&format=jsonfm&origin=*&iiprop=extmetadata&iiextmetadatafilter=ImageDescription|ObjectName')
    response = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(response, 'html.parser')
    spans = soup.find_all('span', {'class': 's2'})
    lines = [span.get_text() for span in spans]
    new_list = [item.replace('"', '') for item in lines]
    new_list2 = [x for x in new_list if x.startswith('File')]
    new_list3 = [x[5:] for x in new_list2]
    new_list4 = [x.replace(' ','_') for x in new_list3]
    print(new_list4)