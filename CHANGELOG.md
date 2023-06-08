
## [v0.2.11-rc03] - 2023-06-08

### Changed

- Updated the processing of commands to only parse arguments in OPSECPre and CreateTasking
- Updated the processing of commands to add unknown args for other stages of tasking in case CreateTasking manipulates the total arguments


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