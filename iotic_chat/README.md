# Iotic Chat Messenger

#### Table of contents
1. [What it does](#what-it-does)
2. [How it works](#how-it-works)
3. [Get your thing](#get-your-thing)
4. [Define feed](#define-feed)
5. [Sharing and retrieving data](#sharing-and-retrieving-data)
6. [Subscribing to others](#subscribing-to-others)
7. [Running your source](#running-your-source)

## Why?

This simple example uses the well-known paradigm of a chat room to show some concepts of programming in Iotic Space.
The Iotic Chat Messenger is a tool that shows:
1. The publish/subscribe model of Iotic Space
2. Search and dynamic binding to other things

## What?

### What it does

The Chat Messenger sends users' messages via a feed (in the diagram, from Bob to Alice).
The client thing at the far end follows the feed and shows the message.
The process is repeated in reverse by the original thing so that Bob can see Alice's messages.

```
+-----------------------+                                                 +-----------------------+
|       BOB AGENT       |                                                 |      ALICE AGENT      |
+-----------------------+                                                 +-----------------------+
|  +-----------------+  |   Feed out     +---------------+    Feed in     |  +-----------------+  |
|  |                 +------------------>+  BOB MESSAGE  +------------------>+                 |  |
|  |       BOB       |  |                +---------------+                |  |      ALICE      |  |
|  |      THING      |  |   Feed in      +---------------+    Feed out    |  |      THING      |  |
|  |                 +<------------------+ ALICE MESSAGE +<------------------+                 |  |
|  +-----------------+  |                +---------------+                |  +-----------------+  |
+-----------------------+                                                 +-----------------------+
```
## How?

### How it works
This tool automatically creates an explicit thing for messaging communication inside one of your agents
using the Iotic Space. This thing publishes the name of the user with the text input into the feed out and
starts following the rest things of its same kind, consuming their feeds.

### Get your thing

The first step is create the thing in your agent. This code sets up and returns the thing.
If it doesn't exist it will create a new one, if it does, the infrastructure will return you the existing one.

 ``` python
def setup_thing(client, name):
    print("Connecting to your thing", sep=' ', end=' ... ')
    sys.stdout.flush()
    # 1- Get/Create a thing with the given name
    my_thing = client.create_thing(name)
    # 2-Add tags for searching
    add_tags(my_thing)
    # 3-Add metada to the thing
    with my_thing.get_meta() as meta_thing:
        add_metadata_information(meta_thing)
    # 4-Makes the thing visible
    my_thing.set_public()

    return my_thing
 ```

### Define the message feed

After getting the thing, it defines a feed to share its data with others. This function creates a feed in three steps and returns the new or existing feed.

``` python
def setup_thing_feed(my_thing):

    # 1-Get feed from thing
    my_feed = my_thing.create_feed('message_data')
    # 2-Put metadata information
    with my_feed.get_meta() as meta_feed:
        meta_feed.set_label('Message data')
        meta_feed.set_description('data sended in the messages')
    # 3-Create skeleton structure
    my_feed.create_value('user', Datatypes.STRING, lang='en', description="Name of the user")
    my_feed.create_value('message', Datatypes.STRING, lang='en', description="Message sent by the user")

    return my_feed
```

### Sharing and retrieving data
To send thing's data to others it sends the template of its feed, filled with username and message.

``` python
    # fill in your values using the template "skeleton"
    my_feed_skeleton.values.user = user
    # ...
    my_feed_skeleton.values.message = text

def share_data(my_feed, my_feed_skeleton):
    my_feed.share(my_feed_skeleton)
```

When a user is disconnected, the application sends a message to the other users

``` python
def share_goodbye_data(my_feed, my_feed_skeleton):

    my_feed_skeleton.values.message = my_feed_skeleton.values.user + ' left the the chat'
    my_feed_skeleton.values.user = ''

    my_feed.share(my_feed_skeleton)
```

To manage all the data sent by other things it has a callback function.
This function is called every time the thing receives feed (in).
The information will be shown this way: `<user>: <message>`

``` python
def follow_feed_callback(data):

    values = data['parsed'].values
    text = '>' + values.user + ': ' + values.message

    print(text)

```

### Subscribing to others

The first time you run the application, after your thing and your feed is created,
the program automatically searches for other things with the same tags and subscribe them to yours.
To make it possible we attached a function callback to each feed.


``` python
def connect_subscriptions(client, my_thing, callback_function):

    # Get tags to search other thing with same tags
    my_thing_tags = my_thing.list_tag()
    string_tags = ' '.join(my_thing_tags['en'])

    iotic_chat_things = client.search_reduced(text=string_tags)

    # Delete our thing from the search result if exists
    if my_thing.guid in iotic_chat_things:
        del iotic_chat_things[my_thing.guid]

    print("Connecting subscriptions")
    sys.stdout.flush()

    # Get global Point ID (gpid) from this information and wire up the follow to the callback
    for key in iotic_chat_things:
        for feed_guid, feed_type in iotic_chat_things[key].items():
            if feed_type == 'Feed':
                my_thing.follow(feed_guid, None, callback_parsed=callback_function)
```

Finally it executes a function in order to follow the new users of the chat room without rebooting.
Now, when someone subcribes to your thing it will follow the subscriber too.
There's a callback for this called `register_callback_subscription`.
This example uses the `partial` idea to send the client to this function
via a keyword parameter rather than using a global

*Note* the use of `callback_parsed=follow_feed_callback` the callback_parsed function is called with a
populated template for the feed, making the data extraction easier.

``` python
    # Create a new function which recieves a iotic-client
    manage_new_subsciptions = partial(incoming_subscription_callback, client=client)
    client.register_callback_subscription(manage_new_subsciptions)


# This fuction is called when someone is subscribed to your thing
def incoming_subscription_callback(data, client=None):

    print('New user is subscribed')
    # Your thing with new subscriptor
    subscribed_thing = client.create_thing(data['entityLid'])

    # Your feed's thing
    thing_feed = subscribed_thing.create_feed(data['lid'])

    # Gets all the followers even the new one
    feed_followers = thing_feed.list_followers()

    for key in feed_followers:
        # Get external things subscribed to you
        external_thing = client.describe(feed_followers[key])

        # Get the points from external thing
        external_thing_points = external_thing['meta']['points']
        for point in external_thing_points:

            if point['type'] == 'Feed':
                # Attach callback to see new messages
                subscribed_thing.follow(point['guid'], None, callback_parsed=follow_feed_callback)
```


### Running your source

1. Create `Agent_File.ini` with credentials retrieved through Iotic Space.
2. Put the `Agent_File.ini` in the same folder as the Chat Messenger script
3. Execute the python script with the arguments "AgentFile" and "ThingName"
4. Repeat 1,2,3 on another machine and get chatting!

`Note` you might need to set the PYTHONPATH so that your python code can find the IoticAgent.
There's a helpful post
[here](http://stackoverflow.com/questions/4580101/python-add-pythonpath-during-command-line-module-run)
on stack overflow

```bash
$ PYTHONPATH=/path/to/agent:. python main.py Agent_File.ini ThingName
```
