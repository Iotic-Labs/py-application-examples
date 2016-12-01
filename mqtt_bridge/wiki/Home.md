
## Iotic Labs MQTT Bridge

### Overview
This bridge provides a MQTT interface similar to the python IoticAgent Core Client.

The MQTT bridge represents one Agent, there is no authentication on the requests.


### [Requests](#requests_head)

Resource  |  Type  |  Purpose
---|---|---
entity | create | [Create a new entity](#entity_create)
entity | rename | [Rename an entity](#entity_rename)
entity | reassign | [Reassign an entity to agent](#entity_reassign)
entity | delete | [Delete an entity](#entity_delete)
entity | list | [List entities](#entity_list)
entity | list | [List all entities across agents](#entity_list_all)
entity | list | [Get raw metadata](#entity_meta_get)
entity | update | [Set raw metadata](#entity_meta_set)
entity | update | [entity set public](#entity_setpublic)
entity | create | [entity add tags](#entity_tag_set)
entity | list | [entity list tags](#entity_tag_list)
entity | delete | [entity delete tags](#entity_tag_delete)
point | create | [point create feed](#point_create_feed)
point | create | [point create control](#point_create_control)
point | create | [feed share](#point_share)
point | create | [point add tags](#point_tag_set)
point | list | [point list tags](#point_tag_list)
point | delete | [point tag delete](#point_tag_delete)
value | create | [value create](#value_create)
value | list | [value list](#value_list)
value | delete | [value delete](#value_delete)
sub | create | [sub create](#sub_create)
sub | create | [sub create local](#sub_create_local)
sub | list | [sub list](#sub_list)
sub | delete | [sub delete](#sub_delete)
sub | create | [sub ask](#sub_ask)
sub | create | [sub tell](#sub_tell)
search | create | [search](#search)
describe | create | [describe](#describe)
feeddata | list | [get incoming unsolicited feeddata](#feeddata)
controlreq | list | [get incoming unsolicitedcontrolreq](#controlreq)
unsolicited | list | [get incoming other unsolicited](#unsolicited)


### Topic request layout
Item | Purpose
---|---
**Prefix** | All messages start with ioticlabs/
**Request** | Requests (client to bridge) req/ and responses (bridge to client) rsp/
**Device** | Device ID (free text) to allow Things to filter their messages
**Msg** | Request ID (free text) to allow Things to filter certain responses
**Command** | One of create, list, update, delete (Maps to HTTP REST interface POST, GET, UPDATE, DELETE)
**Path** | Starts with resource (e.g. entity) and is followed by one or more arguments (separated by '/'), which identify existing resources or are constants. The order of arguments identifies them.
**Payload** | (string) Contains any other data required by a given request in form of a JSON-encoded dictionary, utf-8 encoded with a maximum size of 64*1024 bytes

### Response layout
Item | Purpose
---|---
**Code** | (int)
200 | Synchronous request completed (e.g. entity listing)
201 | A resource was created (e.g. container, owner or user). If a 200 response is received for a creation request, this indicates the resource did already exist.
204 | A resource was deleted (e.g. container, owner or user)
400 | Malformed request (e.g. missing parameter or failed validation)
405 | Request type not available for this resource type
410 | An item in the path or arguments required for the request does not exist
5** | Server error
**Payload** | (string) JSON-encoded dictionary, utf-8 encoded with a maximum size of 64*1024 bytes, dependent on response type
t | QAPI Message Type (e.g. 4 = IoticAgent.Core.Const.E_CREATED - see [Const.py](https://github.com/Iotic-Labs/py-IoticAgent/blob/master/src/IoticAgent/Core/Const.py))
p | QAPI Message Payload
p['m'] | (string/null) Optional message describing problem
p['c'] | Optional reason code in case of problems (e.g. 3 = IoticAgent.Core.Const.E_FAILED_CODE_MALFORMED)
p['r'] | Resource type (e.g. 1 = IoticAgent.Core.Const.R_ENTITY)

#### Note on Payloads:
For `2**` response codes the payload is the QAPI complete request payload.

For listing the limit,offset go into the payload.

#### Note on Errors:
A `200` response does not mean that your request succeeded, rather that it went into the infrastructure and back successfully.
You will need to check the payload `'t'` value to see if successful.  Abbreviated table below

`'t'` value | Meaning
---|---
 `'t':1` | COMPLETE
 `'t':3` | FAILED - see `'c':` for reason
 `'t':4` | CREATED
 `'t':5` | DUPLICATED
 `'t':6` | DELETED

Full list of shortcodes here: [[Shortcodes|Shortcodes]]

A `4**` response code means that your request parameters failed validation.



## MQTT Command Index
The MQTT bridge follows the standard RESTful commands create (POST), list (GET), update (PUT), delete (DELETE).

Command | Meaning
---|---
create | Create a resource
list | Return information about a resource
update | Update a resource
delete | Delete a resource


## Topic index

### Entities ("Things")

#### <a name="entity_create"></a> Create a new entity
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/create/entity` | `{'lid': 'proxyentitya'}`

##### Response
`HTTP: 201`
```
{
    "t": 4,
    "p": {
        "epId": "28cf13bbacbf9a59d4fb300e1d6eff0f",
        "lid": "proxyentitya",
        "id": "58056ba7362d6ec2bdea7bc76ba8cfd3",
        "r": 1
    }
}
```

#### Rename <a name="entity_rename"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/update/entity/<lid>/rename` | `{'newlid': 'proxyentityb'}`

##### Response
`HTTP: 200`
```
{
    "t": 10,
    "p": {
        "lid": "proxyentityb",
        "id": "58056ba7362d6ec2bdea7bc76ba8cfd3",
        "r": 1,
        "oldLid": "proxyentitya"
    }
}
```

#### Reassign <a name="entity_reassign"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/update/entity/<lid>/reassign` |`{'epId': None}`

##### Response
`HTTP: 200`
```
{
    "t": 3,
    "p": {
        "m": "New epId same as existing",
        "c": 3
    }
}
```

#### Delete <a name="entity_delete"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/delete/entity/<lid>` |

##### Response
`HTTP: 204`


#### List <a name="entity_list"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/list/entity` |

##### Response
`HTTP: 200`
```
{
    "p": {
        "entities": {
            "proxyentityb": {
                "epId": "28cf13bbacbf9a59d4fb300e1d6eff0f",
                "id": "efb826df289f19ec8c47218a965e7b8e",
                "public": false
            }
        }
    },
    "t": 1
}
```

#### List ALL <a name="entity_list_all"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/list/entity/all` |

##### Response
`HTTP: 200`
```
{
    "t": 1,
    "p": {
        "entities": {
            "tims_energenie": {
                "epId": "b01f2cb576014239f053eff44a7ed4b4",
                "id": "df167e1c79250d9041cd80f943600542",
                "public": true
            },
            "proxyentityb": {
                "epId": "28cf13bbacbf9a59d4fb300e1d6eff0f",
                "id": "efb826df289f19ec8c47218a965e7b8e",
                "public": false
            }
        }
    }
}
```

#### List Metadata <a name="entity_meta_get"></a>
Lists the raw metadata - useful if you can deal with RDF/XML on the edge

URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/list/entity/<lid>/xml/meta` |

##### Response
`HTTP: 200`
```
{
    "t": 1,
    "p": {
        "id": "91dbf1dc572681d2fa3dad459f52bb73",
        "meta": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<rdf:RDF\n   xmlns:iotic=\"http://purl.org/net/iotic-labs#\"\n   xmlns:j.0=\"http://purl.org/dc/terms/\"\n   xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\"\n>\n  <rdf:Description rdf:about=\"urn:uuid:91dbf1dc-5726-81d2-fa3d-ad459f52bb73\">\n    <rdf:type rdf:resource=\"http://purl.org/net/iotic-labs#Entity\"/>\n    <iotic:ContainedIn rdf:resource=\"urn:uuid:f8fd93ed-7328-0432-3edc-3dc9f5202d0d\"/>\n    <j.0:created rdf:datatype=\"http://www.w3.org/2001/XMLSchema#datetime\">2016-05-11T09:45:21.230993</j.0:created>\n  </rdf:Description>\n</rdf:RDF>\n"
    }
}
```

#### Set Metadata <a name="entity_meta_set"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/update/entity/<lid>/xml/meta` | `{'meta': '<xml metadata>'}`

##### Response - Invalid here as malformed xml
`HTTP: 200`
```
{
    "t": 3,
    "p": {
        "m": "Invalid argument(s): RDF is badly formed",
        "c": 3
    }
}
```

#### Set Public/Private <a name="entity_setpublic"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/update/entity/<lid>/setpublic` | `{'public': True}`

##### Response
`HTTP: 200`
```
{
    "t": 1,
    "p": null
}
```


#### Add tags <a name="entity_tag_set"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/create/entity/<lid>/tag` | `{'tags': ['hello', 'fish'], 'lang': 'en'}`

##### Response
`HTTP: 200`
```
{
    "t": 1,
    "p": null
}
```

#### List tags <a name="entity_tag_list"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/list/entity/<lid>/tag` |

##### Response
`HTTP: 200`
```
{
    "t": 1,
    "p": {
        "tags": {
            "en": ["fish", "hello"]
        }
    }
}
```

#### Delete tags <a name="entity_tag_delete"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/delete/entity/<lid>/tag` | `{'tags': ['hello'], 'lang': 'en'}`

##### Response
`HTTP: 200`
```
{
    "t": 1,
    "p": null
}
```

### Points ("Feeds" and "Controls")

#### Create a feed on an entity <a name="point_create_feed"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/create/point/feed` | `{'pid': 'data', 'lid': 'proxyentitya'} `

##### Response
`HTTP: 201`
```
{
    "t": 4,
    "p": {
        "entityLid": "proxyentitya",
        "lid": "data",
        "id": "c3a6e6d34be7e20fa049d20042293c98",
        "r": 2
    }
}
```

#### Create a control on an entity <a name="point_create_control"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/create/point/control` | `{'pid': 'button', 'lid': 'proxyentitya'}`

##### Response
`HTTP: 201`
```
{
    "t": 4,
    "p": {
        "entityLid": "proxyentitya",
        "lid": "button",
        "id": "f0e16959c998e5d904fca26aeef4c9c9",
        "r": 3
    }
}
```

#### Share data from a feed <a name="point_share"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/create/point/<lid>/<pid>/share` | `{'what': 'ever', 'you': 'want'}`

##### Response
`HTTP: 200`
```
{
    "t": 1,
    "p": null
}
```


#### Add tags for a point <a name="point_tag_set"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/create/point/<foc>/<lid>/<pid>/tag` | `{'tags': ['goodbye', 'cats'], 'lang': 'en'}`

##### Response
`HTTP: 200`
```
{
    "t": 1,
    "p": null
}
```

#### List tags for a point <a name="point_tag_list"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/list/point/<foc>/<lid>/<pid>/tag` |

##### Response
`HTTP: 200`
```
{
    "t": 1,
    "p": {
        "tags": {
            "en": ["cats", "goodbye"]
        }
    }
}
```


#### Delete tags <a name="point_tag_delete"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/delete/point/<foc>/<lid>/<pid>/tag` | `{'tags': ['goodbye'], 'lang': 'en'}`

##### Response
`HTTP: 200`
```
{
    "t": 6,
    "p": null
}
```

### Values ("Values")

#### <a name="value_create"></a> Create a new value
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/create/value/<foc>/<lid>/<pid>` | `{'label': 'label', 'vtype': 'primitive', 'lang': 'en', 'comment': 'comment', 'unit': 'obo url'}`

##### Response
`HTTP: 201`
```
{
    "t": 1,
    "p": null
}
```

#### List <a name="value_list"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/list/value/<foc>/<lid>/<pid>` |

##### Response
`HTTP: 200`
```
{
    "t": 1,
    "p": {
        "values": [{
            "label": "col1",
            "type": "int",
            "lang": "en",
            "unit": null,
            "comment": null}]
    }
}
```

#### Delete a value <a name="value_delete"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/delete/value/<foc>/<lid>/<pid>/<label>/<lang>` |

##### Response
`HTTP: 204`


### Subscription ("Sub")

#### <a name="sub_create"></a> Create a new subscription
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/create/sub/<foc>/<lid>` | `{'gpid': 'guid of remote thing'}`

##### Response
`HTTP: 201`
```
{
    "t": 1,
    "p": {
    }
}
```

#### <a name="sub_create_local"></a> Create a new local subscription
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/create/sub/<foc>/<lid>/<pid>` | `{'slid': 'lid of local subscribing thing'}`

##### Response
`HTTP: 201`
```
{
    "t": 1,
    "p": {
    }
}
```

#### List <a name="sub_list"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/list/sub/<lid>` |

##### Response
`HTTP: 200`
```
{
    "t": 1,
    "p": {
    }
}
```

#### Delete a subscription <a name="sub_delete"></a>
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/delete/sub/<subid>` |

##### Response
`HTTP: 204`


### Search and Describe

#### <a name="search"></a> Search
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/create/search` | `{'text': 'search query'}`

##### Response
`HTTP: 201`
```
{
    "t": 1,
    "p": {"result": {
        "57b778f83aa8342b39ebec9bf4a6c161": {
            "matches": 10.796984,
            "long": null,
            "lat": null,
            "label": "Energenie 2",
            "points": {
                "55866459614100c03bc2585fd0c2abbd": {
                    "matches": 10.796984,
                    "label": "latest motion sensor values",
                    "type": "Feed"
                }
            }
        }}
    }
}
```

#### <a name="describe"></a> Describe a Thing or Point by GUID
URL | Command | Payload
---|---|---|---
`ioticlabs/req/<device>/<reqid>/create/describe` | `{'guid': 'guid'}`

##### Response
`HTTP: 201`
```
{
    "t": 1,
    "p": {
        "result": {
            "type": "Entity",
            "meta": {
                "tags": ["energenie", "energy", "fishytag", "monitor", "power", "usage"],
                "points": [{
                    "label": "Data feed",
                    "type": "Feed",
                    "guid": "1b6283afa5fd68ae25a1426af5619310"}],
                "comment": "Energenie monitor attached to home office power outlet (laptop, server, monitor, switch, UPS)",
                "label": "Tim's Energenie",
                "long": 0.387971,
                "lat": 52.526787
            }
        }
    }
}
```


### Unsolicited messages, feeddata, controlreq

`ioticlabs/feeddata/<feedid>` | payload
`ioticlabs/controlreq/<entityLid>/<pid>` | payload
