# this file will be used to set up a cron job to clear temp table periodically

from sqlalchemy.orm import Session
from model import TempUser

def delete_temp_users():
    session = Session()
    try:
        session.query(TempUser).delete()
        session.commit()
        print("All temp users deleted successfully.")
    except Exception as e:
        session.rollback()
        print(f"Failed to delete temp users: {str(e)}")
    finally:
        session.close()