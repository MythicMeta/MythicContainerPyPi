
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