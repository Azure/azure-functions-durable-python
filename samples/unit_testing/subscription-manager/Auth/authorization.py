import logging
import azure.functions as func
from .usertoken import UserToken
from functools import wraps

"""
Decorator method that is called for authorization before the Durable HTTP start method is invoked.
It uses the X-MS-CLIENT-PRINCIPAL id in the request header to authenticate against a set of known
Subscription Managers/Readers
"""
def authorize(allowed_groups:list):
    """Wrap the decorator to allow passing in a group name"""
    def decorator_authorize(decorated_function):
        """Decorator to handle authorization"""

        # Wraps ensures that the decorated function's parameters are exposed and not
        # this function's parameters.
        @wraps(decorated_function)
        async def validate_authorization(*args, **kwargs):
            """Check authorization of caller"""
            logging.info("In the authorization decorator authorizing for %s" %(allowed_groups))
            
            # Get 'req' parameter that was passed to the decorated function
            request = kwargs['req']
            
            # Get the claims token from the request header
            token_b64 = request.headers.get('X-MS-CLIENT-PRINCIPAL', '')

            # Simulate 403 call if we don't pass in a header
            if token_b64 == '':
                return func.HttpResponse("", status_code=403)
            user_token = UserToken(token_b64)

            for group_id in allowed_groups:
                if user_token.is_member(group_id): 
                    # Call the decorated function
                    return await decorated_function(*args, **kwargs)
                else:
                    return func.HttpResponse("", status_code=403)

        return validate_authorization
    return decorator_authorize