import json,base64

"""
Represents a UserToken with a specific set of user id's and groups.
Validates token from Identifies if a token belongs to a specific group from the claims
"""
class UserToken:
    id_token = []
    group_ids = []

    def __init__(self,base64_token:str):

        decoded_token = base64.b64decode(base64_token)
        id_token = json.loads(decoded_token)

        try:
            UserToken.validate_token(id_token)
            self.id_token = id_token
            self.group_ids = UserToken.get_group_ids(self.id_token)
        except Exception as e:
            raise
    
    @staticmethod
    def get_group_ids(id_token:str):
        claims = id_token["claims"]
        group_ids = [c["val"] for c in claims if c["typ"] == "groups"]
        return group_ids
        
    @staticmethod
    def validate_token(id_token:str):
        try:
            claims = id_token["claims"]
        except Exception as e:
            raise
    
    def is_member(self,group_id:str):
        if group_id in self.group_ids:
            return True
        return False



