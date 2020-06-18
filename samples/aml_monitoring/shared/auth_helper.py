import os
import logging
import time

from azureml.core.authentication import ServicePrincipalAuthentication

_TENANT_ID_ENV_NAME = "TenantId"
_SERVICE_PRINCIPAL_ID_ENV_NAME = "ServicePrincipalId"
_SERVICE_PRINCIPAL_SECRET_ENV_NAME = "ServicePrincipalSecret"


def get_service_principal_auth():
    tenant_id = os.environ[_TENANT_ID_ENV_NAME]
    service_principal_id = os.environ[_SERVICE_PRINCIPAL_ID_ENV_NAME]
    service_principal_password = os.environ[_SERVICE_PRINCIPAL_SECRET_ENV_NAME]

    svc_pr = ServicePrincipalAuthentication(
        tenant_id=tenant_id,
        service_principal_id=service_principal_id,
        service_principal_password=service_principal_password)

    return svc_pr


def get_access_token():
    start_time = time.time()

    svc_pr = get_service_principal_auth()
    aad_token = svc_pr.get_authentication_header()

    end_time = time.time()

    logging.info('Get Access Token Time: %s seconds', end_time - start_time)
    return aad_token
