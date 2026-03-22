from supabase import Client
class CleanUpDatabase:
    @staticmethod
    def cleanup_test_data(supabase: Client, member_id=None, operator_id=None, organisation_admin_id=None,organisation_id=None):
        #print("CleanUp",member_id, operator_id, organisation_admin_id,organisation_id,flush=True)
        if member_id:
            #supabase.table("members").delete().eq("id", member_id).execute()
            supabase.auth.admin.delete_user(member_id)
        if operator_id:
            #supabase.table("operators").delete().eq("id", operator_id).execute()
            supabase.auth.admin.delete_user(operator_id)
        if organisation_id:
            supabase.table("organisations").delete().eq("id", organisation_id).execute()
            supabase.auth.admin.delete_user(organisation_admin_id)
        