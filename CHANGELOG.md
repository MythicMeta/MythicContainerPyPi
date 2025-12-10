
## [v0.6.8] - 2025-12-10

### Changed

- Added new `CustomBrowser` class in `CustomBrowserBase`
- Added new `HideConditionOperand` values for PayloadType's BuildParameter Hide Conditions
- Added `verifier_regex` option to Command Parameters
- Updated imports in `__init__.py` for MythicGoRPC
- Updated `SendMythicRPCCallbackCreate` to allow supplying `Cwd`, `ImpersonationContext`, and `ProcessName` parameters
- Updated `MythicRPCCallbackDisplayToRealIdSearch` to supply `None` instead of default `""` for `OperationName`
- Updated `MythicRPCTaskDisplayToRealIdSearch` to supply `None` instead of default `""` for `OperationName`
- Updated `SendMythicRPCCallbackUpdate` to allow supplying `Cwd`, `ImpersonationContext`, and `Dead` parameters
- Added `SendMythicRPCCallbackTokenSearch`
- Added `SendMythicRPCCustomBrowserSearch`
- Updated `ContainerVersion` to `"v1.4.1"`

## [v0.6.7] - 2025-10-30

### Changed

- Merging PR for getIOC and getSampleMessage fixes

## [v0.6.6] - 2025-10-29

### Changed

- Updating failsafe checks for a few MythicRPC calls to account for missing parameters

## [v0.6.5] - 2025-10-29

### Changed

- Added SendMythicRPCCallbackEdgeRemove
- Added SendMythicRPCHandleAgentMessageJson
- Updated the following MythicRPC calls to be consistent about CallbackID, AgentCallbackID, and the use of ID in general:
  - CallbackID is always an Int, AgentCallbackID is the UUID string, and all ID variables should have capital ID not Id
  - SendMythicRPCCallbackAddCommand: CallbackAgentUUID -> AgentCallbackID
  - SendMythicRPCCallbackDecryptBytes: AgentCallbackUUID -> AgentCallbackID
  - SendMythicRPCCallbackEdgeSearch: AgentCallbackUUID -> AgentCallbackID, AgentCallbackID -> CallbackID
  - SendMythicRPCCallbackEncryptBytes: AgentCallbackUUID -> AgentCallbackID
  - SendMythicRPCCallbackRemoveCommand: AgentCallbackUUID -> AgentCallbackID
  - SendMythicRPCCallbackSearch: AgentCallbackUUID -> AgentCallbackID, AgentCallbackID -> CallbackID, SearchCallbackUUID -> SearchAgentCallbackID
  - SendMythicRPCCallbackUpdate: AgentCallbackUUID -> AgentCallbackID
  - SendMythicRPCCallbackTokenCreate: TokenId -> TokenID
  - SendMythicRPCFileGetContent: AgentFileId -> AgentFileID
  - SendMythicRPCFileCreate: AgentFileId -> AgentFileID
  - SendMythicRPCFileSearch: AgentFileId -> AgentFileID
  - SendMythicRPCOperationEventLogCreate: TaskId -> TaskID, CallbackId -> CallbackID, CallbackAgentId -> AgentCallbackID, OperationId -> OperationID
  - SendMythicRPCPayloadOnHostCreate: PayloadId -> PayloadID
  - Failsafe checks are added to account for old naming, but warning messages are emitted when an old name is detected

## [v0.6.4] - 2025-10-28

### Changed

- Added "ui_position" fields to Payload Type Build Parameters and C2 Profile Parameters
- Added "dynamic_query_function" option to Payload Type Build Parameters
- Fixed an issue with bad responses fetching files from Mythic is the response code wasn't 200

## [v0.6.3] - 2025-10-22

### Changed

- Fixed an issue with missing parameters for webhook new callback data

## [v0.6.2] - 2025-10-14

### Changed

- Fixed an issue with the callbackgraph edge search that wouldn't clear results between calls

## [v0.6.1] - 2025-10-13

### Changed

- Fixed the processing for the callbackgraph edge search

## [v0.6.0] - 2025-10-07

### Changed

- Fixed an issue with streaming long output from C2 profile debugging
- Added `semver` fields to all service definitions
- C2 Profiles can now report back agent_icon and dark_mode_agent_icon just like payload types
- Payload type build parameters now have a supported_os, group_name, and hide_conditions fields
  - hide conditions allow you to specify when a specific build parameter should be hidden from user view
  - group_name allows you to group like-parameters together in the UI
  - supported_os allows you to limit build parameters to certain OS selections
- Payload type how has a c2 deviations parameter that allows you to modify fields of supported C2 profiles
  - for example - alter the defaults, change dropdown options, hide parameters completely

## [v0.5.32] - 2025-05-30

### Changed

- Updating for the PR adjusting how abstract classes are processed for command discovery in payload types

## [v0.5.31] - 2025-04-18

### Changed

- Updated CommandBase to have an optional `supported_payload_types` attribute
  - this can be used if multiple payload types are defined within one container to restrict which commands are associated with each payload type
  
## [v0.5.30] - 2025-04-16

### Changed

- Updated the custom logger code to not reinstantiate each time
- Updated the custom webhook code to not reinstantiate each time

## [v0.5.29] - 2025-04-08

### Changed

- Merged a PR to fix an issue with a legacy RPC call

## [v0.5.28] - 2025-04-03

### Changed

- Fixed the RabbitMQ endpoint name for the SendMythicRPCTagTypeGetOrCreate function

## [v0.5.26] - 2025-03-14

### Changed

- Updated some of the logging and looping for RPC calls in rabbitmq
- Updated error message output for eventing response intercepts

## [v0.5.25] - 2025-03-28

### Changed

- Added SearchParentTaskID options for MythicRPCTaskSearch
- Added MythicRPCTagCreate, MythicRPCTagSearch, and MythicRPCTagTypeGetOrCreate
- Added support for intercepting interactive task sub tasks for processing
- Added support to dynamic query functions to access "other_parameters" for context about what the other parameters have set

## [v0.5.24] - 2025-03-13

### Changed

- Fixed variable name usage

## [v0.5.23] - 2025-03-13

### Changed

- Added checks around crashing Eventing functions to catch errors and update proper event steps

## [v0.5.22] - 2025-02-10

### Changed

- Reverted some rabbitmq changes
- Updated the ordering for syncing classes so that translation containers happen before payload types

## [v0.5.21] - 2025-02-07

### Changed

- Fixed a bug with instantiating classes

## [v0.5.20] - 2025-02-07

### Changed

- Updated CommandBase to have more explicit attributes instead of abstract properties
- Adding Python pieces for CallbackUpdate time and c2 profile components via MythicRPC

## [v0.5.19] - 2024-12-14

### Changed

- Updated the MythicRPCCallbackSearch to allow specifying Payload Type names
- Updated the MythicRPCCallbackAddCommand and MythicRPCCallbackRemoveCommand functions to allow specifying list of callback IDs

## [v0.5.18] - 2024-12-13

### Changed

- Updated the SendMythicRPCSyncPayloadType functionality to force Mythic to NOT re-call the on_start functionality
  - This needs Mythic v3.3.1-rc31+

## [v0.5.17] - 2024-11

### Changed

- Added ReprocessAtNewCommandPayloadType option for create_go_tasking response
- Added AgentCallbackID and PayloadType to MythicRPCCallbackAddCommand and MythicRPCCallbackRemoveCommand messages
- Added more checks when syncing commands to make sure that duplicates aren't processed
- Added new SendMythicRPCSync* functions in the base classes for the following classes
  - PayloadBuilder
    - This one in particular has you specify a set of additional commands (potentially dynamically created) to sync with Mythic
  - WebhookBase
  - AuthBase
  - EventingBase
  - LoggingBase
  - This will allow you to make changes to your class definitions as needed and re-sync the updates to Mythic when you want

## [v0.5.16] - 2024-11-15

### Changed

- Merged Evan McBroom's PR to fix missing imports in the MythicGoRPC Folder

## [v0.5.15] - 2024-10-28

### Changed

- Added Evan McBroom's PR for multi-level inheritance (https://github.com/MythicMeta/MythicContainerPyPi/pull/12)
- Added support for specifying username/password for proxy stop
- Added support for specifying in the agent definition if original or display parameters should be used in the cli history
  - This is an effort to reduce the amount of JSON users might see if they up/down arrow on the command line
  - This defaults to false, but if you set it to true then you should make sure that your `response.DisplayParams` are a valid format for tasking
  
## [v0.4.14] - 2024-10-11

### Changed

- Changed order of calls for C2 Syncing so that RabbitMQ listeners are started before syncing over data

## [v0.5.13] 

### Changed

- Added mutex around starting/stopping the internal server
- Updated many C2 RPC functions to allow them to ask for the internal server to restart
- Added explicit update function for c2 internal server status
- Added username/password options when starting socks proxy 
- Added 'remove' option in hosting files via c2

## [v0.5.12] - 2024-09-08

### Changed

- Fixed a typo in the JSON tag for the MythicRPCCallbackTokenCreate RPC call

## [v0.5.11] - 2024-09-06

### Changed

- Updated Eventing-based functions to auto-set the eventstepinstance_id field on the response

## [v0.5.10] - 2024-09-04

### Changed

- ContainerVersion v1.3.3
- Added support for PayloadUUID and StagingUUID to be used in MythicRPCCallbackEncryptBytes and MythicRPCCallbackDecryptBytes
  - A new field, `C2Profile` must be provided with these so that the appropriate keys can be looked up
  
## [v0.5.8] - 2024-08-27

### Changed

- Fixed awaited functions in eventing containers

## [v0.5.7] - 2024-08-27

### Changed

- Added in container ReSync message acknowledgement for consuming containers to indicate uptime

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