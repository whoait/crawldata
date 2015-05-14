import urllib2
"""
Parse Utils for Tripadvisor
"""
def get_site_id(url, separator_string):
    try:
        return int(
            url.split(
                separator_string)[1].
                split("-")[0])
    except:
        return None

# util for extracted encoded links
def getOffset(url):
    a = ord(url)
    if a >= 97 and a <= 122:
        return a - 61
    if a >= 65 and a <= 90:
        return a - 55
    if a >= 48 and a <= 71:
        return a - 48
    print a, (type(a)), (int(a))
    return -1

def decode_url(url):
    h = {
        "": ["&", "=", "p", "6", "?", "H", "%", "B", ".com", "k", "9", ".html", "n", "M", "r", "www.", "h", "b", "t", "a", "0", "/", "d", "O", "j", "http://", "_", "L", "i", "f", "1", "e", "-", "2", ".", "N", "m", "A", "l", "4", "R", "C", "y", "S", "o", "+", "7", "I", "3", "c", "5", "u", 0, "T", "v", "s", "w", "8", "P", 0, "g", 0],
        "q": [0, "__3F__", 0, "Photos", 0, "https://", ".edu", "*", "Y", ">", 0, 0, 0, 0, 0, 0, "`", "__2D__", "X", "<", "slot", 0, "ShowUrl", "Owners", 0, "[", "q", 0, "MemberProfile", 0, "ShowUserReviews", '"', "Hotel", 0, 0, "Expedia", "Vacation", "Discount", 0, "UserReview", "Thumbnail", 0, "__2F__", "Inspiration", "V", "Map", ":", "@", 0, "F", "help", 0, 0, "Rental", 0, "Picture", 0, 0, 0, "hotels", 0, "ftp://"],
        "x": [0, 0, "J", 0, 0, "Z", 0, 0, 0, ";", 0, "Text", 0, "(", "x", "GenericAds", "U", 0, "careers", 0, 0, 0, "D", 0, "members", "Search", 0, 0, 0, "Post", 0, 0, 0, "Q", 0, "$", 0, "K", 0, "W", 0, "Reviews", 0, ",", "__2E__", 0, 0, 0, 0, 0, 0, 0, "{", "}", 0, "Cheap", ")", 0, 0, 0, "#", ".org"],
        "z": [0, "Hotels", 0, 0, "Icon", 0, 0, 0, 0, ".net", 0, 0, "z", 0, 0, "pages", 0, "geo", 0, 0, 0, "cnt", "~", 0, 0, "]", "|", 0, "tripadvisor", "Images", "BookingBuddy", 0, "Commerce", 0, 0, "partnerKey", 0, "area", 0, "Deals", "from", "\\", 0, "urlKey", 0, "'", 0, "WeatherUnderground", 0, "MemberSign", "Maps", 0, "matchID", "Packages", "E", "Amenities", "Travel", ".htm", 0, "!", "^", "G"]	}
    b = ""
    a = 0
    while a < len(url):
        j = url[a]
        f = j
        try:
            if h[j] and ((a + 1) < len(url)):
                a += 1
                f += url[a]
            else:
                j = ""
        except:
            j = ""
        g = getOffset(url[a])
        if (g < 0):
            b += f
        else:
            b += h[j][g]
        print "f = {0} , g = {1}, h[j][g] = {2}, type(h[j][g]) = {3}, b = {4}".format(f, g, h[j][g], type(h[j][g]), b)
        a += 1
    return b

"""
As we want to find the highest URL containing a review,
we will check that the url selected contains a review,
but the next url does not
:param - base_url - base_url
:param - index - candidate index to be checked
:return - int indicating if index is maximum permissible index
-1 - both invalid URL
1 - both valid URL
"""
def verify_url(base_url, index):
    review_url = base_url.replace(
        "/reviews/",
        "/reviews-page-{0}/".format(
            index))
    try:
        urllib2.urlopen(review_url)
    except urllib2.HTTPError:
        return False
    review_url = base_url.replace(
        "/reviews/",
        "/reviews-page-{0}/".format(
            index+1))
    try:
        urllib2.urlopen(review_url)
    except urllib2.HTTPError:
        return True
    return False


"""
agoda reviews use a page number
find largest page number based on base_url
function will find highest URL that will cause
:base_url - base url of hotel
:return - list of urls
"""
def binary_search_url(base_url):
    page_count = 2
    bounds = [1, 1]
    return_list = [base_url]
    search_index = 1

    # first phase - find max url
    while True:
        review_url = base_url.replace(
        "/reviews/",
        "/reviews-page-{0}/".format(
            page_count
        ))
        try:
            urllib2.urlopen(review_url)
        except urllib2.HTTPError:
            bounds[1] = page_count
            break
        # record that we the lower bound contains a valid page
        bounds[0] = page_count
        page_count *= 2

    # second phase - find max real URL
    while bounds[1] - bounds[0] > 10:
        search_index = bounds[0] + (bounds[1] - bounds[0])/2
        status = verify_url(base_url, search_index)
        if status == -1:
            bounds[1] = search_index
        elif status == 1:
            bounds[0] = search_index
        else:
            return [base_url.replace(
                "/reviews/",
                "/reviews-page-{0}/".format(
                    i
            )) for i in xrange(2, search_index+1)]

    for i in range(bounds[0], bounds[1]):
        if verify_url(base_url, search_index) == 0:
            return [base_url.replace(
                "/reviews/",
                "/reviews-page-{0}/".format(
                    i
            )) for i in xrange(2, search_index+1)]
    return return_list