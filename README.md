# :traffic_light:P O L A R I S
An object oriented approach to legible production queries.
Class Domain:
  - Actor (Back-End for user-facing)
  - Reactor (Server Sessions [With UI Monitor] )
  - Entity (Archetypal discrete object)


### Aims: ###
- To develop an entity-centered class environment that use actor classes and reactor classes negotiate requests/pushes.
- To distribute a low-end-user-cost product for production teams. (reliant on cloud [airtable @$20/mo]).
- To open a channel of community development to fork into sub-industries.

#### :camel::mountain: Environment

## Installing
#### Requirements
Anticipating initial development in `3.5`.
Anticipating utilizing portable `PySide2` or `Qt.py`
The ever lovely `requests` package is needed.
If you do not have `requests`, simply open a shell/cmd window and
```bash
$ pip install requests
```
Ramayana uses Airtable as a backend and has a nice python wrapper from @gtalarico.
https://github.com/gtalarico/airtable-python-wrapper
You shouldnt have to do install anything for that. 
## Usage
```
import vayu
```
From here, create a session manager. 
```
sm = vayu.SessionManager()
sm.build_all_sessions()
```
Now we have a session manager to collect all of our bases, and it has initialized each table within the base. 
We are ready to query/push. 
```python
sm.base['Avatar2']['Shots'].get_all() #a readable structure for calls. .get_all retrieves a json of the table.
```
For the shotgun_api oriented coders, there are similar implementations:
For retrieving entity json lists:
```python
sm.find("Shot", fields=["code", "sequence", "tasks"] , formula="{frame_count}>100"  )
```
as well as updating entities. (The following is also how to upload attachments) 
```python
sm.update('Shot', id="recTVVSsw2ldkfu2S", fields={"Attachments": [{'url' : "https://i.imgur.com/iVfx5uw.png"}]}, project="Avatar2" )
```
Tables will also be retrieved and stacked into a full base object that can be indexed against itself with whatever records reference eachother in the base. 
