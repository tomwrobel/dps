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

### Run the code to create the behavioural objects

```
python create_behavioural_objects.py
```

This assumes the following:

```
host     = 'localhost'
port     = '8080'
username = 'fedoraAdmin'
password = 'fedoraAdmin',
base_url = '/fcrepo/rest'
use_https = False
test_data_dir = './test_data'
```

To use different values, instantiate BehaviouralObjects with the required values in [line #5](https://github.com/tomwrobel/dps/blob/main/create_behavioural_objects.py#5), `create_behavioural_objects.py`

```
b = BehaviouralObjects(host=host, port=post, username=username, password=password,
                 base_url=base_url, use_https=use_https, test_data_dir=test_data_dir)
```

