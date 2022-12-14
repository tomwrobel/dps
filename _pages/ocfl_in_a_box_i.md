# Fedora 6 and OCFL-in-a-box, part one

If you don't want to hear the why, and just want the how, then [skip to the technical stuff](#HowTo)

## Introduction 

Our bit of the Bodleian Libraries (Oxford University's main library service) aims to be at the forefront of Digital Preservation. Our Digital Microservices Project team has been working on building a set of microservices tools for the past 3 years. Part of this is the efficient, performant, and standardised preservation of digital content and metadata in a secure and open way. The Digital Preservation Service aims to provide a place for the long term storage of versioned digital objects and their metadata. 

We have selected [OCFL](https://ocfl.io/), the Oxford Common File Layer, as our format for versioned digital objects. Our aim - as the title suggests - is to deploy an application to get the objects into OCFL, and to manage them once in place. Ideally, this application would create 'vanilla' OCFL objects with no additional application behaviour preserved in the OCFL object.

This post is about how we set up, configured, and tested Fedora 6 as the application layer. At the time of writing, December 2022, there were no other applications with a REST API that would allow us to create and manage OCFL objects.

### What we're looking for

- reliability and stability
- performance within defined boundaries
- being able to create and update a valid and sensible OCFL object on disk, locatable from its identifier only
- shorter file paths are better (it helps rsync)
- the system should not create too many versions (versions should make sense, ideally)
- a system to protect objects against concurrent writes
- basic access restrictions (e.g. username/password) on a system level
- a stable, documented REST API that allows us to
  - to create and update OCFL objects 
  - to download binary files
  - access point in time versions of those objects
  - list point in time versions of those objects
  - manage and deploy the application as a decoupled service

### What we're not looking for

- We aren't looking to Fedora-ise our data. Beyond the API, we won't be making searches or queries of the data using Fedora.
- ACLs or access management beyond username/password
- We aren't looking for our object containers to have anything more than the ids and paths we want to create 
- We won't be using Fedora to store triples relating to these objects
- We won't be using Fedora for digital preservation apart from - ideally - validating ingest  

## Howto

#### Configuration

Running on Postgres 12 

fcrepo.session.timeout	has to be set insanely long for large files, at least 90 minutes (5,400,000 milliseconds, '5400000')

#### Use transactions

Fedora6 transactions are very useful. 

Firstly, Once a transaction is started and an object is altered within that transaction, the object locks to all subsequent POST, PUT, and DELETE operations, preventing concurrent overwrites.

Secondly, if you create a transaction, then all actions within that transaction will be put into the same OCFL version directory. This prevents the unnecessary creation of too many versions.

Finally, note that any single POST or PUT action not part of a transaction creates its own transaction. This prevents current overwrites of an object, as above. It also means that a POST or PUT that times out will return the result that a transaction has been rolled back. 


#### How to create an object

The type of Fedora6 object you need to create is called an 'Archival Group'. The children of normal F6 containers are treated as independent entities (e.g. binary resources or metadata containers), linked to them via metadata. They're stored in their own OCFL objects and in a different part of the storage root. This has performance advantages, as each child can be updated atomically. However, as the children wills be stored throughout the file system, this wouldn't be suitable for a DPS.

In an archival group, all child resources will be treated as part of the parent object, rather than as independent object children. An archival group keeps all child resources together on the file system. 

***Fedora6 quirk***: When creating an archival group, F6 will generate an OCFL object with the file `v1/content/fcr-container.nt`. For all external object behaviours, this file can be ignored. 

#####  Call you'll need to create an object with files

Assuming you want to create an object with id: `0184b503-6e45-46db-b8b8-7d599952c673`. And three files, all of which are available in the root of the directory you're running the `curl` from:

```
ora.ox.ac.uk:uuid:0184b503-6e45-46db-b8b8-7d599952c673.ora2.json
binary_0.bin
binary_1.bin
```

To create the files


```
## 1. Create a transaction (and store the ID)
curl -i -u ${AUTH} -X POST https://${MY_REPO}/rest/fcr:tx 

## 2. Make sequentiual POST calls to create the object and add the necessary files to the object

curl -X POST -u ${AUTH} -H "Atomic-ID:${TX_URI}" https://${MY_REPO}/rest/0184b503-6e45-46db-b8b8-7d599952c673

curl -X POST -u ${AUTH} --data-binary @ora.ox.ac.uk:uuid:0184b503-6e45-46db-b8b8-7d599952c673.ora2.json -H "Slug: ora.ox.ac.uk:uuid:0184b503-6e45-46db-b8b8-7d599952c673.ora2.json" -H "Atomic-ID:${TX_URI}" -H -"Content-Disposition: attachment; filename=\"ora.ox.ac.uk:uuid:0184b503-6e45-46db-b8b8-7d599952c673.ora2.json\"" https://${MY_REPO}/rest/0184b503-6e45-46db-b8b8-7d599952c673

curl -X POST -u ${AUTH} --data-binary @binary_0.bin -H "Slug: binary_0.bin" -H "Atomic-ID:${TX_URI}" -H -"Content-Disposition: attachment; filename=\"binary_0.bin\"" https://${MY_REPO}/rest/0184b503-6e45-46db-b8b8-7d599952c673

curl -X POST -u ${AUTH} --data-binary @binary_1.bin -H "Slug: binary_1.bin" -H "Atomic-ID:${TX_URI}" -H -"Content-Disposition: attachment; filename=\"binary_1.bin\"" https://${MY_REPO}/rest/0184b503-6e45-46db-b8b8-7d599952c673

### 3. Finish the transaction

curl -X PUT -u ${AUTH} ${TX_URI}

```

##### Object on disk after the call

```
/data/ocfl/ocfl-root/18f/8d1/c6e/18f8d1c6ed46fcc252c9874568d72d5d1209352b9310c57ec56e730e082c8a7f
├── 0=ocfl_object_1.1
├── inventory.json
├── inventory.json.sha512
└── v1
    ├── content
    │   ├── binary_0.bin
    │   ├── binary_1.bin
    │   ├── fcr-container.nt
    │   └── ora.ox.ac.uk:uuid:0184b503-6e45-46db-b8b8-7d599952c673.ora2.json
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
## 1. Create a transaction (and store the ID)
curl -i -u ${AUTH} -X POST https://${MY_REPO}/rest/fcr:tx 

## 2. Make sequentiual POST calls to add the necessary files to the object

curl -X POST -u ${AUTH} --data-binary @${FILE_PATH} -H "Slug: ${FILENAME}" -H "Atomic-ID:${TX_URI}" -H -"Content-Disposition: attachment; filename=\"${FILENAME}\"" https://${MY_REPO}/rest/${MY_ID}

curl -X POST -u ${AUTH} --data-binary @${FILE_PATH_2} -H "Slug: ${FILENAME_2}" -H "Atomic-ID:${TX_URI}" -H -"Content-Disposition: attachment; filename=\"${FILENAME_2}\"" https://${MY_REPO}/rest/${MY_ID}

### 3. Finish the transaction

curl -X PUT -u ${AUTH} ${TX_URI}
```

#### How to upload large files

Note for large files: we could start the upload. Wait for the reply, and keep alive during it. But we'd need to start a transaction first.

## Links

Fedora6 OCFL implementation notes: https://wiki.lyrasis.org/display/FEDORA6x/Fedora+OCFL+Object+Structure
