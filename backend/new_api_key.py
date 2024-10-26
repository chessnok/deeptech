from datetime import datetime, timedelta

from application.models import ApiKey
import random
import string

random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
random_string = random_string.encode('utf-8')
api_key = ApiKey(random_string, expires=datetime.now() + timedelta(days=30))
api_key.save()
print(random_string.decode('utf-8'))