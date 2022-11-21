import os
import sys
import time
import http.client
import mimetypes
import rdflib
import hashlib
import base64


class FedoraApi:
    def __init__(self):
        self.host = "localhost"
        self.port = 8080
        self.base_url = "/fcrepo/rest"
        self.username = "fedoraAdmin"
        self.password = "fedoraAdmin"
        uspwd = f"{self.username}:{self.password}"
        b64 = base64.b64encode(uspwd.encode("ascii")).decode()
        self.auth = f"Basic {b64}"
        if not self.base_url.endswith("/"):
            self.base_url = self.base_url + "/"
        self.ocfl_root = "/data/ocfl-root"

    def myConnection(self, method="GET", url="", payload="", headers={}):
        headers["Authorization"] = self.auth
        conn = http.client.HTTPConnection(self.host, self.port)
        conn.request(method, url, payload, headers)
        res = conn.getresponse()
        conn.close()
        return res

    def get_original_link_location(self, res, key="Link"):
        location = ""
        if key == "Location":
            return res.getheader("Location")
        # Default to searching around the headers for the original Link
        for j in res.getheader("Link").split(","):
            if "original" in j:
                location = j.split(";")[0].strip()[1:-1]
        return location

    def create_container(self, container_id=None):
        if not container_id:
            myURL = self.base_url
        else:
            myURL = self.base_url + container_id
        res = self.myConnection(method="PUT", url=myURL, payload="", headers={})
        if res.status in [201, 204]:
            # Location header is returned for 201
            # The link header contains the url of the container in original
            location = self.get_original_link_location(res)
            # _container_id = location.replace(self.base_url, "")
            return location
        else:
            return False

    def create_archival_group_container(self, container_id=None):
        headers = {}
        headers["Link"] = '<http://fedora.info/definitions/v4/repository#ArchivalGroup>;rel="type"'
        if container_id:
            headers["Slug"] = container_id
        myURL = self.base_url + container_id
        res = self.myConnection(method="POST", url=myURL, payload="", headers=headers)

        if res.status in [201, 204]:
            location = self.get_original_link_location(res)
            return location
        else:
            return False

    def get_information(self, container_id=None):
        headers = {"Accept": "text/turtle"}
        myURL = self.base_url + container_id
        res = self.myConnection(method="POST", url=myURL, payload="", headers=headers)

        g = rdflib.Graph()
        g.parse(data=bytes(res.info()), format="turtle")
        attributes = {}
        for s, p, o in g.triples((None, None, None)):
            if "fedora.info" in p:
                prop = p.split("#")[-1]
                attributes[prop] = o.value
        return attributes

    def add_file(self, container_id, file_path, mime_type=None, digest=None):
        # curl -X PUT --upload-file image.jpg -H"Content-Type: image/jpeg"
        #      -H"digest: sha=cb1a576f22e8e3e110611b616e3e2f5ce9bdb941" "http://localhost:8080/rest/new/image"
        #
        # curl -i -u fedoraAdmin:fedoraAdmin -X POST --data-binary "@test_data/myparent8_data.json"
        #      -H "Content-Disposition: attachment; filename=\"myparent8_data.json\"" "http://localhost:8080/fcrepo/rest/myparent0"
        #
        # curl -i -u fedoraAdmin:fedoraAdmin -X POST --data-binary "@/home/nraja/Downloads/ce666-10Nov2022.png"
        #      -H "Content-Disposition: attachment; filename=\"ce666-10Nov2022.png\"" "http://localhost:8080/fcrepo/rest/myparent0"

        if not container_id:
            return False
        if not os.path.exists(file_path):
            return FileNotFoundError(file_path)
        if not mime_type:
            mime_type = self.get_mime_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"

        file_name = os.path.basename(file_path)
        headers = {}
        headers["Content-Disposition"] = f"attachment; filename={file_name}"
        headers["Content-Type"] = mime_type
        files = open(file_path, "rb").read()

        myURL = self.base_url + container_id + "/"
        res = self.myConnection(method="POST", url=myURL, payload=files, headers=headers)

        if res.status in [201, 204]:
            location = self.get_original_link_location(res, key="Location")
            return location
        else:
            return False

    def start_transaction(self):
        return

    def ocfl_object_path(self, container_id):
        container = f"info:fedora/{container_id}"
        csha = hashlib.sha256(container.encode("utf-8")).hexdigest()
        cpath = os.path.join(self.ocfl_root, csha[0:3], csha[3:6], csha[6:9], csha)
        return cpath

    def get_mime_type(self, file_path):
        if not os.path.exists(file_path):
            return FileNotFoundError(file_path)
        mt = mimetypes.guess_type(file_path)
        if mt:
            return mt[0]
        else:
            return None
