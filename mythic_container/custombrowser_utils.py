import ujson
from . import CustomBrowserBase
import traceback
import mythic_container


async def ExportFunction(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in CustomBrowserBase.custombrowsers.items():
            if pt.name == msgDict["container_name"]:
                inputMessage = CustomBrowserBase.ExportFunctionMessage(**msgDict)
                if pt.export_function is not None:
                    try:
                        response = await pt.export_function(inputMessage)

                    except Exception as e:
                        response = CustomBrowserBase.ExportFunctionMessageResponse(
                            Success=False,
                            Error=f"Hit exception trying to call export function: {traceback.format_exc()}\n{e}",
                        )
                    response.OperationID = inputMessage.OperationID
                    response.TreeType = inputMessage.TreeType
                    await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                        queue=mythic_container.CUSTOMBROWSER_EXPORT_FUNCTION_RESPONSE,
                        body=response.to_json()
                    )
                else:
                    response = CustomBrowserBase.ExportFunctionMessageResponse(
                        Success=True, CompletionMessage="Export Function not defined",
                        OperationID=inputMessage.OperationID, TreeType=inputMessage.TreeType
                    )
                    await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                        queue=mythic_container.CUSTOMBROWSER_EXPORT_FUNCTION_RESPONSE,
                        body=response.to_json()
                    )
                return
    except Exception as e:
        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
            queue=mythic_container.CUSTOMBROWSER_EXPORT_FUNCTION_RESPONSE,
            body=CustomBrowserBase.ExportFunctionMessageResponse(
                Error=f"Hit exception trying to call export function: {traceback.format_exc()}\n{e}"
            ).to_json()
        )