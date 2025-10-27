"""
Tenant management API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
import uuid

from ..store.firestore.tenants import TenantStore
from ..store.firestore.rules import RuleStore
from ..common.auth import auth_manager, validate_tenant_access, log_auth_event
from ..common.logger import get_logger, LogContext
from ..common.api_constants import ApiConstants
from ..common.firewall_constants import FirewallConstants
from ..common.database_constants import DatabaseConstants
from ..common.auth_constants import AuthConstants
from ..models.schemas import TenantCreate, TenantResponse, TenantLogin, TenantLoginResponse

# Initialize stores
tenant_store = TenantStore()
rule_store = RuleStore()
logger = get_logger("tenants")

router = APIRouter()

@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(request: TenantCreate):
    """Create a new tenant."""
    with LogContext("create_tenant", tenant_name=request.name):
        try:
            # Check if tenant name already exists
            if auth_manager.check_tenant_name_exists(request.name):
                logger.warning(f"Duplicate tenant name attempted: {request.name}")
                raise HTTPException(
                    status_code=ApiConstants.HTTP_400_BAD_REQUEST,
                    detail=ApiConstants.DUPLICATE_TENANT_NAME.format(request.name)
                )
            
            tenant_id = str(uuid.uuid4())
            tenant_data = {
                DatabaseConstants.NAME_FIELD: request.name,
                DatabaseConstants.PASSWORD_FIELD: request.password,
                DatabaseConstants.METADATA_FIELD: request.metadata or {}
            }
            
            tenant_id = tenant_store.save(tenant_id, tenant_data)
            
            # Create default rules for the tenant
            rule_store.create_default_rules(tenant_id)
            
            # Log tenant creation
            log_auth_event(tenant_id, FirewallConstants.EVENT_TENANT_CREATED, {
                DatabaseConstants.TENANT_NAME_FIELD: request.name,
                DatabaseConstants.CREATED_BY_FIELD: DatabaseConstants.SYSTEM_CREATED_BY
            })
            
            # Get tenant with decrypted API key for response
            tenant = tenant_store.get_with_decrypted_api_key(tenant_id)
            logger.info(ApiConstants.TENANT_CREATED_SUCCESSFULLY.format(tenant_id))
            return TenantResponse(**tenant)
        
        except HTTPException:
            raise
        except Exception as e:
            error_str = str(e)
            logger.error(f"Failed to create tenant: {error_str}")
            raise HTTPException(
                status_code=ApiConstants.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create tenant: {error_str}"
            )

@router.post("/tenants/login", response_model=TenantLoginResponse)
async def login_tenant(request: TenantLogin):
    """Login tenant with name and password."""
    try:
        # Validate tenant credentials
        tenant, error_message = auth_manager.validate_tenant_credentials(request.name, request.password)
        
        if not tenant:
                raise HTTPException(
                    status_code=ApiConstants.HTTP_401_UNAUTHORIZED,
                    detail=error_message or ApiConstants.INVALID_TENANT_CREDENTIALS
                )
        
        # Get tenant with decrypted API key
        tenant_with_key = tenant_store.get_with_decrypted_api_key(tenant["tenant_id"])
        
        # Log successful login
        log_auth_event(tenant["tenant_id"], FirewallConstants.EVENT_TENANT_LOGIN, {
            DatabaseConstants.TENANT_NAME_FIELD: request.name,
            DatabaseConstants.LOGIN_METHOD_FIELD: DatabaseConstants.PASSWORD_LOGIN_METHOD
        })
        
        return TenantLoginResponse(
            tenant_id=tenant["tenant_id"],
            name=tenant["name"],
            api_key=tenant_with_key["api_key"],
            message=ApiConstants.LOGIN_SUCCESSFUL,
            status=DatabaseConstants.SUCCESS_STATUS
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=ApiConstants.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ApiConstants.LOGIN_FAILED.format(str(e))
        )

@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: str = Depends(validate_tenant_access)):
    """Get tenant information."""
    tenant = tenant_store.get(tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=ApiConstants.HTTP_404_NOT_FOUND,
            detail=AuthConstants.TENANT_NOT_FOUND
        )
    
    return TenantResponse(**tenant)

