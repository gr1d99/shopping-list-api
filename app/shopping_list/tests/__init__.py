from app import API


BASE_PREFIX = API.prefix

# shoppinglist urls.
PREFIX_ONE = BASE_PREFIX + 'shopping-lists'
PREFIX_TWO = BASE_PREFIX + 'shopping-lists/'

# shoppingitems urls.
ALL_SHOPPINGITEMS_URL = PREFIX_TWO + 'shopping-items/all'
CREATE_SHOPPINGITEMS_URL = PREFIX_TWO + '%(id)s/shopping-items'
UPDATE_SHOPPINGITEMS_URL = PREFIX_TWO + '%(shl_id)s/shopping-items/%(shi_id)s'
DELETE_SHOPPINGITEMS_URL = PREFIX_TWO + '%(shl_id)s/shopping-items/%(shi_id)s'
