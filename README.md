# py-cmake-client - Python3 client for cmake-server
py-cmake-client is an open source client for **cmake-server** protocol. It is written in Python3 using asyncio. This project is licensed under the MIT software license.

## What is cmake-server?
[cmake-server](https://cmake.org/cmake/help/latest/manual/cmake-server.7.html) is a special mode of the well-known [Cmake](https://cmake.org/) build system. When run in server mode, instead of the usual build generation, cmake will listen in a local socket/pipe, waiting for commands. Using these commands you can control the build process, and you can **get semantic information about the build**.

This mode is mainly useful to anyone who needs information about the semantics of a Cmake build. For example, using this protocol, you can know every binary the project is building, and which their sources and include directories are.

py-cmake-client implements the client side of this protocol. Once cmake is in server mode, you can use it to obtain any information about the build easily.

## Requirements
As py-cmake-client uses the new async-await asyncio syntax, you will need Python 3.5+ to run the examples. No further Python packages are needed. You will need cmake 3.7 or upper to be able to run it in server mode.

This package and the examples have been developed on and for Linux. We will be adding support for Windows soon.

## Example
In a Linux terminal, start Cmake server:
```shell
cmake -E server --experimental --pipe=/tmp/pipe
```
This will start cmake in server mode listening in the /tmp/pipe Unix socket. Note that no source/build directory is specified, as this will be done by the client.

In another terminal, ```cd``` inside py-cmake-client project, and run the demo:
```shell
python3 demo.py
```

This will cause Cmake to parse and display information about the C++ project inside the demo/ directory. Build files will be stored in /tmp/build. The following information will be displayed:
- General global Cmake settings.
- The project code model: which executables are built, which source files are used, include directories...
- The current state of the Cmake cache.

Go into the source code of main.py to learn more about this module.

## Contributing
Any ideas, suggestions, requests or any other form of contribution are always welcome!
