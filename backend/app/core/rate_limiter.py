from slowapi import Limiter
from slowapi.util import get_remote_address


# Simple request limiter for login throttling.
limiter = Limiter(key_func=get_remote_address)