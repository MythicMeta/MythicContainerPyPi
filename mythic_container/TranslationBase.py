import asyncio
from abc import abstractmethod
from .grpc.translationContainerGRPC_pb2_grpc import TranslationContainerStub
from .grpc import translationContainerGRPC_pb2 as grpcFuncs
import grpc.aio
from mythic_container.logging import logger
from .config import settings
import json
from typing import List


class TrGenerateEncryptionKeysMessage:
    """
    Message from gRPC asking translation container to generate encryption/decryption keys

    :param TranslationContainerName
    :param C2Name
    :param CryptoParamValue - what the user selected when building an agent
    :param CryptoParamName - the name of the parameter that needs a crypto key generated

    """
    def __init__(self,
                 TranslationContainerName: str,
                 C2Name: str,
                 CryptoParamValue: str,
                 CryptoParamName: str):
        self.TranslationContainerName = TranslationContainerName
        self.C2Name = C2Name
        self.CryptoParamValue = CryptoParamValue
        self.CryptoParamName = CryptoParamName

    def to_json(self):
        return {
            "translation_container_name": self.TranslationContainerName,
            "c2_profile_name": self.C2Name,
            "value": self.CryptoParamValue,
            "name": self.CryptoParamName
        }


class TrGenerateEncryptionKeysMessageResponse:
    """
    Response to a request to generate encryption keys

    :param Success indicate if this was successful or not
    :param Error if this wasn't successful, what's the error message
    :param EncryptionKey the bytes of the new encryption key to use
    :param DecryptionKey the bytes of the new decryption key to use

    """
    def __init__(self,
                 Success: bool = False,
                 Error: str = "",
                 EncryptionKey: bytes = None,
                 DecryptionKey: bytes = None):
        self.Success = Success
        self.Error = Error
        self.EncryptionKey = EncryptionKey
        self.DecryptionKey = DecryptionKey

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "enc_key": self.EncryptionKey,
            "dec_key": self.DecryptionKey
        }


class CryptoKeys:
    """
    Crypto Key information available for a translation container to decrypt/encrypt a message if necessary

    :param EncKey the bytes of the encryption key or None
    :param DecKey the bytes of the decryption key or None
    :param Value the value selected by the user for the type of encryption
    """
    def __init__(self,
                 EncKey: bytes = None,
                 DecKey: bytes = None,
                 Value: str = ""):
        self.EncKey = EncKey
        self.DecKey = DecKey
        self.Value = Value
    def to_json(self):
        return {
            "enc_key": self.EncKey,
            "dec_key": self.DecKey,
            "value": self.Value
        }


class TrCustomMessageToMythicC2FormatMessage:
    """
    Request to translation a custom C2 formatted message into a Mythic dictionary message

    :param TranslationContainerName
    :param C2Name
    :param Message the raw message to be translated WITHOUT the UUID in front
    :param UUID the extracted UUID from the front of the message
    :param MythicEncrypts indicates if Mythic will do the encryption/decryption or not
    :param CryptoKeys the encryption/decryption keys Mythic is tracking in case the translation container needs them
    """
    def __init__(self,
                 TranslationContainerName: str,
                 C2Name: str,
                 Message: bytes,
                 UUID: str,
                 MythicEncrypts: bool,
                 CryptoKeys: List[CryptoKeys] = []):
        self.TranslationContainerName = TranslationContainerName
        self.C2Name = C2Name
        self.Message = Message
        self.UUID = UUID
        self.MythicEncrypts = MythicEncrypts
        self.CryptoKeys = CryptoKeys

    def to_json(self):
        return {
            "translation_container_name": self.TranslationContainerName,
            "c2_profile_name": self.C2Name,
            "message": self.Message,
            "uuid": self.UUID,
            "mythic_encrypts": self.MythicEncrypts,
            "crypto_keys": [x.to_json() for x in self.CryptoKeys]
        }


class TrCustomMessageToMythicC2FormatMessageResponse:
    """
    Response to a request to translate a custom C2 formatted message into Mythic dictionary format

    :param Success indicating if this translation was successful or not
    :param Error if success is false, what is the error string to report back to the operator
    :param Message the Mythic dictionary message
    """
    def __init__(self,
                 Success: bool = False,
                 Error: str = "",
                 Message: dict = {}):
        self.Success = Success
        self.Error = Error
        self.Message = Message

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": self.Message
        }


class TrMythicC2ToCustomMessageFormatMessage:
    """
    Request to translate a Mythic message into a custom C2 format

    :param TranslationContainerName
    :param C2Name
    :param Message the Mythic dictionary message
    :param UUID the UUID associated with this message
    :param MythicEncrypts does Mythic handle encryption or not, if not, then this function needs to encrypt
    :param CryptoKeys the encryption/decryption keys that Mythic is tracking for this UUID
    """
    def __init__(self,
                 TranslationContainerName: str,
                 C2Name: str,
                 Message: dict,
                 UUID: str,
                 MythicEncrypts: bool,
                 CryptoKeys: List[CryptoKeys]):
        self.TranslationContainerName = TranslationContainerName
        self.C2Name = C2Name
        self.Message = Message
        self.UUID = UUID
        self.MythicEncrypts = MythicEncrypts
        self.CryptoKeys = CryptoKeys

    def to_json(self):
        return {
            "translation_container_name": self.TranslationContainerName,
            "c2_profile_name": self.C2Name,
            "message": self.Message,
            "uuid": self.UUID,
            "mythic_encrypts": self.MythicEncrypts,
            "crypto_keys": [x.to_json() for x in self.CryptoKeys]
        }


class TrMythicC2ToCustomMessageFormatMessageResponse:
    """
    Response to a request for converting a Mythic dictionary message to a custom C2 format

    :param Success was this translation successful or not
    :param Error if this was not successful, what was the error
    :param Message The final message that should be returned back to the agent. No other processing happens to this message after this function, so add the UUID as needed and base64 encode it.
    """
    def __init__(self,
                 Success: bool = False,
                 Error: str = "",
                 Message: bytes = b''):
        self.Success = Success
        self.Error = Error
        self.Message = Message

    def to_json(self):
        return {
            "success": self.Success,
            "error": self.Error,
            "message": self.Message
        }


class TranslationContainer:
    """The base definition for a Translation Container Service.

    To have this hooked up to a Payload Type, you need to specify this service's name as the translation_container attribute in your Payload Type.

    This uses gRPC to connect to port 17444 on the Mythic Server.

    Attributes:
        name (str): The name of the translation container
        description (str): Description of the translation container to appear in Mythic's UI
        author (str): The author of the container

    Functions:
        to_json:
            return dictionary form of class
        generate_keys:
            A function for generating encryption/decryption keys based on provided C2 info
        translate_to_c2_format:
            A function for translating from Mythic's JSON format to a custom C2 format
        translate_from_c2_format:
            A function for translating from a custom C2 format to Mythic's JSON format

    """
    async def generate_keys(self, inputMsg: TrGenerateEncryptionKeysMessage) -> TrGenerateEncryptionKeysMessageResponse:
        response = TrGenerateEncryptionKeysMessageResponse(Success=False)
        response.Error = f"Not Implemented:\n{inputMsg}"

        return response

    async def translate_to_c2_format(self,
                                     inputMsg: TrMythicC2ToCustomMessageFormatMessage) -> TrMythicC2ToCustomMessageFormatMessageResponse:
        response = TrMythicC2ToCustomMessageFormatMessageResponse(Success=False)
        response.Error = f"Not Implemented:\n{inputMsg}"
        return response

    async def translate_from_c2_format(self,
                                       inputMsg: TrCustomMessageToMythicC2FormatMessage) -> TrCustomMessageToMythicC2FormatMessageResponse:
        response = TrCustomMessageToMythicC2FormatMessageResponse(Success=False)
        response.Error = f"Not Implemented:\n{inputMsg}"
        return response

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    @property
    @abstractmethod
    def author(self):
        pass

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "author": self.author,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


translationServices: dict[str, TranslationContainer] = {}


async def handleTranslationServices(tr_name: str):
    while True:
        try:
            logger.info(f"Attempting connection to gRPC for {tr_name}...")
            channel = grpc.aio.insecure_channel(
                f'{settings.get("mythic_server_host", "127.0.0.1")}:{settings.get("mythic_server_grpc_port", 17444)}')
            await channel.channel_ready()
            client = TranslationContainerStub(channel=channel)
            genKeys = handleGenerateKeys(tr_name, client)
            customToMythic = handleCustomToMythic(tr_name, client)
            mythicToCustom = handleMythicToCustom(tr_name, client)
            logger.info(f"[+] Successfully connected to gRPC for {tr_name}")
            await asyncio.gather(genKeys, customToMythic, mythicToCustom)
        except Exception as e:
            logger.exception(f"Translation gRPC services closed for {tr_name}: {e}")


async def handleGenerateKeys(tr_name: str, client):
    try:
        while True:
            stream = client.GenerateEncryptionKeys()
            await stream.write(grpcFuncs.TrGenerateEncryptionKeysMessageResponse(
                Success=True,
                TranslationContainerName=tr_name
            ))
            logger.info(f"Connected to gRPC for generating encryption keys for {tr_name}")
            async for request in stream:
                try:
                    result = await translationServices[tr_name].generate_keys(TrGenerateEncryptionKeysMessage(
                        TranslationContainerName=request.TranslationContainerName,
                        C2Name=request.C2Name,
                        CryptoParamName=request.CryptoParamName,
                        CryptoParamValue=request.CryptoParamValue
                    ))
                    await stream.write(grpcFuncs.TrGenerateEncryptionKeysMessageResponse(
                        Success=result.Success,
                        TranslationContainerName=tr_name,
                        Error=result.Error,
                        EncryptionKey=result.EncryptionKey,
                        DecryptionKey=result.DecryptionKey
                    ))
                except Exception as d:
                    logger.exception(f"Failed to process handleGenerateKeys message:\n{d}")
                    await stream.write(grpcFuncs.TrGenerateEncryptionKeysMessageResponse(
                        Success=False,
                        TranslationContainerName=tr_name,
                        Error=f"Failed to process handleGenerateKeys message:\n{d}"
                    ))
            logger.error(f"disconnected from gRPC for generating encryption keys for {tr_name}")
    except Exception as e:
        logger.exception(f"[-] exception in handleGenerateKeys for {tr_name}")


async def handleCustomToMythic(tr_name: str, client):
    try:
        while True:
            stream = client.TranslateFromCustomToMythicFormat()
            await stream.write(grpcFuncs.TrCustomMessageToMythicC2FormatMessageResponse(
                Success=True,
                TranslationContainerName=tr_name
            ))
            logger.info(f"Connected to gRPC for handling CustomC2 to MythicC2 Translations for {tr_name}")
            async for request in stream:
                try:
                    grpcCryptoKeys = request.CryptoKeys
                    localCryptoKeys = []
                    for keys in grpcCryptoKeys:
                        localCryptoKeys.append(CryptoKeys(
                            Value=keys.Value,
                            DecKey=keys.DecKey,
                            EncKey=keys.EncKey
                        ))
                    inputMsg = TrCustomMessageToMythicC2FormatMessage(
                        TranslationContainerName=request.TranslationContainerName,
                        C2Name=request.C2Name,
                        Message=request.Message,
                        UUID=request.UUID,
                        MythicEncrypts=request.MythicEncrypts,
                        CryptoKeys=localCryptoKeys
                    )
                    result = await translationServices[tr_name].translate_from_c2_format(inputMsg)
                    response = grpcFuncs.TrCustomMessageToMythicC2FormatMessageResponse(
                        Success=result.Success,
                        Error=result.Error,
                        TranslationContainerName=tr_name,
                        Message=json.dumps(result.Message).encode()
                    )
                    await stream.write(response)
                except Exception as d:
                    logger.exception(f"Failed to process handleCustomToMythic message:\n{d}")
                    await stream.write(grpcFuncs.TrCustomMessageToMythicC2FormatMessageResponse(
                        Success=False,
                        TranslationContainerName=tr_name,
                        Error=f"Failed to process handleCustomToMythic message:\n{d}"
                    ))
            logger.error(f"disconnected from gRPC for doing custom->mythic c2 for {tr_name}")
    except Exception as e:
        logger.exception(f"[-] exception in handleCustomToMythic for {tr_name}")


async def handleMythicToCustom(tr_name: str, client):
    try:
        while True:
            stream = client.TranslateFromMythicToCustomFormat()
            await stream.write(grpcFuncs.TrMythicC2ToCustomMessageFormatMessageResponse(
                Success=True,
                TranslationContainerName=tr_name
            ))
            logger.info(f"Connected to gRPC for handling MythicC2 to CustomC2 Translations for {tr_name}")
            async for request in stream:
                try:
                    grpcCryptoKeys = request.CryptoKeys
                    localCryptoKeys = []
                    for keys in grpcCryptoKeys:
                        localCryptoKeys.append(CryptoKeys(
                            Value=keys.Value,
                            DecKey=keys.DecKey,
                            EncKey=keys.EncKey
                        ))
                    inputMsg = TrMythicC2ToCustomMessageFormatMessage(
                        TranslationContainerName=request.TranslationContainerName,
                        C2Name=request.C2Name,
                        UUID=request.UUID,
                        MythicEncrypts=request.MythicEncrypts,
                        CryptoKeys=localCryptoKeys,
                        Message=json.loads(request.Message)
                    )
                    result = await translationServices[tr_name].translate_to_c2_format(inputMsg)
                    response = grpcFuncs.TrMythicC2ToCustomMessageFormatMessageResponse(
                        Success=result.Success,
                        Error=result.Error,
                        TranslationContainerName=tr_name,
                        Message=result.Message
                    )
                    await stream.write(response)
                except Exception as d:
                    logger.exception(f"Failed to process handleMythicToCustom message:\n{d}")
                    await stream.write(grpcFuncs.TrMythicC2ToCustomMessageFormatMessageResponse(
                        Success=False,
                        TranslationContainerName=tr_name,
                        Error=f"Failed to process handleMythicToCustom message:\n{d}"
                    ))
            logger.error(f"disconnected from gRPC for doing mythic->custom c2 for {tr_name}")
    except Exception as e:
        logger.exception(f"[-] exception in handleMythicToCustom for {tr_name}")
