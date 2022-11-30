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

## Creating behavioural objects in Fedora 6
### Install the python packages
```
python3 -m venv dps_venv
source dps_venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Copy the environment variables

Copy the template environment variables file `.env.template` to `.env`. It has default values for working with Fedora running in docker.

```
cp .env.template .env
```

### Run the code to create the behavioural objects

```
python create_behavioural_objects.py
```

The script `create_behavioural_objects.py` creates 5 objects in fedora, as set out in https://github.com/tomwrobel/dps/issues/1.

- Metadata only object

  - a single 2Kb metadata file

- Binary file object

  - 2 binary files 5Mb in size and a single metadata file 2Kb in size

- Large binary file objects

  - 5 binary files 1Gb in size and a single metadata file 2Kb in size

- Complex binary file objects

  - 100 binary files 500Mb in size and a single metadata file 2Kb in size

- Very large binary file objects

  - This is defined as 1 256Gb file and a single metadata file 2Kb in size.

  - In order for this to work, a file is first created, copied to a shared volume, which fedora has access to and then do a POST asking Fedora to copy an external file.

  - **Note:**

    In my development environment, I can create an object in Fedora with a file upto size 10Gb. Anything more than this, and Fedora throws a 500 error. This size can be varied by changing the value in the environment variable `VERY_LARGE_FILE_SIZE`. It is currently set to 10GB.



