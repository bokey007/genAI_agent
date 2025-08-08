from src.database import engine, Base
from src.models import Session, Feedback, Ticket

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created.")