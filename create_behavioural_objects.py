from ocfl_interfaces.fedora.behavioural_objects import BehaviouralObjects
from pprint import pprint
import time

b = BehaviouralObjects()

start_time = time.time()
results = b.create_metadata_object()
pprint(results)
end_time = time.time()
print("--- %s seconds ---" % (end_time - start_time))

start_time = time.time()
results = b.create_binary_file_objects()
pprint(results)
end_time = time.time()
print("--- %s seconds ---" % (end_time - start_time))

start_time = time.time()
results = b.create_large_binary_file_objects()
pprint(results)
end_time = time.time()
print("--- %s seconds ---" % (end_time - start_time))

start_time = time.time()
results = b.create_complex_binary_file_objects()
pprint(results)
end_time = time.time()
print("--- %s seconds ---" % (end_time - start_time))