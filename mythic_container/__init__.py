from .rabbitmq import rabbitmqConnectionClass
from .mythic_service import start_and_run_forever, test_command
from .SharedClasses import *

containerVersion = "v1.3.5"

PyPi_version = "0.5.16"

RabbitmqConnection = rabbitmqConnectionClass()

MYTHIC_RPC_OTHER_SERVICES_RPC = "mythic_rpc_other_service_rpc"
PAYLOAD_BUILD_C2_ROUTING_KEY = "payload_c2_build"
# payload routes
PT_SYNC_ROUTING_KEY = "pt_sync"
PT_RPC_RESYNC_ROUTING_KEY = "pt_rpc_resync"
PT_RPC_COMMAND_DYNAMIC_QUERY_FUNCTION = "pt_command_dynamic_query_function"
PT_RPC_COMMAND_TYPEDARRAY_PARSE_FUNCTION = "pt_command_typedarray_parse"
PAYLOAD_BUILD_ROUTING_KEY = "payload_build"
PT_BUILD_RESPONSE_ROUTING_KEY = "pt_build_response"
PT_ON_NEW_CALLBACK_ROUTING_KEY = "pt_on_new_callback"
PT_CHECK_IF_CALLBACKS_ALIVE = "pt_check_if_callbacks_alive"
PT_ON_NEW_CALLBACK_RESPONSE_ROUTING_KEY = "pt_on_new_callback_response"
PT_BUILD_C2_RESPONSE_ROUTING_KEY = "pt_c2_build_response"
PT_TASK_OPSEC_PRE_CHECK = "pt_task_opsec_pre_check"
PT_TASK_OPSEC_PRE_CHECK_RESPONSE = "pt_task_opsec_pre_check_response"
PT_TASK_CREATE_TASKING = "pt_task_create_tasking"
PT_TASK_CREATE_TASKING_RESPONSE = "pt_task_create_tasking_response"
PT_TASK_OPSEC_POST_CHECK = "pt_task_opsec_post_check"
PT_TASK_OPSEC_POST_CHECK_RESPONSE = "pt_task_opsec_post_check_response"
PT_TASK_COMPLETION_FUNCTION = "pt_task_completion_function"
PT_TASK_COMPLETION_FUNCTION_RESPONSE = "pt_task_completion_function_response"
PT_TASK_PROCESS_RESPONSE = "pt_task_process_response"
PT_TASK_PROCESS_RESPONSE_RESPONSE = "pt_task_process_response_response"
# c2 routes
C2_SYNC_ROUTING_KEY = "c2_sync"
C2_RPC_RESYNC_ROUTING_KEY = "c2_rpc_resync"
C2_RPC_OPSEC_CHECKS_ROUTING_KEY = "c2_rpc_opsec_check"
C2_RPC_CONFIG_CHECK_ROUTING_KEY = "c2_rpc_config_check"
C2_RPC_GET_IOC_ROUTING_KEY = "c2_rpc_get_ioc"
C2_RPC_SAMPLE_MESSAGE_ROUTING_KEY = "c2_rpc_sample_message"
C2_RPC_REDIRECTOR_RULES_ROUTING_KEY = "c2_rpc_redirector_rules"
C2_RPC_START_SERVER_ROUTING_KEY = "c2_rpc_start_server"
C2_RPC_STOP_SERVER_ROUTING_KEY = "c2_rpc_stop_server"
C2_RPC_GET_SERVER_DEBUG_OUTPUT = "c2_rpc_get_server_debug_output"
C2_RPC_GET_AVAILABLE_UI_FUNCTIONS = "c2_rpc_get_ui_functions"
CONTAINER_RPC_GET_FILE = "container_rpc_get_file"
CONTAINER_RPC_REMOVE_FILE = "container_rpc_remove_file"
CONTAINER_RPC_LIST_FILE = "container_rpc_list_file"
CONTAINER_RPC_WRITE_FILE = "container_rpc_write_file"
C2_RPC_HOST_FILE_ROUTING_KEY = "c2_rpc_host_file"
# tr routes
TR_SYNC_ROUTING_KEY = "tr_sync"
TR_RPC_RESYNC_ROUTING_KEY = "tr_rpc_resync"
# webhook routes
EMIT_WEBHOOK_ROUTING_KEY_PREFIX = "emit_webhook"
WEBHOOK_TYPE_NEW_CALLBACK = "new_callback"
WEBHOOK_TYPE_NEW_FEEDBACK = "new_feedback"
WEBHOOK_TYPE_NEW_STARTUP = "new_startup"
WEBHOOK_TYPE_NEW_ALERT = "new_alert"
WEBHOOK_TYPE_NEW_CUSTOM = "new_custom"
# log routes
EMIT_LOG_ROUTING_KEY_PREFIX = "emit_log"
LOG_TYPE_CALLBACK = "new_callback"
LOG_TYPE_CREDENTIAL = "new_credential"
LOG_TYPE_FILE = "new_file"
LOG_TYPE_ARTIFACT = "new_artifact"
LOG_TYPE_TASK = "new_task"
LOG_TYPE_PAYLOAD = "new_payload"
LOG_TYPE_KEYLOG = "new_keylog"
LOG_TYPE_RESPONSE = "new_response"
# CONSUMING_SERVICES_ROUTING_KEY
CONSUMING_CONTAINER_SYNC_ROUTING_KEY   = "consuming_container_sync"
CONSUMING_CONTAINER_RESYNC_ROUTING_KEY = "consuming_container_rpc_resync"
# EVENTING
EVENTING_CUSTOM_FUNCTION_RESPONSE    = "eventing_custom_function_response"
EVENTING_CUSTOM_FUNCTION             = "eventing_custom_function"
EVENTING_CONDITIONAL_CHECK_RESPONSE  = "eventing_conditional_check_response"
EVENTING_CONDITIONAL_CHECK           = "eventing_conditional_check"
EVENTING_TASK_INTERCEPT              = "eventing_task_intercept"
EVENTING_TASK_INTERCEPT_RESPONSE     = "eventing_task_intercept_response"
EVENTING_RESPONSE_INTERCEPT          = "eventing_response_intercept"
EVENTING_RESPONSE_INTERCEPT_RESPONSE = "eventing_response_intercept_response"
# AUTH
AUTH_RPC_GET_IDP_REDIRECT        = "auth_rpc_get_idp_redirect"
AUTH_RPC_PROCESS_IDP_RESPONSE    = "auth_rpc_process_idp_response"
AUTH_RPC_GET_IDP_METADATA        = "auth_rpc_get_idp_metadata"
AUTH_RPC_GET_NONIDP_METADATA     = "auth_rpc_get_nonidp_metadata"
AUTH_RPC_GET_NONIDP_REDIRECT     = "auth_rpc_get_nonidp_redirect"
AUTH_RPC_PROCESS_NONIDP_RESPONSE = "auth_rpc_process_nonidp_response"

CONTAINER_ON_START          = "container_on_start"
CONTAINER_ON_START_RESPONSE = "container_on_start_response"
