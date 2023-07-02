### Tinkoff SRE Middle

# Practice #1

Steps to run:
Clone repo:
```
git@github.com:denisko890Courses/tinkoff_SRE.git
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
