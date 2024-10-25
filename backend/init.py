from datetime import datetime, timedelta

from application import app, db
from application.models import ApiKey


with app.app_context():
    db.create_all()

# adminApiKey = ApiKey(key="eFew5EAslt38FwpNos8LN1DU988y0OQX", expires=None)
# db.session.add(adminApiKey)
# db.session.commit()
