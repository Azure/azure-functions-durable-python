from .subscription import SubscriptionInterface, SubscriptionProperties
from .subscription import SubscriptionResponse
from .subscription import ManagementGroupMoveResponse

"""
Simulates Azure API REST calls made via Python ms-rest SDK to manage subscription lifecycle
with canned response

Returns:
    SubscriptionResponse : Holds current state of Subscription
"""
class LocalSubscription(SubscriptionInterface):

    async def get_billing_account_id(self) -> str:
        return "1234567"
    
    async def get_enrollment_account_id(self) -> str:
        return "7654321"

    async def create_subscription(self,subscription_name:str,display_name:str) -> SubscriptionResponse:
        id = "/providers/Microsoft.Subscription/aliases/" + subscription_name
        props = SubscriptionProperties(subscription_id="1111111-2222-3333-4444-ebc1b75b9d74",provisioning_state="Succeeded")
        response = SubscriptionResponse(sub_id=id,sub_name=display_name,sub_type="Microsoft.Subscription/aliases",sub_props=props)        
        return response

    async def get_subscription_status(self, subscription_name:str) -> SubscriptionResponse:
        id = "/providers/Microsoft.Subscription/aliases/" + subscription_name

        props = SubscriptionProperties(subscription_id="1111111-2222-3333-4444-ebc1b75b9d74",provisioning_state="NotFound")
        response = SubscriptionResponse(sub_id=id,sub_name="sampleAlias",sub_type="Microsoft.Subscription/aliases",sub_props=props)
        return response

    async def move_subscription(self,subscription_id:str,management_group_id:str) -> ManagementGroupMoveResponse:
        group_sub_id = "/providers/Microsoft.Management/managementGroups/Group/subscriptions/" + subscription_id
        group_id = "/providers/Microsoft.Management/managementGroups/"  + management_group_id

        response: ManagementGroupMoveResponse = {
            "name": subscription_id,
            "id" : group_sub_id,
            "type" : "Microsoft.Management/managementGroups/subscriptions",
            "properties" : {
                "displayName" : "Group",
                "parent" : {
                    "id" : group_id
                },
                "state" : "Active",
                "tenant" : "1111111-2222-3333-4444-ebc1b75b9d74"
            } 
        }
        return response