# Overview

Annotated Python3 examples using the Python v3.2+ (and 2.7.9+) Iotic Space (https://iotic-labs.com) agent (client). 

They are written to accompany the "Getting Started" tutorials on the Iotic Labs Developer Portal, and also act as standalone quick-start examples introducing beginners to Iotic Space.

# Tutorials

The "Getting Started" tutorials can be accessed here: https://developer.iotic-labs.com/ (log in to view).

# To run examples

(Follow "Getting Started" tutorials for a step-by-step guide.) 

- Install the Python Iotic Agent .

- Create an owner ID, and join a Container through the Iotic Labs Developer Portal.

- Create or download from the Iotic Space UI an Agent initialisaion (.ini) file, containing your epid, password, and token. 

- Make sure the name of your Agent's config .ini matches that in the example you are running. Either create a new one, or rename an existing one to match.

- Alter fields in script as required to create own name, use correct Agent, or insert Point guids where needed.

- Set the pythonpath.

- To run:
$ python3 name_of_example.py 



# Licence

All of the code examples are made available to you under the terms of the Apache 2.0 licence, the terms of which are defined here: https://github.com/Iotic-Labs/py-application-examples/blob/master/LICENSE



# Examples included

CONNECTING YOUR AGENT

01_its_alive.py
Minimum script wiring up your agent to Iotic Space.

02_wired_up_catchall.py
Adds callback to print any data picked up by the catchall.


CONNECTING YOUR THING

03.1_connect_thing.py
Uses 'create_thing' to wire up the Iotic Thing you created in the UI. 
(Note: if you havent already created it, this will create a new Thing.)

03.2_connect_thing_see_handiwork.py
Wires up your Iotic Thing, and prints what you have set up in the UI.

03.3_connect_thing_following.py
Wires up your Thing, adds callback and prints data from the follow you arranged in the UI.

03.4_connect_thing_following_hardcoded.py
Wires up your Thing, adds callback and prints data from feed using hardcoded gpid.

CREATING A THING

04.1_create_minimal_thing.py
Creates a shiny new Thing in code.

04.2_create_thing_metadata_tags.py
Creates a fresh new Thing in code, and adds metadata and tags. 
(Note: if you ran 4.1 first, it's not fresh anymore, you are connecting this script to the same virtual Thing)

IOTIC INTERACTIONS

Feeds

05.1_follow_feed.py
Creates a Thing and follows a Feed using the gpid.
Prints data recieved.

06.1_advertise_feed.py
Creates a Thing and advertises a Feed.

06.2_advertise_feed_metadata.py
Creates a Thing, advertises a Feed.
Adds metadata.
Makes public

06.3_advertise_feed_share.py
Creates a Thing, advertises and describes a feed.
Adds metadata and makes public
Shares data.

Controls

07.1_offer_control.py
Creates a Thing, offers a control.
(keep private)

07.2_offer_control_metadata.py
Creates a Thing, sets to private, adds metadata.

08.1_attach_to_control.py
(attach to control you just made)
Creates a Thing, attaches to a control using hard-coded Point guid.

08.2_actuate_control_ask.py
Creates a Thing, attaches to remote Control using hard-coded Point guid.
Actuates control using ask.





