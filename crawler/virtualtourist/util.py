"""
Parse Utils for Booking
"""


def get_site_id(url):
    try:
        return int(
            url.split('.h')[1].
            split('.Hotel-Information')[0]
        )
    except:
        return None


def trim_url_query_string(url):
    return url.split("?")[0]


"""
Function to split line by \\n and , separator
:param - input_soup - BeautifulSoup tag containing section to split
:separator - string to tokenize input line with
:trim - string to be removed from each element

:return - list of strings from tag
"""
def split_line(input_soup, separator="\n", trim=","):
    in_list = input_soup.text.split(separator) if input_soup.text else []
    return [i.replace(trim, "") for i in in_list]
