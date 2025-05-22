from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


from app.models.organization import Organization
from app.models.opportunity import Opportunity
from app.models.match import Match
from app.models.volunteer_hour import VolunteerHour
from app.models.admin import Admin