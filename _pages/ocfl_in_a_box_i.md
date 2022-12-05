# OCFL in a Box, part one

If you don't want to hear the why, and just want the how, then [skip to the technical stuff](#HowTo)

## Introduction 

Our bit of the Bodleian Libraries (Oxford University's main library service) aims to be at the forefront of Digital Preservation. Our Digital Microservices Project team has been working on building a set of microservices tools for the past 3 years. Part of this is the efficient, performant, and standardised preservation of digital content and metadata in a secure and open way. The Digital Preservation Service aims to provide a place for the long term storage of versioned digital objects and their metadata....

### What we're looking for

- reliable
- create an valid and sensible OCFL version on disk
- not too many file paths
- not too many versions (versions should make sense, ideally)

### What we're not looking for

We aren't looking to Fedora-ise our data. We aren't looking for our object containers to have anything more than the ids and paths we want to create. We won't be using Fedora to store triples relating to these objects.


## Howto

#### Configuration

Running on Postgres 12 

fcrepo.session.timeout	has to be set insanely long for large files, at least 90 minutes (5,400,000 milliseconds, '5400000')

#### How to create an object

The type of Fedora6 object you need to create is called an 'Archival Group'. The children of normal F6 containers are treated as independent entities (e.g. binary resources or metadata containers), linked to them via metadata. They're stored in their own OCFL objects and in a different part of the storage root. This has performance advantages, as each child can be updated atomically. However, as the children wills be stored throughout the file system, this wouldn't be suitable for a DPS.

In an archival group, all child resources will be treated as part of the parent object, rather than as independent object children. An archival group keeps all child resources together on the file system. 

***Fedora6 quirk***: When creating an archival group, F6 will generate an OCFL object with the file `v1/content/fcr-container.nt` and no other content. For all external object behaviours, the contents of the `v1/` version can be ignored. It creates this version, or revision, regardless of further calls. It also means that you don't NEED to wrap the object creation call within a transaction if you don't want or need to, as this version will be created regardless (you can't avoid unnecessary versions). See also [F6 transactions, timeouts, and other behaviours](#transactions)

#####  Call you'll need to create an object

```
curl -X POST -u ${AUTH} -H "Slug: ${MY_ID}" -H "Link: <http://fedora.info/definitions/v4/repository#ArchivalGroup>;rel=\"type\"" https://${MY_REPO}/rest
```

##### Object on disk after the call

```
/data/ocfl/ocfl-root/b96/a59/fa0/b96a59fa0559f5e232d5a787322fdd8337053863f37b3d3bc6fced71c690f6d0
├── 0=ocfl_object_1.1
├── inventory.json
├── inventory.json.sha512
└── v1
    ├── content
    │   └── fcr-container.nt
    ├── inventory.json
    └── inventory.json.sha512

```

#### How to add versions to an object sensibly

You can, if you like, use the OCFL mutable head extension developed and proposed by Fedora6 (see the [OCFL Spec Extension 0005-mutable-head](https://ocfl.github.io/extensions/0005-mutable-head.html). However, we found this offered no noticeable benefits over transactions, and the downside that each separate call went into a separate revision directory, thereby increasing path depth. It's possible that mutable head would be useful for VERY large changes to objects that took place over serveral days, but we found that switching off mutable head beheviour didn't affect performance, and led to a less complex object structure.

There are three steps to creating a new version

1. Create transaction
2. Make sequential POST calls to add the necessary files to the object
3. Finish the transaction

```
## 1. Get the transaction ID
curl -i -u ${AUTH} -X POST https://${MY_REPO}/rest/fcr:tx 

## 2. Make sequentiual POST calls to add the necessary files to the object

curl -X POST -u ${AUTH} --data-binary @${FILE_PATH} -H "Slug: ${FILENAME}" -H "Atomic-ID:${TX_URI}" -H -"Content-Disposition: attachment; filename=\"${FILENAME}\"" https://${MY_REPO}/rest/${MY_ID}

curl -X POST -u ${AUTH} --data-binary @${FILE_PATH_2} -H "Slug: ${FILENAME_2}" -H "Atomic-ID:${TX_URI}" -H -"Content-Disposition: attachment; filename=\"${FILENAME_2}\"" https://${MY_REPO}/rest/${MY_ID}

### 3. Finish the transaction

curl -X PUT -u ${AUTH} ${TX_URI}
```

#### How to upload large files

#### Transactions

If you create a transaction explicitly, you control the version

But you get a transaction any time

## Links

Fedora6 OCFL implementation notes: https://wiki.lyrasis.org/display/FEDORA6x/Fedora+OCFL+Object+Structure
