import ujson
from . import AuthBase
import traceback


async def GetIDPMetadata(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in AuthBase.authServices.items():
            if pt.name == msgDict["container_name"]:
                response = pt.get_idp_metadata(AuthBase.GetIDPMetadataMessage(**msgDict))
                return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = AuthBase.GetIDPMetadataMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call get_idp_metadata function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


async def GetIDPRedirect(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in AuthBase.authServices.items():
            if pt.name == msgDict["container_name"]:
                response = pt.get_idp_redirect(AuthBase.GetIDPRedirectMessage(**msgDict))
                return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = AuthBase.GetIDPRedirectMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call get_idp_redirect function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


async def ProcessIDPResponse(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in AuthBase.authServices.items():
            if pt.name == msgDict["container_name"]:
                response = pt.process_idp_response(AuthBase.ProcessIDPResponseMessage(**msgDict))
                return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = AuthBase.ProcessIDPResponseMessageResponse(
            SuccessfulAuthentication=False,
            Error=f"Hit exception trying to call process_idp_response function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


async def GetNonIDPMetadata(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in AuthBase.authServices.items():
            if pt.name == msgDict["container_name"]:
                response = pt.get_non_idp_metadata(AuthBase.GetNonIDPMetadataMessage(**msgDict))
                return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = AuthBase.GetNonIDPMetadataMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call get_non_idp_metadata function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


async def GetNonIDPRedirect(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in AuthBase.authServices.items():
            if pt.name == msgDict["container_name"]:
                response = pt.get_non_idp_redirect(AuthBase.GetNonIDPRedirectMessage(**msgDict))
                return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = AuthBase.GetNonIDPRedirectMessageResponse(
            Success=False,
            Error=f"Hit exception trying to call get_non_idp_redirect function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()


async def ProcessNonIDPResponse(msg: bytes) -> bytes:
    try:
        msgDict = ujson.loads(msg)
        for name, pt in AuthBase.authServices.items():
            if pt.name == msgDict["container_name"]:
                response = pt.process_non_idp_response(AuthBase.ProcessNonIDPResponseMessage(**msgDict))
                return ujson.dumps(response.to_json()).encode()
    except Exception as e:
        response = AuthBase.ProcessNonIDPResponseMessageResponse(
            SuccessfulAuthentication=False,
            Error=f"Hit exception trying to call process_non_idp_response function: {traceback.format_exc()}\n{e}"
        )
        return ujson.dumps(response.to_json()).encode()
