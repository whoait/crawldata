"""
Parse Utils for Tripadvisor
"""


def get_site_id(url):
    try:
        return int(
            url.split('&hotelId=')[1].
            split('&')[0]
        )
    except:
        return None
