# Mythic Payload Type Container

The `mythic_container` library provides the steps for defining and utilizing payload types, c2 profiles, translation containers, webhook containers, and logging containers for Mythic. 
Mythic is a Command and Control (C2) framework for Red Teaming with the code on GitHub (https://github.com/its-a-feature/Mythic) and the Mythic project's documentation on GitBooks (https://docs.mythic-c2.net). 

## Installation

You can install the mythic scripting interface from PyPI:

```
pip install mythic-container
```

## How to use

Use it with Mythic version 3.0.0.

For the main execution of the heartbeat and service functionality, simply import and start the service:
```
import mythic_container
import [my agent | my c2 profile | my translation container | my webhooks | my loggers]
mythic_container.mythic_service.start_and_run_forever()
```

## Where is the code?

The code for this PyPi package can be found at https://github.com/MythicMeta/Mythic_Container 
