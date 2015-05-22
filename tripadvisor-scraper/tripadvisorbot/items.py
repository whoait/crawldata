from scrapy.item import Item, Field

# TripAdvisor items
class TripAdvisorItem(Item):

	url = Field()
	business_id = Field()
	name = Field()
	country = Field()
	street = Field()
	postal_code = Field()
	phone = Field()
	email = Field()

class TripAdvisorAddressItem(Item):

	street = Field()
	postal_code = Field()
	locality = Field()
	country = Field()
	phone = Field()
	email = Field()