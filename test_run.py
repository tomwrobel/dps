import os
from ocfl_interfaces.fedora import FedoraApi
from test_objects.create_objects import CreateObjects

container_id = "myparent2"

# create test metadata file
co = CreateObjects("./test_data")
md_file_path = co.create_metadata_file(container_id)

# create a container and add the file
fa = FedoraApi()

b = fa.create_container(container_id)
print(b)

d = fa.ocfl_object_path(container_id)
print(d)

info = fa.get_information(container_id)
print(info)

new_file = fa.post_file_with_filename(container_id, "./test_data/myparent8_data.json")
print(new_file)

new_file = fa.put_file_with_digest(container_id, "./test_data/myparent8_data.json")
print(new_file)

new_file = fa.post_file_with_digest(container_id, "./test_data/myparent8_data.json")
print(new_file)


# b = a.create_archival_group_container("myparent8")
# print(b)
