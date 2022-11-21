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
        res = self.myConnection(method="GET", url=myURL, payload="", headers=headers)
        attributes = {}
        body = res.read().decode()
        if body:
            g = rdflib.Graph()
            g.parse(data=body, format="turtle")
            for s, p, o in g.triples((None, None, None)):
                if "fedora.info" in p:
                    prop = p.split("#")[-1]
                    attributes[prop] = o.value
        return attributes

    def create_new_version(self, container_id):
        # curl -i -u fedoraAdmin:fedoraAdmin -X POST http://localhost:8080/fcrepo/rest/myparent0/fcr:versions
        if not container_id:
            return False
        headers = {}
        myURL = self.base_url + container_id + "/fcr:versions"
        res = self.myConnection(method="POST", url=myURL, payload="", headers=headers)
        if res.status in [201, 204]:
            location = self.get_original_link_location(res, key="Location")
            return location
        else:
            print(res.status)
            print(res.info())
            print(res.msg())
            return False


    def post_file_with_filename(self, container_id, file_path, mime_type=None):
        # curl -i -u fedoraAdmin:fedoraAdmin -X POST --data-binary "@picture.jpg" -H "Content-Disposition: attachment; filename=\"picture.jpg\"" "http://localhost:8080/rest/parent"
        # curl -i -u fedoraAdmin:fedoraAdmin -X POST --data-binary "@./test_data/myparent8_data.json" -H "Content-Disposition: attachment; filename=\"myparent8_data.json\"" "http://localhost:8080/fcrepo/rest/myparent0"
        # In python we have to add mime_type header. Otherwise it returns a 400 error.

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

    def post_file_with_digest(self, container_id, file_path, mime_type=None, digest={}):
        # curl -i -u fedoraAdmin:fedoraAdmin -X POST --data-binary "@picture.jpg"
        #      -H"digest: sha=cb1a576f22e8e3e110611b616e3e2f5ce9bdb941" "http://localhost:8080/rest/parent"
        # In python we have to add mime_type header. Otherwise it returns a 400 error.

        return self.add_file_with_digest("POST", container_id, file_path, mime_type=mime_type, digest=digest)

    def put_file_with_digest(self, container_id, file_path, mime_type=None, digest={}):
        # curl -X PUT --upload-file image.jpg -H"Content-Type: image/jpeg"
        #      -H"digest: sha=cb1a576f22e8e3e110611b616e3e2f5ce9bdb941" "http://localhost:8080/rest/new/image"
        file_name = os.path.basename(file_path)
        file_location = container_id + "/" + file_name
        return self.add_file_with_digest("PUT", file_location, file_path, mime_type=mime_type, digest=digest)

    def add_file_with_digest(self, method, container_id, file_path, mime_type=None, digest={}):
        # curl -X PUT --upload-file image.jpg -H"Content-Type: image/jpeg"
        #      -H"digest: sha=cb1a576f22e8e3e110611b616e3e2f5ce9bdb941" "http://localhost:8080/rest/new/image"

        print("Arguments are ....", method, container_id, file_path, mime_type, digest)

        if method not in ["PUT", "POST"]:
            method = "POST"

        if not container_id:
            return False
        if not os.path.exists(file_path):
            return FileNotFoundError(file_path)
        if not mime_type:
            mime_type = self.get_mime_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"

        headers = {}
        # headers["Content-Disposition"] = f"attachment; filename={file_name}"
        headers["Content-Type"] = mime_type
        files = open(file_path, "rb").read()
        if digest.get('sha1', None):
            headers['digest'] = f"sha={digest['sha1']}"
        elif digest.get('sha256', None):
            headers['digest'] = f"sha-256={digest['sha256']}"
        elif digest.get('sha512', None):
            headers['digest'] = f"sha-512={digest['sha512']}"
        else:
            print("No digest given. Evaluating ...")
            digest['sha1'] = hashlib.sha1(files).hexdigest()
            print(headers)
            headers['digest'] = f"sha={digest['sha1']}"
            print(headers)
        myURL = self.base_url + container_id
        res = self.myConnection(method=method, url=myURL, payload=files, headers=headers)

        if res.status in [201, 204]:
            location = self.get_original_link_location(res, key="Location")
            return location
        else:
            print(headers)
            print("URL sent over : ", myURL)
            print("File path ...: ", file_path)
            print(res.status)
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
