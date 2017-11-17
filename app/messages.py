__all__ = [
    'account_created', 'data_required', 'email_not_provided', 'email_exists', 'incorrect_old_password',
    'incorrect_password_or_username', 'invalid_email', 'invalid_limit', 'invalid_page', 'negative_limit',
    'negative_page', 'password_changed', 'passwords_donot_match', 'password_not_provided',
    'search_not_found', 'server_error', 'shoppingitem_created', 'shoppingitem_exists',
    'shoppingitem_not_found', 'shoppingitem_updated', 'shoppinglist_created', 'shoppinglist_deleted',
    'shoppinglist_name_exists', 'shoppinglist_not_found', 'shoppinglist_updated', 'username_exists',
    'user_not_found', 'username_not_provided', 'username_or_email_required', 'valid_integer_required'
]

username_not_provided = 'Provide a username'
email_not_provided = 'Provide an email'
password_not_provided = 'Provide a password'
username_exists = 'User with that username exists, use a different name or login if it belongs to you'
email_exists = 'User with that email exists, use a different email id or login if it belongs to you'
account_created = 'Account created, login with your email and password to get your access tokens'
password_changed = 'Your password has been successfully changed'
username_or_email_required = 'You must provide a username or email'
incorrect_old_password = 'Incorrect old password provided'
passwords_donot_match = 'Passwords do not match'
incorrect_password_or_username = 'Incorrect username or password'
user_not_found = "User not found, login and try again"
invalid_email = "Not a valid email address."
data_required = "Missing data for required field."


# shopping list and shopping items endpoints messages
shoppinglist_created = "Shopping list created"
valid_integer_required = "Provide a valid id"
shoppinglist_not_found = 'Shopping list not found'
shoppinglist_updated = 'Shopping list updated'
shoppinglist_name_exists = "There exists a shoppinglist with the provided name exists, try again with a different name"
shoppinglist_deleted = 'Shopping list deleted'

shoppingitem_exists = 'There exists a shopping item with similar name, try again'
shoppingitem_created = 'Shopping item created'
shoppingitem_not_found = 'Shopping item not found'
shoppingitem_updated = 'Shopping item updated'


# server error message
server_error = 'Server error, try again'

# url params error messages
invalid_limit = 'limit parameter should be an integer'
invalid_page = 'page parameter should be an integer'
negative_limit = 'limit parameter should be an integer greater than 0'
negative_page = 'page parameter should be an integer greater than 0'

# search messages.
search_not_found = "Your search did not match any shoppings, try again."
