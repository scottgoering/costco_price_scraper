"""
Module: price_scraper

This module defines functions for scraping data from sales posts on a website,
storing the data in a CSV file, and updating the database with the scraped information.

Functions:
- scrape_website(url): Scrape data from a website given its URL.
- get_sales_post_urls(): Get relevant links for sales posts.
- scrape_items_from_posts(post_urls_list): Scrape items from lists of sales posts.
- store_data_csv(data, filename): Store data in a CSV file.
- run_price_scraper(): Orchestrates the price scraper workflow.

Constants:
- CSV_FILENAME (str): Default CSV file name for storing scraped data.

Note: The 'requests' library is used for making HTTP requests,
and 'BeautifulSoup' is used for HTML parsing.
"""
import csv
import re
from bs4 import BeautifulSoup
import requests

from costco_price_scraper.price_scraper import items_db
from costco_price_scraper.price_scraper.regex import parse_product_string

CSV_FILENAME = "scraped_coupon_data.csv"


def scrape_coupons(url):
    """
    Scrape data from a website.

    Args:
        url (str): The URL of the website.

    Returns:
        list: A list of lists containing scraped data.
    """
    cookies = {
        '_abck': '5E2FC32104AC7077E7171FA64E87C602~0~YAAQhHZAF6tGUpaUAQAAemzLrg2QD+a9rJ++leEPjL9uy31koefpeTE5PWYlNGm4g9fbTv1kQ3S2R6ugosuLSLzQYQUqCAj44xfukUyllsVL/3i+wh6tNpx9rnafXLP4otXr2XpTFv9DxYPS1/Mxw+9xd/PJIrpjuDUYFA7jr5N2hxDExNu/TvUj7267d5oHB4bcbYCANk7XmciDj7X9mm/WYtSJxIT2zIwJhH+UOx6OykT4zSSqCZoj6nGxNxMYaDF1o5wFGeGUWvR8Kh5IjHiC1TNb8DfmhI3RUbpDLllVl9p/K/lRpdxyu9TRM0j85AtKPrf/Y+jzLmkTcQgw8Pu8vUzH1HuTa9c1BhQFw/rAVXqY/qTmK8ra7Zvj/p1MIn717frg3GkKPljnazf+zLBL8d/oqogXCQl8Kr21PYA44zq25fCAyYS8HCknKYTusXQ4svuZ8Gjtok+vwiX11IElcE8RaMZY990lOLauvLasEUolFv+Qmdff0vQ/GwECMfn+AFICx5/vksBNYHsXVDCUr5m1VqiJAQiQjw7rfVTF4q9b+x/ydcyYOkDJdpcVD3NnNqR93VMlIbiYkUrg8XTH0BV9d5gWlefv6w6kJ8j89JdC7FJy/V9NJNitsKV4lh0mTweuefvVXK6zYLJTkm9OAMoAzdtXKVGiPM0fSYGMi0lB~-1~-1~-1',
        'invCheckPostalCode': '66018',
        'invCheckStateCode': 'KS',
        'invCheckCity': 'De%20Soto',
        'OptanonConsent': 'isGpcEnabled=0&datestamp=Tue+Jan+28+2025+15%3A22%3A51+GMT-0600+(Central+Standard+Time)&version=202401.2.0&isIABGlobal=false&hosts=&consentId=7abc10f3-6b52-4b9c-b11a-3f48cd7ac474&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CSPD_BG%3A1%2CC0004%3A1%2CBG117%3A1&AwaitingReconsent=false&browserGpcFlag=0',
        'STORELOCATION': '{%22storeLocation%22:{%22zip%22:%2266215%22%2C%22city%22:%22Lenexa%22}}',
        'forterToken': '5bd734b449394161b2125c31e4b79282_1733981096015_183_UAS9_21ck',
        'C_WHLOC': 'USKS',
        'nonce': 'UhnQJTKmSa0ARSAP',
        '_cc': 'AYEJ%2By8qtKNqlud9pAV4Lana',
        '_cid_cc': 'AYEJ%2By8qtKNqlud9pAV4Lana',
        'AMCV_97B21CFE5329614E0A490D45%40AdobeOrg': '179643557%7CMCIDTS%7C20073%7CMCMID%7C26150934958236172266131276550005386395%7CMCAID%7CNONE%7CMCOPTOUT-1734313198s%7CNONE%7CvVersion%7C5.5.0',
        'mbox': 'session#b0e6eb97c8ad445dbea2c7ed280469b3#1719795766|PC#b0e6eb97c8ad445dbea2c7ed280469b3.35_0#1783038706',
        'WAREHOUSEDELIVERY_WHS': '{%22distributionCenters%22:[%221254-3pl%22%2C%221321-wm%22%2C%221559-3pl%22%2C%22283-wm%22%2C%22561-wm%22%2C%22725-wm%22%2C%22731-wm%22%2C%22758-wm%22%2C%22759-wm%22%2C%22847_0-cor%22%2C%22847_0-cwt%22%2C%22847_0-edi%22%2C%22847_0-ehs%22%2C%22847_0-membership%22%2C%22847_0-mpt%22%2C%22847_0-spc%22%2C%22847_0-wm%22%2C%22847_1-cwt%22%2C%22847_1-edi%22%2C%22847_d-fis%22%2C%22847_lg_ntx-edi%22%2C%22847_NA-cor%22%2C%22847_NA-pharmacy%22%2C%22847_NA-wm%22%2C%22847_ss_u359-edi%22%2C%22847_wp_r455-edi%22%2C%22951-wm%22%2C%22952-wm%22%2C%229847-wcs%22]%2C%22groceryCenters%22:[%221665-bd%22]%2C%22nearestWarehouse%22:{%22catalog%22:%22349-wh%22}%2C%22pickUpCenters%22:[]}',
        'bvUserToken': 'b4a4cef9d2fb07693bd49ff2227bade3646174653d323032352d30312d3238267573657269643d66363535336130612d633062352d343639642d386664382d65353563306361613062393926656d61696c616464726573733d73636f7474676f6572696e6740676d61696c2e636f6d264d656d6265724e756d6265723d313131383034393630383639',
        'wcMember': 'dbe5e8fe040361228e283e31cfeac658%2C1%2CZ00020%2CZ010%2C1%2C1%2CE0002%2CDEFAULT%2C111804960869%2Cscottgoering%40gmail.com%2C0',
        'sso-pharmacy-session': 'TJ1gMM4HfwYabi%2FxSmZ0nQ%3D%3D',
        'kmsi': 'true_1738099355884',
        'AKA_A2': 'A',
        'akavpau_zezxapz5yf': '1738099673~id=8b12d51334b37cc47076c214ee593b48',
        'akaas_AS01': '2147483647~rv=88~id=ed17146e223121c70e447a8e0e0e89f9',
        'bm_ss': 'ab8e18ef4e',
        'bm_s': 'YAAQhHZAFwFIUpaUAQAAbqjLrgL8FwFnSn+H5177B9iS7+gdZPqfwhZ7k6fSYa8iXFE/JJDP00PLPbAQRJtd3RF9jGtsTMPZwvt3jNWj2cZJ/99vrdp8Vtni4hEoRjn5BSvR385ArqwylxWF+zRYXCyIc73B+SmlRgd+UG3jaIIN7UQrVn4vopBERrlK9KtJ8CUoX0L8Kd3J76j5ndMPAgaWTtAJs1HmYMUS/wucH5gs3338U9Fsh1NZg1vMvboIxox+Z9CmYBMWmBc+ZPcHQ79Xs1CAF9SWoYpSnyYYMLJ0E4c/3twv2+e/q26x2bBHP7O9crDzXqtiob6Lv3gv+CxvHavgRkgfZ6jNSWJY6Go2ILSX5PaqtsX4OqBcB0WApU0FZVFYnYz5ql94/FODW4Br4HxyGUAHzlGVDH+e6KoQk5IqQaS443nSVKR/n9z2Yxh6wk+MgiH38Q==',
        'bm_so': '21BE7412E22634E7B56B5144456A750EA5B881B4FE156F6A777A12046A176CD0~YAAQhHZAF6JGUpaUAQAA62rLrgJDlvDC1LpIxn0qvZPyq32Y9XDHsNQrOfWzLbgYk/BFatNaliPc8zA9fo6G6A08JEEK182KCG7O5XLocVNLTNpirTdUZZalK5ZHqWY9YhHK6Ed3ziy+0tjRmz21RIlwCM69S4snRPcDy1H9sD7nl8fNwRKb/BiufMMp78vA35LyU3BjKqvdGjJKKL7g9roUqJo1FTGBieSLZnb1V7oZ5H7wvRij18uFV/gfI6rjTQWDIuGykj2G9RrPB7C5ZnfLXaQ2g35PF4uMGHSv3+WdzedRF8EnJVCB18Xt/cTwPl6LtbWxJYpxIDKEEL1+0rzZj5lxs2ZcYDJAR/1hQ7UnZco5dvWYBsGMHShAEzin6t/TDdgCbcBflvWlVNJD0NTf4l4vJ7Q8cIJ+j7oc16w2N1B/Qs+YL4z5LCBwupgb/i85d8mrW90CclwQxw==',
        'bm_sz': '824B0DEF5226614C074871CA08F7999D~YAAQhHZAFwNIUpaUAQAAbqjLrhrgaRRW4q6/ImjNeLLdas/g59MUq5+Lj9wGVBmitI5nUTiAKtpAUosCVjDj1jiVOWS8QjL05etk+0CdXG19n5xUkQTlQ0MILJNCiZ63zzksoCBB9fVg4QeK3pNvkHxiZhK1F6G9dJ5EuloHDPSMgQfOPrJh5z+RkPwhGk/k6wyNJ6g1FTmmvxkiHpFThdnqSJ6QmkHo1kM42P3OnKK/3+dTPAN+xmW9TWB2kszYVFUjZfC91XtNPonJta7TENX7KuSH7vSFrOgr6Gh4xqNeslo6y/jFZpWHrFD8LTPq7OFG1DymQdHT379Rg/DPSSTfuKapJll4eQVRZjw+FWZG0XqeQI8IN1GHWgVKbYujthCogrc9mP7OYkS9Bc5YhgUfmw==~3159859~4404788',
        'BCO': 'pm2',
        'JSESSIONID': '0000a55b0jy6PXqqBfLQWH7smBW:1g39pnqv4',
        'WC_PERSISTENT': 'IzkkpBV7s%2Fxy1KnY1fBHn4FURcOZOJ5%2Be0TZX7rvZzc%3D%3B2025-01-28+13%3A22%3A35.888_1356716386780-3608036_10301',
        'costco_f_p_LOCATIONS': '%7B%22contract%22%3A%7B%22id%22%3A%22%22%2C%22switch%22%3A%22true%22%7D%7D',
        'rrDisabledPref': '0',
        'rrStoreFlag': '0',
        'hashedUserId': 'dbe5e8fe040361228e283e31cfeac658',
        'costcoHashId': 'e4ab14885a40e3979795fe445caf985c9aa48537ae9bb805e3d75d0d104b52b4',
        'memberPrimaryPostal': '66018',
        'memberPrimaryStateCode': 'KS',
        'cartCountCookie': '2',
        'checkoutMemberTier': 'Z00020',
        'mSign': '1',
        'WC_SESSION_ESTABLISHED': 'true',
        'WC_AUTHENTICATION_28438614': '28438614%2CjDRDDQcNWFJ%2BOni8A3daeMxeRRJUedN%2BfRBrEbn562s%3D',
        'WC_ACTIVEPOINTER': '-1%2C10301',
        'WC_USERACTIVITY_28438614': '28438614%2C10301%2C0%2Cnull%2C1738099355889%2C1738102955889%2Cnull%2Cnull%2Cnull%2Cnull%2C1830977664%2C4dXQoUVLEdG1i36%2BsGNvrXgliMDjCC%2BqiRHZc1FGRkVNsYIWnDznMXuk3hvDssd4BHDV8ylyBnrMPv3%2Fj07u%2BxM4CS1%2FbjTYFy00kIpT4LEGBth4%2Berj0G3RjvXs35jytvLpDk00VrFqjXhU2WKV4%2B%2Fwdxc%2FvGXu67xBA5EshjyoWaBnp5uthBQT6SrEu6WBRcEn9rOIHhN2Q%2FCUbN2Y7sX2o27F8ywNROR8Wukeyda6hvcNlSyok0NlSwBFQGukSrY9yVewpW31MX8flGqFtA%3D%3D',
        'ak_bmsc': '020FEF50D35D79310BD2681FE63D8482~000000000000000000000000000000~YAAQhHZAF9JGUpaUAQAAonHLrhrN7EAh7gwRlXRfilkVSIrEz9X/bObQULeUJtMUW3hAYzad5LwCJfizPqSqEje34QMyBzIFM3r+RK361RtNFNkNDgAi384ZIjOfGbadOsQUuuFEvTL6HgBljdd1e5qUyok7aruPAt0RvhBOf8SdWG8VxuiY06KY5biY9ovk8IZ/5i4QiUuR3jowl2tqdLy3Wj5YvSIiIpEIDA8OtyJeJ+6GLSxRONbKRr4OqOrv0UTBzPrjNa1ooI8Sq9Oe540rcqI5Ri+1+zDIDzUxzJPJYblYuWB0kn/7Ia5+ZpECxfkpx+hP3fVBFAtZUOnushthjn6Fbj0qhIFxds5HLUOcdcpwCAJC+7SKg6AIsbZg+/2+gv1OP+Es',
        'kmsi_58fc2cee86dd3b5c60cebf95d121e30cdbb303d693dac877a9a2594b08c270d9': 'ygVmt+FtXdX3575n/MOKPn55mM6SqOlDWAjeBV69mscVDHWLwUTsLT6PyYmuNGJFe9Dn+cjXgOFvVPsnZ032qhw9apzh9wGZxLXkSs5VO1E=',
        'bm_lso': '21BE7412E22634E7B56B5144456A750EA5B881B4FE156F6A777A12046A176CD0~YAAQhHZAF6JGUpaUAQAA62rLrgJDlvDC1LpIxn0qvZPyq32Y9XDHsNQrOfWzLbgYk/BFatNaliPc8zA9fo6G6A08JEEK182KCG7O5XLocVNLTNpirTdUZZalK5ZHqWY9YhHK6Ed3ziy+0tjRmz21RIlwCM69S4snRPcDy1H9sD7nl8fNwRKb/BiufMMp78vA35LyU3BjKqvdGjJKKL7g9roUqJo1FTGBieSLZnb1V7oZ5H7wvRij18uFV/gfI6rjTQWDIuGykj2G9RrPB7C5ZnfLXaQ2g35PF4uMGHSv3+WdzedRF8EnJVCB18Xt/cTwPl6LtbWxJYpxIDKEEL1+0rzZj5lxs2ZcYDJAR/1hQ7UnZco5dvWYBsGMHShAEzin6t/TDdgCbcBflvWlVNJD0NTf4l4vJ7Q8cIJ+j7oc16w2N1B/Qs+YL4z5LCBwupgb/i85d8mrW90CclwQxw==^1738099356158',
        'CriteoSessionUserId': 'bacd1bc8a51a464e82d604699761150f',
        'bm_mi': 'DB82C5873CFED6B2A2796A944305674B~YAAQhHZAF/ZGUpaUAQAA+nXLrhpXbrDPLM9+FgZOYC9jgjDvfCnzFmcEI74rwVT3qkrJgx94UveqOUBU2naHPehP5UR4Op7cH8I0qD7X26WGfuy8w5CnLVrTwPQZ0bglRorxdwqQV4qUq3v33IWt7Pi9Cqi2zLf8xG7WqE0pyxkxeZ9sknpnJpbyvnG2QajnjOJKqvlz74wbWThaosov6t/kZaQwd0NI7AD2NV8S1sVT/F1kfxwzRFwp8NEaAFWS0SlwYmigJNmQPfw/smAhlpDARA03ro6iNk2eR/4zLM71Bif6rIxFa+K0whPCURjW8SWl1qdc~1',
        'bm_sv': '9CF7F88DC4E647130EB1E7239BBDA339~YAAQhHZAFwJIUpaUAQAAbqjLrhrUgQj8lIlgtpEIqGE6MHIyOn63BF5pL9sew/Kvx5Y3tp1Hn7f+/A3WDBTWPz8LCecfkQFcg2iDV8z36SD6pFxDmbkS7MBTpPjaooEBPRrielCS/O238p/lVC7EIkwQYlnKXUJ1IQm3MSeFEtqR+YGdTYCYFk/SXtImp1aeW9hgceEik0McGpluL1P9a6VT7WoV/+B7W73LErHqx2b4IhreK+MDH6X3z9NdDS3D~1',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Connection': 'keep-alive',
        # 'Cookie': '_abck=5E2FC32104AC7077E7171FA64E87C602~0~YAAQhHZAF6tGUpaUAQAAemzLrg2QD+a9rJ++leEPjL9uy31koefpeTE5PWYlNGm4g9fbTv1kQ3S2R6ugosuLSLzQYQUqCAj44xfukUyllsVL/3i+wh6tNpx9rnafXLP4otXr2XpTFv9DxYPS1/Mxw+9xd/PJIrpjuDUYFA7jr5N2hxDExNu/TvUj7267d5oHB4bcbYCANk7XmciDj7X9mm/WYtSJxIT2zIwJhH+UOx6OykT4zSSqCZoj6nGxNxMYaDF1o5wFGeGUWvR8Kh5IjHiC1TNb8DfmhI3RUbpDLllVl9p/K/lRpdxyu9TRM0j85AtKPrf/Y+jzLmkTcQgw8Pu8vUzH1HuTa9c1BhQFw/rAVXqY/qTmK8ra7Zvj/p1MIn717frg3GkKPljnazf+zLBL8d/oqogXCQl8Kr21PYA44zq25fCAyYS8HCknKYTusXQ4svuZ8Gjtok+vwiX11IElcE8RaMZY990lOLauvLasEUolFv+Qmdff0vQ/GwECMfn+AFICx5/vksBNYHsXVDCUr5m1VqiJAQiQjw7rfVTF4q9b+x/ydcyYOkDJdpcVD3NnNqR93VMlIbiYkUrg8XTH0BV9d5gWlefv6w6kJ8j89JdC7FJy/V9NJNitsKV4lh0mTweuefvVXK6zYLJTkm9OAMoAzdtXKVGiPM0fSYGMi0lB~-1~-1~-1; invCheckPostalCode=66018; invCheckStateCode=KS; invCheckCity=De%20Soto; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Jan+28+2025+15%3A22%3A51+GMT-0600+(Central+Standard+Time)&version=202401.2.0&isIABGlobal=false&hosts=&consentId=7abc10f3-6b52-4b9c-b11a-3f48cd7ac474&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CSPD_BG%3A1%2CC0004%3A1%2CBG117%3A1&AwaitingReconsent=false&browserGpcFlag=0; STORELOCATION={%22storeLocation%22:{%22zip%22:%2266215%22%2C%22city%22:%22Lenexa%22}}; forterToken=5bd734b449394161b2125c31e4b79282_1733981096015_183_UAS9_21ck; C_WHLOC=USKS; nonce=UhnQJTKmSa0ARSAP; _cc=AYEJ%2By8qtKNqlud9pAV4Lana; _cid_cc=AYEJ%2By8qtKNqlud9pAV4Lana; AMCV_97B21CFE5329614E0A490D45%40AdobeOrg=179643557%7CMCIDTS%7C20073%7CMCMID%7C26150934958236172266131276550005386395%7CMCAID%7CNONE%7CMCOPTOUT-1734313198s%7CNONE%7CvVersion%7C5.5.0; mbox=session#b0e6eb97c8ad445dbea2c7ed280469b3#1719795766|PC#b0e6eb97c8ad445dbea2c7ed280469b3.35_0#1783038706; WAREHOUSEDELIVERY_WHS={%22distributionCenters%22:[%221254-3pl%22%2C%221321-wm%22%2C%221559-3pl%22%2C%22283-wm%22%2C%22561-wm%22%2C%22725-wm%22%2C%22731-wm%22%2C%22758-wm%22%2C%22759-wm%22%2C%22847_0-cor%22%2C%22847_0-cwt%22%2C%22847_0-edi%22%2C%22847_0-ehs%22%2C%22847_0-membership%22%2C%22847_0-mpt%22%2C%22847_0-spc%22%2C%22847_0-wm%22%2C%22847_1-cwt%22%2C%22847_1-edi%22%2C%22847_d-fis%22%2C%22847_lg_ntx-edi%22%2C%22847_NA-cor%22%2C%22847_NA-pharmacy%22%2C%22847_NA-wm%22%2C%22847_ss_u359-edi%22%2C%22847_wp_r455-edi%22%2C%22951-wm%22%2C%22952-wm%22%2C%229847-wcs%22]%2C%22groceryCenters%22:[%221665-bd%22]%2C%22nearestWarehouse%22:{%22catalog%22:%22349-wh%22}%2C%22pickUpCenters%22:[]}; bvUserToken=b4a4cef9d2fb07693bd49ff2227bade3646174653d323032352d30312d3238267573657269643d66363535336130612d633062352d343639642d386664382d65353563306361613062393926656d61696c616464726573733d73636f7474676f6572696e6740676d61696c2e636f6d264d656d6265724e756d6265723d313131383034393630383639; wcMember=dbe5e8fe040361228e283e31cfeac658%2C1%2CZ00020%2CZ010%2C1%2C1%2CE0002%2CDEFAULT%2C111804960869%2Cscottgoering%40gmail.com%2C0; sso-pharmacy-session=TJ1gMM4HfwYabi%2FxSmZ0nQ%3D%3D; kmsi=true_1738099355884; AKA_A2=A; akavpau_zezxapz5yf=1738099673~id=8b12d51334b37cc47076c214ee593b48; akaas_AS01=2147483647~rv=88~id=ed17146e223121c70e447a8e0e0e89f9; bm_ss=ab8e18ef4e; bm_s=YAAQhHZAFwFIUpaUAQAAbqjLrgL8FwFnSn+H5177B9iS7+gdZPqfwhZ7k6fSYa8iXFE/JJDP00PLPbAQRJtd3RF9jGtsTMPZwvt3jNWj2cZJ/99vrdp8Vtni4hEoRjn5BSvR385ArqwylxWF+zRYXCyIc73B+SmlRgd+UG3jaIIN7UQrVn4vopBERrlK9KtJ8CUoX0L8Kd3J76j5ndMPAgaWTtAJs1HmYMUS/wucH5gs3338U9Fsh1NZg1vMvboIxox+Z9CmYBMWmBc+ZPcHQ79Xs1CAF9SWoYpSnyYYMLJ0E4c/3twv2+e/q26x2bBHP7O9crDzXqtiob6Lv3gv+CxvHavgRkgfZ6jNSWJY6Go2ILSX5PaqtsX4OqBcB0WApU0FZVFYnYz5ql94/FODW4Br4HxyGUAHzlGVDH+e6KoQk5IqQaS443nSVKR/n9z2Yxh6wk+MgiH38Q==; bm_so=21BE7412E22634E7B56B5144456A750EA5B881B4FE156F6A777A12046A176CD0~YAAQhHZAF6JGUpaUAQAA62rLrgJDlvDC1LpIxn0qvZPyq32Y9XDHsNQrOfWzLbgYk/BFatNaliPc8zA9fo6G6A08JEEK182KCG7O5XLocVNLTNpirTdUZZalK5ZHqWY9YhHK6Ed3ziy+0tjRmz21RIlwCM69S4snRPcDy1H9sD7nl8fNwRKb/BiufMMp78vA35LyU3BjKqvdGjJKKL7g9roUqJo1FTGBieSLZnb1V7oZ5H7wvRij18uFV/gfI6rjTQWDIuGykj2G9RrPB7C5ZnfLXaQ2g35PF4uMGHSv3+WdzedRF8EnJVCB18Xt/cTwPl6LtbWxJYpxIDKEEL1+0rzZj5lxs2ZcYDJAR/1hQ7UnZco5dvWYBsGMHShAEzin6t/TDdgCbcBflvWlVNJD0NTf4l4vJ7Q8cIJ+j7oc16w2N1B/Qs+YL4z5LCBwupgb/i85d8mrW90CclwQxw==; bm_sz=824B0DEF5226614C074871CA08F7999D~YAAQhHZAFwNIUpaUAQAAbqjLrhrgaRRW4q6/ImjNeLLdas/g59MUq5+Lj9wGVBmitI5nUTiAKtpAUosCVjDj1jiVOWS8QjL05etk+0CdXG19n5xUkQTlQ0MILJNCiZ63zzksoCBB9fVg4QeK3pNvkHxiZhK1F6G9dJ5EuloHDPSMgQfOPrJh5z+RkPwhGk/k6wyNJ6g1FTmmvxkiHpFThdnqSJ6QmkHo1kM42P3OnKK/3+dTPAN+xmW9TWB2kszYVFUjZfC91XtNPonJta7TENX7KuSH7vSFrOgr6Gh4xqNeslo6y/jFZpWHrFD8LTPq7OFG1DymQdHT379Rg/DPSSTfuKapJll4eQVRZjw+FWZG0XqeQI8IN1GHWgVKbYujthCogrc9mP7OYkS9Bc5YhgUfmw==~3159859~4404788; BCO=pm2; JSESSIONID=0000a55b0jy6PXqqBfLQWH7smBW:1g39pnqv4; WC_PERSISTENT=IzkkpBV7s%2Fxy1KnY1fBHn4FURcOZOJ5%2Be0TZX7rvZzc%3D%3B2025-01-28+13%3A22%3A35.888_1356716386780-3608036_10301; costco_f_p_LOCATIONS=%7B%22contract%22%3A%7B%22id%22%3A%22%22%2C%22switch%22%3A%22true%22%7D%7D; rrDisabledPref=0; rrStoreFlag=0; hashedUserId=dbe5e8fe040361228e283e31cfeac658; costcoHashId=e4ab14885a40e3979795fe445caf985c9aa48537ae9bb805e3d75d0d104b52b4; memberPrimaryPostal=66018; memberPrimaryStateCode=KS; cartCountCookie=2; checkoutMemberTier=Z00020; mSign=1; WC_SESSION_ESTABLISHED=true; WC_AUTHENTICATION_28438614=28438614%2CjDRDDQcNWFJ%2BOni8A3daeMxeRRJUedN%2BfRBrEbn562s%3D; WC_ACTIVEPOINTER=-1%2C10301; WC_USERACTIVITY_28438614=28438614%2C10301%2C0%2Cnull%2C1738099355889%2C1738102955889%2Cnull%2Cnull%2Cnull%2Cnull%2C1830977664%2C4dXQoUVLEdG1i36%2BsGNvrXgliMDjCC%2BqiRHZc1FGRkVNsYIWnDznMXuk3hvDssd4BHDV8ylyBnrMPv3%2Fj07u%2BxM4CS1%2FbjTYFy00kIpT4LEGBth4%2Berj0G3RjvXs35jytvLpDk00VrFqjXhU2WKV4%2B%2Fwdxc%2FvGXu67xBA5EshjyoWaBnp5uthBQT6SrEu6WBRcEn9rOIHhN2Q%2FCUbN2Y7sX2o27F8ywNROR8Wukeyda6hvcNlSyok0NlSwBFQGukSrY9yVewpW31MX8flGqFtA%3D%3D; ak_bmsc=020FEF50D35D79310BD2681FE63D8482~000000000000000000000000000000~YAAQhHZAF9JGUpaUAQAAonHLrhrN7EAh7gwRlXRfilkVSIrEz9X/bObQULeUJtMUW3hAYzad5LwCJfizPqSqEje34QMyBzIFM3r+RK361RtNFNkNDgAi384ZIjOfGbadOsQUuuFEvTL6HgBljdd1e5qUyok7aruPAt0RvhBOf8SdWG8VxuiY06KY5biY9ovk8IZ/5i4QiUuR3jowl2tqdLy3Wj5YvSIiIpEIDA8OtyJeJ+6GLSxRONbKRr4OqOrv0UTBzPrjNa1ooI8Sq9Oe540rcqI5Ri+1+zDIDzUxzJPJYblYuWB0kn/7Ia5+ZpECxfkpx+hP3fVBFAtZUOnushthjn6Fbj0qhIFxds5HLUOcdcpwCAJC+7SKg6AIsbZg+/2+gv1OP+Es; kmsi_58fc2cee86dd3b5c60cebf95d121e30cdbb303d693dac877a9a2594b08c270d9=ygVmt+FtXdX3575n/MOKPn55mM6SqOlDWAjeBV69mscVDHWLwUTsLT6PyYmuNGJFe9Dn+cjXgOFvVPsnZ032qhw9apzh9wGZxLXkSs5VO1E=; bm_lso=21BE7412E22634E7B56B5144456A750EA5B881B4FE156F6A777A12046A176CD0~YAAQhHZAF6JGUpaUAQAA62rLrgJDlvDC1LpIxn0qvZPyq32Y9XDHsNQrOfWzLbgYk/BFatNaliPc8zA9fo6G6A08JEEK182KCG7O5XLocVNLTNpirTdUZZalK5ZHqWY9YhHK6Ed3ziy+0tjRmz21RIlwCM69S4snRPcDy1H9sD7nl8fNwRKb/BiufMMp78vA35LyU3BjKqvdGjJKKL7g9roUqJo1FTGBieSLZnb1V7oZ5H7wvRij18uFV/gfI6rjTQWDIuGykj2G9RrPB7C5ZnfLXaQ2g35PF4uMGHSv3+WdzedRF8EnJVCB18Xt/cTwPl6LtbWxJYpxIDKEEL1+0rzZj5lxs2ZcYDJAR/1hQ7UnZco5dvWYBsGMHShAEzin6t/TDdgCbcBflvWlVNJD0NTf4l4vJ7Q8cIJ+j7oc16w2N1B/Qs+YL4z5LCBwupgb/i85d8mrW90CclwQxw==^1738099356158; CriteoSessionUserId=bacd1bc8a51a464e82d604699761150f; bm_mi=DB82C5873CFED6B2A2796A944305674B~YAAQhHZAF/ZGUpaUAQAA+nXLrhpXbrDPLM9+FgZOYC9jgjDvfCnzFmcEI74rwVT3qkrJgx94UveqOUBU2naHPehP5UR4Op7cH8I0qD7X26WGfuy8w5CnLVrTwPQZ0bglRorxdwqQV4qUq3v33IWt7Pi9Cqi2zLf8xG7WqE0pyxkxeZ9sknpnJpbyvnG2QajnjOJKqvlz74wbWThaosov6t/kZaQwd0NI7AD2NV8S1sVT/F1kfxwzRFwp8NEaAFWS0SlwYmigJNmQPfw/smAhlpDARA03ro6iNk2eR/4zLM71Bif6rIxFa+K0whPCURjW8SWl1qdc~1; bm_sv=9CF7F88DC4E647130EB1E7239BBDA339~YAAQhHZAFwJIUpaUAQAAbqjLrhrUgQj8lIlgtpEIqGE6MHIyOn63BF5pL9sew/Kvx5Y3tp1Hn7f+/A3WDBTWPz8LCecfkQFcg2iDV8z36SD6pFxDmbkS7MBTpPjaooEBPRrielCS/O238p/lVC7EIkwQYlnKXUJ1IQm3MSeFEtqR+YGdTYCYFk/SXtImp1aeW9hgceEik0McGpluL1P9a6VT7WoV/+B7W73LErHqx2b4IhreK+MDH6X3z9NdDS3D~1',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i',
    }


    response = requests.get(url, cookies=cookies, headers=headers, timeout=19)

    if response.status_code == 200:
        batch_data = []
        soup = BeautifulSoup(response.content, "html5lib")
        all_items = soup.find_all('div', class_='MuiBox-root mui-17tvcl1')
        #coupons = soup.find_all("div", class_="MuiBox-root mui-1d73mkv")
        coupons = []
        for item in all_items:
            location = item.find('div', {"class": re.compile('MuiTypography-root MuiTypography-bodyCopy.*')})
            if location:
                location_text = location.get_text()
                if 'Warehouse' in location_text:
                    coupons.append(item)

        disclaimer_header_elements = soup.find_all('div', {"class": re.compile('MuiTypography-root MuiTypography-bodyCopy.*')})
        for t in disclaimer_header_elements:
            if t.get_text().startswith('Pricing shown'):
                disclaimer_header_text = t.get_text()
        # disclaimer_header_text = disclaimer_header_elements[0].get_text()
        if disclaimer_header_text:
            valid_date_pattern = r'(?:.*Valid \d{1,2}/\d{1,2}/\d{1,2} - )(\d{1,2}/\d{1,2}/\d{1,2})'
            valid_to_match = re.match(valid_date_pattern, disclaimer_header_text)
            expiry_date = valid_to_match.groups()[0]
        else:
            expiry_date = '12/31/29'

        for item in coupons:
            item_text = item.find("div", class_="MuiBox-root mui-1d73mkv")
            item_name, item_numbers, price, savings = parse_product_string(item_text.get_text(' '))
            for item_id in item_numbers:
                if item_id:
                    batch_data.append(
                        [item_id, item_name, savings, expiry_date, price]
                    )
        return batch_data
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None


def store_data_csv(data, filename):
    """
    Store data in a CSV file.

    Args:
        data (list): A list of lists containing data to be stored.
        filename (str): The name of the CSV file.
    """
    # Write the batch data to the CSV file
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        # Create a CSV writer
        csv_writer = csv.writer(csvfile)

        # Write header
        csv_writer.writerow(
            ["Item ID", "Item Name", "Savings", "Expiry Date", "Sale Price"]
        )

        # Write the batch data
        csv_writer.writerows(data)

    print(f"Batch data written to {filename}")


def run_price_scraper():
    """
    Run the price scraper workflow.

    This function orchestrates the process of scraping data from sales posts on a website,
    storing the data in a CSV file, and updating the database with the scraped information.

    Steps:
    1. Get the list of URLs for sales posts.
    2. Print the list of obtained URLs.
    3. Create the items table in the database.
    4. Delete expired items from the database.
    5. Scrape data from the sales posts using the obtained URLs.
    6. If data is successfully scraped:
        a. Upsert (update or insert) the scraped data into the database.
        b. Remove duplicate entries based on item ID.
        c. If unique data is obtained:
            i. Store the unique scraped data in a CSV file.
            ii. Print a success message.
    7. If the scraping process failed, print an error message.
    """
    url = 'https://www.costco.com/online-offers.html'

    # Step 2: Create the items table in the database
    items_db.create_items_table()

    # Step 3: Delete expired items from the database
    items_db.delete_expired_items()

    # Step 4: Scrape data from the sales posts using the obtained URLs
    scraped_data = scrape_coupons(url)

    # Step 5: If data is successfully scraped
    if scraped_data:
        # Step 6a: Upsert the scraped data into the database
        items_db.upsert_items(scraped_data)

        # Step 6b: Remove duplicate entries based on item ID
        unique_dict = {}
        for inner_list in scraped_data:
            key = inner_list[0]

            # Only add the inner list if the key is not in the dictionary
            if key not in unique_dict:
                unique_dict[key] = inner_list

        # Step 6c: Convert the dictionary values back to a list
        scraped_data = list(unique_dict.values())

        # Step 6d: If unique data is obtained
        if scraped_data:
            # Step 6d-i: Store the unique scraped data in a CSV file
            store_data_csv(scraped_data, CSV_FILENAME)

            # Step 6d-ii: Print a success message
            print(f"Scraped_data stored in {CSV_FILENAME}")

    else:
        # Step 7: If the scraping process failed, print an error message
        print("Scraping failed.")

if __name__ == '__main__':
    run_price_scraper()