from .subscription import SubscriptionInterface,SubscriptionResponse,ManagementGroupMoveResponse
from .localsubscription import LocalSubscription

"""
Returns an implementation of subscription interface depending on the runtime environment

AzureSubscription: if runtime environment is production
LocalSubscription: if runtime environment is local

"""
class SubscriptionManager:

    subscription : SubscriptionInterface

    def __init__(self):        
            self.subscription = LocalSubscription()
    
    async def get_subscription(self) -> SubscriptionInterface:
        return self.subscription
    
    async def get_subscription_status(self, subscription_name:str) -> SubscriptionResponse:
        sub_mgr = await self.get_subscription()
        return await sub_mgr.get_subscription_status(subscription_name)
    
    async def get_enrollment_account_id(self) -> str:
        sub_mgr = await self.get_subscription()
        return await sub_mgr.get_enrollment_account_id()
    
    async def get_billing_account_id(self) -> str:
        sub_mgr = await self.get_subscription()
        return await sub_mgr.get_billing_account_id()
    
    async def move_subscription(self,subscription_id:str,management_group_id:str) -> ManagementGroupMoveResponse:
        sub_mgr = await self.get_subscription()
        return await sub_mgr.move_subscription(subscription_id,management_group_id)
    
    async def create_subscription(self,subscription_name:str,display_name:str) -> SubscriptionResponse:
        sub_mgr = await self.get_subscription()
        return await sub_mgr.create_subscription(subscription_name,display_name)