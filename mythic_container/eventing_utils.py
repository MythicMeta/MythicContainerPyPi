import ujson
from . import EventingBase
import traceback
import mythic_container


async def ConditionalEventingCheck(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in EventingBase.eventingServices.items():
            if pt.name == msgDict["container_name"]:
                for conditionalDef in pt.conditional_checks:
                    if conditionalDef.Name == msgDict["function_name"]:
                        try:
                            response = await conditionalDef.Function(EventingBase.ConditionalCheckEventingMessage(**msgDict))
                            response.EventStepInstanceID = msgDict["eventstepinstance_id"]
                        except Exception as e:
                            response = EventingBase.ConditionalCheckEventingMessageResponse(
                                EventStepInstanceID=msgDict["eventstepinstance_id"],
                                StdErr=f"Hit exception trying to call conditional check function: {traceback.format_exc()}\n{e}"
                            )
                        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                            queue=mythic_container.EVENTING_CONDITIONAL_CHECK_RESPONSE,
                            body=response.to_json()
                        )
                return
    except Exception as e:
        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
            queue=mythic_container.EVENTING_CONDITIONAL_CHECK_RESPONSE,
            body=EventingBase.ConditionalCheckEventingMessageResponse(
                StdErr=f"Hit exception trying to call conditional check function: {traceback.format_exc()}\n{e}"
            ).to_json()
        )


async def CustomFunction(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in EventingBase.eventingServices.items():
            if pt.name == msgDict["container_name"]:
                for conditionalDef in pt.custom_functions:
                    if conditionalDef.Name == msgDict["function_name"]:
                        try:
                            response = await conditionalDef.Function(EventingBase.NewCustomEventingMessage(**msgDict))
                            response.EventStepInstanceID = msgDict["eventstepinstance_id"]
                        except Exception as e:
                            response = EventingBase.NewCustomEventingMessageResponse(
                                EventStepInstanceID=msgDict["eventstepinstance_id"],
                                StdErr=f"Hit exception trying to call custom function function: {traceback.format_exc()}\n{e}",
                            )
                        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                            queue=mythic_container.EVENTING_CUSTOM_FUNCTION_RESPONSE,
                            body=response.to_json()
                        )
                return
    except Exception as e:
        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
            queue=mythic_container.EVENTING_CUSTOM_FUNCTION_RESPONSE,
            body=EventingBase.NewCustomEventingMessageResponse(
                StdErr=f"Hit exception trying to call custom function function: {traceback.format_exc()}\n{e}"
            ).to_json()
        )


async def TaskIntercept(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in EventingBase.eventingServices.items():
            if pt.name == msgDict["container_name"]:
                if pt.task_intercept_function is not None:
                    try:
                        response = await pt.task_intercept_function(EventingBase.TaskInterceptMessage(**msgDict))
                        response.EventStepInstanceID = msgDict["eventstepinstance_id"]
                    except Exception as e:
                        response = EventingBase.TaskInterceptMessageResponse(
                            EventStepInstanceID=msgDict["eventstepinstance_id"],
                            BlockTask=True,
                            Success=False,
                            StdErr=f"Hit exception trying to call task intercept function: {traceback.format_exc()}\n{e}"
                        )
                    await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                        queue=mythic_container.EVENTING_TASK_INTERCEPT_RESPONSE,
                        body=response.to_json()
                    )
                return
    except Exception as e:
        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
            queue=mythic_container.EVENTING_TASK_INTERCEPT_RESPONSE,
            body=EventingBase.TaskInterceptMessageResponse(
                StdErr=f"Hit exception trying to call task intercept function: {traceback.format_exc()}\n{e}"
            ).to_json()
        )


async def ResponseIntercept(msg: bytes) -> None:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in EventingBase.eventingServices.items():
            if pt.name == msgDict["container_name"]:
                if pt.response_intercept_function is not None:
                    try:
                        response = await pt.response_intercept_function(EventingBase.ResponseInterceptMessage(**msgDict))
                        response.EventStepInstanceID = msgDict["eventstepinstance_id"]
                    except Exception as e:
                        response = EventingBase.ResponseInterceptMessageResponse(
                            Success=False,
                            StdErr=f"Hit exception trying to call get_idp_metadata function: {traceback.format_exc()}\n{e}"
                        )
                    await mythic_container.RabbitmqConnection.SendDictDirectMessage(
                        queue=mythic_container.EVENTING_RESPONSE_INTERCEPT_RESPONSE,
                        body=response.to_json()
                    )
                return
    except Exception as e:
        await mythic_container.RabbitmqConnection.SendDictDirectMessage(
            queue=mythic_container.EVENTING_RESPONSE_INTERCEPT_RESPONSE,
            body=EventingBase.ResponseInterceptMessageResponse(
                StdErr=f"Hit exception trying to call get_idp_metadata function: {traceback.format_exc()}\n{e}"
            ).to_json()
        )
