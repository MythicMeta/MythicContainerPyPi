# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pushC2GRPC.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10pushC2GRPC.proto\x12\x0epushC2Services\"\xab\x01\n\x16PushC2MessageFromAgent\x12\x15\n\rC2ProfileName\x18\x01 \x01(\t\x12\x10\n\x08RemoteIP\x18\x02 \x01(\t\x12\x0f\n\x07Message\x18\x03 \x01(\x0c\x12\x11\n\tOuterUUID\x18\x04 \x01(\t\x12\x15\n\rBase64Message\x18\x05 \x01(\x0c\x12\x12\n\nTrackingID\x18\x06 \x01(\t\x12\x19\n\x11\x41gentDisconnected\x18\x07 \x01(\x08\"^\n\x17PushC2MessageFromMythic\x12\x0f\n\x07Success\x18\x01 \x01(\x08\x12\r\n\x05\x45rror\x18\x02 \x01(\t\x12\x0f\n\x07Message\x18\x03 \x01(\x0c\x12\x12\n\nTrackingID\x18\x04 \x01(\t2\xef\x01\n\x06PushC2\x12m\n\x14StartPushC2Streaming\x12&.pushC2Services.PushC2MessageFromAgent\x1a\'.pushC2Services.PushC2MessageFromMythic\"\x00(\x01\x30\x01\x12v\n\x1dStartPushC2StreamingOneToMany\x12&.pushC2Services.PushC2MessageFromAgent\x1a\'.pushC2Services.PushC2MessageFromMythic\"\x00(\x01\x30\x01\x42/Z-github.com/its-a-feature/Mythic/grpc/servicesb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'pushC2GRPC_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z-github.com/its-a-feature/Mythic/grpc/services'
  _PUSHC2MESSAGEFROMAGENT._serialized_start=37
  _PUSHC2MESSAGEFROMAGENT._serialized_end=208
  _PUSHC2MESSAGEFROMMYTHIC._serialized_start=210
  _PUSHC2MESSAGEFROMMYTHIC._serialized_end=304
  _PUSHC2._serialized_start=307
  _PUSHC2._serialized_end=546
# @@protoc_insertion_point(module_scope)
