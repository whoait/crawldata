from scrapy.item import Item, Field

# TripAdvisor items
class TripAdvisorItem(Item):

	url = Field()
	name = Field()
	address = Field()
	avg_stars = Field()
	photos = Field()
	reviews = Field()

class TripAdvisorAddressItem(Item):

	street = Field()
	postal_code = Field()
	locality = Field()
	country = Field()
	phone = Field()
	email = Field()