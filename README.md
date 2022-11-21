# DPS

This is a project to manage code and tests related to the ORA-developed test of Fedora 6 as an API layer for the BDLSS Digital Preservation Service.

A description of the overall set of tasks and background can be found on the wiki: https://github.com/tomwrobel/dps/wiki/home

## Getting Started with running [Fedora 6.x](https://wiki.lyrasis.org/display/FEDORA6x)
Clone the repository with git clone https://github.com/tomwrobel/dps.git.

Ensure you have docker and docker-compose. See [notes on installing docker](https://github.com/tomwrobel/dps/wiki/Installing-Docker).

Open a console and try running `docker -h` and `docker-compose -h` to verify they are both accessible.

Create the environment file `.env`. You can start by copying the template file [.env.template](https://github.com/tomwrobel/dps/blob/main/.env.template) to `.env` and customizing the values to your setup.

Start the docker containers for Fedora 6
```bash
$ docker-compose up -d
```
You should see the containers being built and the services start.
