from sqlalchemy.orm import Session

from blustorymicroservices.blustory_accounts_auth.pgsqlalchemy.SQLAlchemyDatabaseProvider import SQLAlchemyDatabaseProvider
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
            db_client.delete("organisations",{"id":organisation_id})
                    # 5. Finally, delete from auth.users (The Root)
        # We collect all potential user IDs to clean the auth table
        user_ids_to_clean = []
        if member_id: user_ids_to_clean.append(member_id)
        if operator_id: user_ids_to_clean.append(operator_id)
        if organisation_admin_id: user_ids_to_clean.append(organisation_admin_id)

        for u_id in user_ids_to_clean:
            db_client.delete("auth.users",{"id":u_id})


          
        