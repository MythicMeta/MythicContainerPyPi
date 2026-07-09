# Mythic Payload Type Container

The `mythic_container` library provides the steps for defining and utilizing payload types, c2 profiles, translation containers, webhook containers, and logging containers for Mythic. 
Mythic is a Command and Control (C2) framework for Red Teaming with the code on GitHub (https://github.com/its-a-feature/Mythic) and the Mythic project's documentation on GitBooks (https://docs.mythic-c2.net). 

## Installation

You can install the mythic scripting interface from PyPI:

```
pip install mythic-container
```

## How to use

Use it with Mythic version 3.3.0.

For the main execution of the heartbeat and service functionality, simply import and start the service:
```
import mythic_container
import [my agent | my c2 profile | my translation container | my webhooks | my loggers | my eventing | my auth]
mythic_container.mythic_service.start_and_run_forever()
```

## Chat containers

AI chat containers subclass `mythic_container.ChatBase.Chat`. The base class
provides Mythic request/response types, response helpers, typed config/secret
readers, chat-channel API token delegation, and reusable MCP tool primitives.
Provider connection semantics stay in each chat container.

See [CHAT_CONTAINERS.md](CHAT_CONTAINERS.md) for subclassing, typed settings,
response helper, MCP connection, confirmation-flow, sub-agent delegation, and
lazy tool-output examples.

## Where is the code?

The code for this PyPi package can be found at https://github.com/MythicMeta/MythicContainerPyPi
