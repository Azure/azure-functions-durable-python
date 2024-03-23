import os

"""
Set of known groups represented as environment variables.
Subscription Managers: Service principals have permissions to create and delete subscriptions
Subscription Readers: Service principals have permissions to read subscription
"""
class SecurityGroups:
    subscription_managers = os.getenv("SecurityGroups_SUBSCRIPTION_MANAGERS")
    subscription_readers = os.getenv("SecurityGroups_SUBSCRIPTION_READERS")