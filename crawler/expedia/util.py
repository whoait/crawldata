"""
Parse Utils for Expedia
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