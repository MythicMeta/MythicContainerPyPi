
## [v0.5.6] - 2024-08-21

### Changed

- Added the option for `limit_credentials_by_type` for CredentialJson command parameters to limit the options in the UI dropdown to certain types

## [v0.5.5] - 2024-08-13

### Changed

- Updated the processing of commands to not check command class module's parent path name, too error prone

## [v0.5.4] - 2024-08-07

### Changed

- Updated payload type definition to support using legacy "note" field or updated "description" field
- Updated typed array parsing to fix bugs

## [v0.5.3] - 2024-07-31

### Changed

- fixed typo when building payload
- 
## [v0.5.1] - 2024-07-31

### Changed

- fixed typo when building payload

## [v0.5.0] - 2024-07-09

### Changed

- This is updated to work with Mythic 3.3+ and will cause some issues with Mythic 3.2 and below
- New Auth
- New Eventing
- New Build/C2/Command parameter options of ChooseOneCustom and FileMultiple
- New Logging options
- Added MythicRPCAPITokenCreate
- Added MythicRPCCallbackNextCheckinRange
- Added MythicRPCFilebrowserParsePath

## [v0.4.19] - 2024-04-29

### Changed

- Updated PayloadTypes to store lowercase names locally and check against module names lower case
  - This fixes an issue where a Capital payload type name and a lowercase module name won't sync together
  
## [v0.4.18] - 2024-04-11

### Changed

- Fixed a typo in the SendMythicRPCFileBrowserCreate

## [v0.4.17] - 2024-04-08

### Changed

- Added CallbackDisplayID, PayloadType, IsInteractiveTask, and InteractiveTaskType to task search and task log data

## [v0.4.16] - 2024-04-08

### Changed

- Added InteractiveTaskType dictionary lookup in MythicCommandBase based on InteractiveTaskType
- Updated the processing of payload type commands to be based on root module name

## [v0.4.14] - 2024-03-20

### Changed

- Added `Number` parameter type to build parameters to match C2 Profile Parameters
- Updated package dependencies

## [v0.4.13] - 2024-03-05

### Changed

- Added OperatorUsername and OperationName to PTTaskMessageCallbackData fields with Mythic 3.2.19

## [v0.4.11] - 2024-03-04

### Changed

- Added `agent_type` attribute for Payload Types

## [v0.4.10] - 2024-02-13

### Changed

- Added access to "Secrets" in tasking, dynamic queries, new callbacks, and payload builds
- Added `message_format` attribute for Payload Types for use later

## [v0.4.8] - 2024-01-23

### Changed
- Fixed a bug where in some situations old style tasking would get improperly formatted typedarray args

## [v0.4.7] - 2024-01-22

### Changed

- Fixed a breaking bug in parsing tasking for old create_tasking style when checking for typedArray functions

## [v0.4.6] - 2024-01-22

### Changed

- Fixed a path that was too long on windows

## [v0.4.5] - 2024-01-16

### Changed

- Updated the c2 profile sub-process code to not cause deadlocks and only keep the latest 100 messages from debug output

## [v0.4.4] - 2024-01-13

### Changed

- Updated the typedarray_parse_function to be called after parse_dictionary or parse_arguments is called
  - Parsing dictionary and arguments should simply make sure that there's data in the typed array parameter
  - The `typedarray_parse_function` will be called if the value after parse_dictionary or parse_arguments is `[ ["", "string"], ["", "value" ]]` or `[ "value", "value" ]` formats.
    - The first format with the empty first value is how Mythic's UI parsing will interpret the arrays

## [v0.4.3] - 2024-01-13

### Changed

- Updated the DynamicFunctionQuery attributes to be optional and not required

## [v0.4.2] - 2024-01-11

### Changed

- Removed the FileRegister MythicRPC Call
- Updated the FileCreate MythicRPC Call to allow TaskID, PayloadUUID, or AgentCallbackID to be supplied
  - This makes it possible to register new files with Mythic during payload build, translation containers, etc
- Updated the DynamicQuery Parameters to now also have PayloadOS, PayloadUUID, CallbackDisplayID, and AgentCallbackID
  - This should make it easier to use MythicRPC functionality to make more informed decisions
- Updated container version to v1.1.4, Needs Mythic v3.2.13+
  
## [v0.4.1] - 2024-01-10

### Changed

- Added a new optional `on_new_callback` function to the PayloadType class
  - This allows you to take additional actions on a new callback based on your payload type
- Added new MythicRPC* functions for searching edges associated with a callback and for creating new tasks for a callback
- Needs Mythic v3.2.12+ to leverage new functionality

## [v0.3.6] - 2023-12-22

### Changed

- Fixed an issue with async timeout in rabbitmq from issue #10

## [v0.3.5] - 2023-12-11

### Changed

- Fixed the MythicRPCEncryptBytes and MythicRPCDecryptBytes functions to base64 decode the responses back from Mythic

## [v0.3.4] - 2023-11-08

### Changed

- Added support for 'Number' parameter types for C2 Profiles

## [v0.3.3] - 2023-11-07

### Changed

- Added support for 'File' parameter types for C2 Profiles

## [v0.3.0] - 2023-10-02

### Changed

- Added gRPC classes for Push C2
- Added C2 RPC calls for hosting files
- Added PayloadType RPC calls for parsing TypedArray values
- Added TypedArray values for Build, Command, and C2 parameters
- Updated ProxyStart/ProxyStop commands to take an optional local_port of 0 and have it dynamically chosen

## [v0.2.11-rc03] - 2023-06-08

### Changed

- Updated the processing of commands to only parse arguments in OPSECPre and CreateTasking
- Updated the processing of commands to add unknown args for other stages of tasking in case CreateTasking manipulates the total arguments

## [v0.2.11-rc7] - 2023-06-29

### Changed

- Updated the MythicRPCTaskCreateSubtaskGroupMessageResponse response to take back a group of IDs rather than a single ID

## [v0.2.11-rc6] - 2023-06-26

### Changed

- Updated to add `wrapped_payload_uuid` field for wrapper payloads to access UUID of wrapped payload during build
- Updated token handling to always default to `None` if token id is None or 0

## [v0.2.11-rc02] - 2023-06-01

### Changed

- Updated the logging/webhook listeners to use unique names so we don't round robin messages

## [v0.2.8-rc05] - 2023-05-18

### Changed

- Updated the type validation keys from a typo for CredentialJson parameter types

## [v0.2.8-rc04] - 2023-05-17

### Changed

- Decoded response searches back to string instead of leaving as bytes

## [v0.2.8-rc02] - 2023-05-12

### Changed

- Fixed some bugs with how translation services handle timeouts and reconnects


## [0.2.8-rc01] - 2023-05-10

### Changed

- Updated the final JSON string from tasking to not include Null values
- Updated the create tasking's Stdout to include information about which arguments aren't getting used and why