### Tinkoff SRE Middle

# Practice #1
Requirements:
Python 3.11.3
Docker
Docker-compose

Clone oncall Repository:

```
git clone -b v2.0.1 https://github.com/linkedin/oncall.git
```

!!!
Don't forget enable Debug mode if you are using Docker-Compose. View file oncall/config/config.docker.yaml

Fix problem with incorrect string for DB(Tested on Ubuntu 20.04 with sed 4.7):

```
sed -i "s/INSERT INTO \`team\` VALUES (1,'Test Team','#team','#team-alerts','team@example.com','US\/Pacific',1,NULL,0,NULL);/INSERT INTO \`team\` VALUES (1,'Test Team','#team','#team-alerts','team@example.com','US\/Pacific',1,NULL,0,NULL,0);/" ./oncall/db/dummy_data.sql
```

Steps to run:
Clone repo:
```
git clone git@github.com:denisko890Courses/tinkoff_SRE.git
```

Install requirements.txt:

```
cd practice1
pip3 install -Ur requrements.txt
```

Create or update file teams.yaml with actual teams, users, dates

Run oncall_api.py

```
bin/python3 ./oncall_api.py http://${oncall_url}:${oncall_port}/ ${username} ${password} ./teams.yaml
```
