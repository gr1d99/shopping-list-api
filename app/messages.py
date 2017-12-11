__all__ = [
    'account_created', 'account_deleted', 'account_not_updated', 'account_updated',
    'credentials_required', 'data_required', 'email_does_not_exist', 'email_not_provided',
    'email_exists', 'incomplete_delete', 'incorrect_old_password', 'incorrect_password',
    'invalid_email', 'invalid_limit', 'invalid_page', 'login_again', 'negative_limit',
    'negative_page', 'new_email_exists', 'new_username_exists', 'password_changed', 'passwords_donot_match',
    'password_not_provided', 'reset_token_sent', 'reset_token_expired', 'reset_token_does_not_exist',
    'reset_token_required', 'search_not_found', 'server_error', 'shoppingitem_created',
    'shoppingitem_deleted', 'shoppingitem_exists', 'shoppingitem_not_found', 'shoppingitem_not_updated',
    'shoppingitem_updated', 'shoppinglist_created', 'shoppinglist_deleted', 'shoppinglist_name_exists',
    'shoppinglist_not_found', 'shoppinglist_not_updated', 'logout_successful', 'shoppinglist_updated',
    'successful_login', 'user_does_not_exist', 'username_exists', 'username_not_allowed',
    'user_not_found', 'username_not_provided', 'username_or_email_required', 'username_with_whitespaces',
    'valid_integer_required'
]

login_again = 'Please login again with your username and password.'
user_does_not_exist = 'The username you provided does not exist, ' \
                      'please check your username or register to get an account'
credentials_required = "You musty provide username and password."
username_not_provided = 'Provide a username'
email_not_provided = 'Provide an email'
password_not_provided = 'Provide a password'
username_exists = 'The username you provided already exists, use a different username or login if it belongs to you'
email_exists = 'User with that email exists, use a different email id or login if it belongs to you'
account_created = 'Account created, login with your username and password to get authorization token.'
account_updated = 'Your account has been successfully updated.'
account_deleted = 'Your account has been deleted successfully.'
password_changed = 'Your password has been successfully changed'
username_or_email_required = 'You must provide a username or email'
incorrect_old_password = 'Incorrect old password provided'
passwords_donot_match = 'The passwords you provided do not match, please try again.'
incorrect_password = 'The password you provided is incorrect.'
user_not_found = "User not found, login and try again"
invalid_email = "Not a valid email address."
data_required = "Missing data for required field."
username_not_allowed = "The username you provided is not allowed, please try again but with a different name."
username_with_whitespaces = 'username values %(err)s, please try again without without whitespaces'
successful_login = 'Successfully logged in.'
new_username_exists = "User with %(username)s exists. Choose a different username."
new_email_exists = "User with %(email)s exists. Choose a different email."
account_not_updated = "You made an update request with no new details, " \
                      "your account has not been modified."
logout_successful = "You have successfully been logged out."
incomplete_delete = "The password you provided is incorrect. Try again."
email_does_not_exist = "There is no such email, check the email you provided and try again."


# shopping list and shopping items endpoints messages
shoppinglist_created = "Shopping list created"
valid_integer_required = "Provide a valid id"
shoppinglist_not_found = 'Shopping list not found, please check the ID you provided or create a new shoppinglist.'
shoppinglist_updated = 'Shopping list updated'
shoppinglist_not_updated = "Your shoppinglist has not been modified."
shoppinglist_name_exists = "The name you provided already exist, please choose a different name and try again."
shoppinglist_deleted = 'Shopping list deleted'

shoppingitem_exists = 'There exists a shopping item with similar name and quantity description, ' \
                      'create a new shopping item or update the existing item. '
shoppingitem_created = 'Shopping item created'
shoppingitem_deleted = 'Shopping item deleted.'
shoppingitem_not_found = 'Shopping item not found'
shoppingitem_updated = 'Shopping item updated'
shoppingitem_not_updated = 'Shopping item not modified.'


# server error message
server_error = 'Server error, try again'

# url params error messages
invalid_limit = 'limit parameter should be an integer'
invalid_page = 'page parameter should be an integer'
negative_limit = 'limit parameter should be an integer greater than 0'
negative_page = 'page parameter should be an integer greater than 0'

# search messages.
search_not_found = "Your search did not match any shoppings, try again."

# password reset message.
reset_token_required = 'Password reset token value is required.'
reset_token_sent = "Please use the password reset token to complete your password reset request."
reset_token_expired = "The password reset token you provided is expired, please request a new one."
reset_token_does_not_exist = "The password reset token you provided does not exist, " \
                             "please check your email or request a new token"
