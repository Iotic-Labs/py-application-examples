# Iotic Thing Runner examples


#### Table of contents
1. [What it does](#what-it-does)
2. [Dependencies](#Dependencies)

## What it does

A set of paired examples showing the four interactions of a Thing
1. Advertise and share a Feed of your own
2. Follow someone else's feed
3. Advertise a control of your own
4. Attach and actuate someone else's control.

In each case there will be examples covering different ways of binding (by Lid, Pid or guid or by searching) and
different ways of approaching data (e.g. via feed templates and callback parsed or just plain)

### Plain template
The [plain template](./plain_template.py) is just the empty ThingRunner template for you to fill in.
The [plain template background](./plain_template_background.py)
 is another empty ThingRunner template for you to fill in - but this one runs in the background, allowing you to
 other things in the foreground (run a graphing package, for instance)

### Basic Share and Follow
The [basic share](./follow_feed/share_basic.py) Creates a thing, a feed and their metadata in `on_startup()`.
It uses its `main()` method to create a loop which shares the feed on a timer.

The [basic share error](./follow_feed/share_basic_error.py) Creates a thing, a feed and their metadata in
`on_startup()`.
It uses its `main()` method to create a loop which shares the feed on a timer.
It demonstrates the use of the `RetryingThingRunner` and the `on_exception()` method.
`RetryingThingRunner` is a subclass of `ThingRunner` that automatically handles network errors and continues
to retry indefinitely. If you want to handle any other exceptions, you have to overload `on_exception()`, call
the superclass' method and then you have a place to handle any other (unhandled) exceptions that might occur

The [basic follow](./follow_feed/follow_basic.py) Creates a thing and binds a `callback_parsed` method to receive the
data from the [basic share](./follow_feed/share_basic.py) thing.  The shared feed data is extracted in the parsed
callback by using `filter_by` to search within the feed for values that match certain criteria.
`NOTE` Requires [basic share](./follow_feed/share_basic.py) to be running to work

The [basic follow catchall](./follow_feed/follow_basic_catchall.py)
Creates a thing and binds a `catchall` and a `catchall_parsed`
method to receive the data from the [basic share](./follow_feed/share_basic.py) thing as before.
In `on_startup()` the `client.catchall_feeddata` method is called.  This routes any recent shares
have either been queued for this Thing while it has been offline or shares for feeds with no explicit callback.
`NOTE` Requires [basic share](./follow_feed/share_basic.py) to be running to work

The [basic follow recent](./follow_feed/follow_basic_recent.py) Creates a thing and binds a `callback_parsed`
method to receive the data from the [basic share](./follow_feed/share_basic.py) thing as before.
In `on_startup()` the `remote_point.get_recent()` method is called.  This returns however many recent shares
there are saved by the remote feed. At the moment, there isn't a way to have the recent data parsed, so we
have to use hard-coded keys in `__callback_recent()`
`NOTE` Requires [basic share](./follow_feed/share_basic.py) to be running to work

The [basic follow restore](./follow_feed/follow_basic_restore.py) Creates a thing and binds a `callback_parsed`
method to receive the data from the [basic share](./follow_feed/share_basic.py) thing as before.
In `on_startup()` the `client.list_connections()` method is called. This returns a list of all the subscriptions
this thing might have had in the past and re-binds them.  Effectively restoring state.
callback by using `filter_by` to search within the feed for values that match certain criteria.
`NOTE` Requires [basic share](./follow_feed/share_basic.py) to be running to work

The [basic follow subscription](./follow_feed/follow_basic_subscription.py) Creates a thing and then,
in `on_startup()`,  the `client.register_callback_subscription()` method is called.
This registers a callback that is called when a subscription is made on your behalf (probably in the UI, but it
could be you following something in another thread).
The subscription callback gets called with either a `RemoteFeed` or a `RemoteControl` object which can be further
inspected to see what callback to bind to its feeddata.
`NOTE` Requires [basic share](./follow_feed/share_basic.py) to be running to work

The [basic follow database](./follow_feed/follow_basic_database.py) Creates a thing and then,
in `on_startup()`,  the `client.register_callback_subscription()` method is called.
This registers a callback that is called when a subscription is made on your behalf (probably in the UI, but it
could be you following something in another thread).
When the subscription callback is called, the feed is added to a database table of feeds and when the data arrives
in the feeddata callback, the data received is added to another database table to hold feed values.

This example uses the popular SQLAlchemy ORM abstraction and SQLite3. Owing to the nature of SQLite's session thread
handling, this example uses a python queue to communicate between the callback functions
(which are called in the agent's thread) and the main thread which holds the session object.
`NOTE` Requires [basic share](./follow_feed/share_basic.py) to be running to work

### Basic Offer and Attach
The [basic offer](./attach_control/offer_basic.py) Creates a thing, a control and their metadata in `on_startup()`.
When it creates the control it binds a `callback_parsed` method to receive the
data from the [basic attach](./attach_control/attach_basic.py) thing.  The control request data is extracted
in the parsed callback by using `filter_by` to search within the feed for values that match certain criteria.

The [basic attach](./attach_control/attach_basic.py) Creates a thing and attaches to the control in
[basic offer](./attach_control/offer_basic.py), in `on_startup()`.
It uses its `main()` method to create a loop which calls `ask()` on the control.
`NOTE` Requires [basic offer](./follow_feed/offer_basic.py) to be running to work

The [basic attach tell](./attach_control/attach_basic_tell.py) Creates a thing and attaches to the control in
[basic offer](./attach_control/offer_basic.py), in `on_startup()`.
It uses its `main()` method to create a loop which calls `tell()` on the control.  `tell()` requires the offerer
of the control to confirm whether it has done it. In this example we deliberately fail to see this confirmation
working.
`NOTE` Requires [basic offer](./follow_feed/offer_basic.py) to be running to work

### Following by search (owned and global)
[search owned](./follow_feed/follow_search_local.py), Creates a Thing in `on_startup()` and then uses
`client.search(search_text, scope=SearchScope.LOCAL_OWN)` to get a list of things it owned by the same owner that match the text.
It then binds to the first thing's feed.
`NOTE` Requires [basic share](./follow_feed/share_basic.py) to be running to work

[search owned: by property](./follow_feed/follow_search_local_property.py), Creates a Thing in `on_startup()` and then uses
`client.search_property(predicate, scope=SearchScope.LOCAL_OWN)` to get a list of things owned by the same owner.
This search is *by property*, i.e. using the semantic properties in the additional metadata of the thing to find it.
This example is contrived, but uses matching on a example category in a taxonomy of categories.
Predicates are specified using python tuples of predicate and object (IOTICS.category, IOTICS_CATEGORIES.Example)

It then binds to the first thing's feed.
`NOTE` Requires [basic share](./follow_feed/share_basic.py) to be running to work

[search global](./follow_feed/follow_search_global.py), Creates a Thing in `on_startup()` and then uses
`client.search()` to get a list of things that match the criteria.
It then binds to the first thing's feed.
`NOTE` Requires [basic share](./follow_feed/share_basic.py) to be running to work

[search global: by property](./follow_feed/follow_search_global_property.py), Creates a Thing in `on_startup()` and then uses
`client.search_property(predicate, scope=SearchScope.LOCAL_OWN)` to get a list of things
This search is *by property*, i.e. using the semantic properties in the additional metadata of the thing to find it.
This example is contrived, but uses matching on a example category in a taxonomy of categories.
Predicates are specified using python tuples of predicate and object e.g. (IOTICS.category, IOTICS_CATEGORIES.Example)

## Note on Semantics
Recent releases of Iotic Space and the agent have added a few new API methods to add and remove semantic triples from things.
These changes have been added in example form to [basic share](./follow_feed/share_basic.py), and to
the [search global: by property](./follow_feed/follow_search_global_property.py)
and [search owned: by property](./follow_feed/follow_search_local_property.py) examples.

- [basic share](./follow_feed/share_basic.py) adds a call to `Thing.create_property()` to add a semantic triple to describe the thing
- [search global: by property](./follow_feed/follow_search_global_property.py) and [search owned: by property](./follow_feed/follow_search_local_property.py)
use this triple to search for the thing (using `Client.search_property()`), yielding more accurate results than text-based search.

The semantics used in the examples are simulated in that the ontologies don't exist, but show you a way to create a category for your things.

We imagine this definition of the iotics:category property in one ontology with this definition of iotics:Category as a skos:Concept

```
iotics:category
    rdf:type rdf:Property ;
    rdfs:range iotics:Category  .

iotics:Category
    rdf:type skos:Concept .
```

...and in another ontology many definitions of categories as a subclasses of iotics:Category

```
iotics_category:Example
    rdfs:subclassof iotics:Category .

iotics_category:Weather
    rdfs:subclassof iotics:Category .

iotics_category:Civic
    rdfs:subclassof iotics:Category .

```

# Dependencies
All examples require the Iotic Agent
`pip3 install py-IoticAgent`

Property examples require RDFLib to handle the semantic namespaces. It should be included in py-IoticAgent, but just in case...
`pip3 install rdflib`

The database example requires
- SQLite3 (see [here](http://www.sqlitetutorial.net/download-install-sqlite/) )
- SQLAlchemy (see [here](https://www.pythoncentral.io/how-to-install-sqlalchemy/) )
