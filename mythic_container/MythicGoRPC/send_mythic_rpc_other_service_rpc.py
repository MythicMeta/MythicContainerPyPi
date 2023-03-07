import mythic_container
from mythic_container.logging import logger

MYTHIC_RPC_OTHER_SERVICES_RPC = "mythic_rpc_other_service_rpc"


class MythicRPCOtherServiceRPCMessage:
    def __init__(self,
                 ServiceName: str = None,
                 service_name: str = None,
                 ServiceRPCFunction: str = None,
                 service_function: str = None,
                 ServiceRPCFunctionArguments: dict = None,
                 service_arguments: dict = None,
                 **kwargs):
        self.ServiceName = ServiceName
        if self.ServiceName is None:
            self.ServiceName = service_name
        self.ServiceRPCFunction = ServiceRPCFunction
        if self.ServiceRPCFunction is None:
            self.ServiceRPCFunction = service_function
        self.ServiceRPCFunctionArguments = ServiceRPCFunctionArguments
        if self.ServiceRPCFunctionArguments is None:
            self.ServiceRPCFunctionArguments = service_arguments
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "service_name": self.ServiceName,
            "service_function": self.ServiceRPCFunction,
            "service_arguments": self.ServiceRPCFunctionArguments
        }
class MythicRPCOtherServiceRPCMessageResponse:
    def __init__(self,
                 success: bool = None,
                 error: str = None,
                 result: dict = None,
                 Success: bool = None,
                 Error: str = None,
                 Result: dict = None,
                 **kwargs):
        self.Success = Success
        if self.Success is None:
            self.Success = success
        self.Error = Error
        if self.Error is None:
            self.Error = error
        self.Result = Result
        if self.Result is None:
            self.Result = result
        for k, v in kwargs.items():
            logger.error(f"unknown kwarg {k} {v}")
    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "result": self.Result
        }


async def SendMythicRPCOtherServiceRPC(
        msg: MythicRPCOtherServiceRPCMessage) -> MythicRPCOtherServiceRPCMessageResponse:
    queue = f"{msg.ServiceName}_{MYTHIC_RPC_OTHER_SERVICES_RPC}"
    response = await mythic_container.RabbitmqConnection.SendRPCDictMessage(queue=queue,
                                                                            body=msg.to_json())
    return MythicRPCOtherServiceRPCMessageResponse(**response)
