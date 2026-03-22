from sqlalchemy.orm import Session

from blustorymicroservices.BluStoryAccounts.providers.pgsqlalchemy.SQLAlchemyDatabaseProvider import SQLAlchemyDatabaseProvider
class CleanUpDatabase:
    @staticmethod
    def cleanup_test_data(db_client: SQLAlchemyDatabaseProvider, member_id=None, operator_id=None, organisation_admin_id=None,organisation_id=None):
        #print("CleanUp",member_id, operator_id, organisation_admin_id,organisation_id,flush=True)
        if member_id:
            #db_client.table("members").delete().eq("id", member_id).execute()
            db_client.delete("members",{"id":member_id})
        if operator_id:
            db_client.delete("members",{"id":operator_id})
        if organisation_id:
            db_client.delete("organisations",{"id":operator_id})
          
        