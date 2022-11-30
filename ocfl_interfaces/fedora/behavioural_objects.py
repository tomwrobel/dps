import os.path
import uuid
import time
import subprocess
from .fedora_api import FedoraApi
from test_objects.create_objects import CreateObjects


class BehaviouralObjects:
    def __init__(self, test_data_dir='./test_data'):
        self.final_result = None
        self.fa = FedoraApi()
        self.test_data_dir = test_data_dir
        self.co = CreateObjects(self.test_data_dir)
        return

    def create_metadata_object(self):
        # Metadata only objects: a single 2Kb metadata file
        container_id = str(uuid.uuid4())
        metadata_file_name = f"ora.ox.ac.uk:uuid:{container_id}.ora2.json"
        files = {
            metadata_file_name: 'metadata'
        }
        # create object in fedora
        return self._create_object(container_id, files)

    def create_binary_file_objects(self):
        # 2 binary files 5Mb in size and a single metadata file 2Kb in size
        container_id = str(uuid.uuid4())
        # create files
        metadata_file_name = f"ora.ox.ac.uk:uuid:{container_id}.ora2.json"
        files = {
            metadata_file_name: 'metadata'
        }
        for i in range(2):
            file_name = f"binary_{i}.bin"
            files[file_name] = 'binary'
        return self._create_object(container_id, files)

    def create_large_binary_file_objects(self):
        # 5 binary files 1Gb in size and a single metadata file 2Kb in size
        container_id = str(uuid.uuid4())
        # create files
        metadata_file_name = f"ora.ox.ac.uk:uuid:{container_id}.ora2.json"
        files = {
            metadata_file_name: 'metadata'
        }
        for i in range(5):
            file_name = f"large_binary_{i}.bin"
            files[file_name] = 'large_binary'
        return self._create_object(container_id, files)

    def create_complex_binary_file_objects(self):
        # 100 binary files 500Mb in size and a single metadata file 2Kb in size
        number_of_files = 10
        container_id = str(uuid.uuid4())
        # create files
        metadata_file_name = f"ora.ox.ac.uk:uuid:{container_id}.ora2.json"
        files = {
            metadata_file_name: 'metadata'
        }
        for i in range(number_of_files):
            file_name = f"complex_binary_{i}.bin"
            files[file_name] = 'complex_binary'
        return self._create_object(container_id, files)

    def _create_object(self, container_id, files):
        final_result = {'status': True, 'msg': []}
        # Start transaction
        result = self.fa.create_transaction()
        final_result = self._collate_results('Start transaction', final_result, result)
        if not final_result['status']:
            return final_result
        atomic_id = result.get('location', None)
        # keep transaction alive
        proc = self._start_keep_alive_subprocess(atomic_id)
        # create a container
        result = self.fa.create_container(container_id=container_id, archival_group=True, atomic_id=atomic_id)
        result['ocfl_path'] = self.fa.get_ocfl_object_path(container_id)
        final_result = self._collate_results('Create a container', final_result, result)
        # add files
        for file_location in files:
            print(".", end="")
            file_path = self._create_file(files[file_location])
            with open(file_path, 'a') as f:
                f.write(f"\n{time.time()}")
            result = self.fa.post_file(container_id, file_path, file_location=file_location,
                                       atomic_id=atomic_id)
            final_result = self._collate_results(f"Add file {file_location}", final_result, result)
        # commit the transaction
        print(f"Committing transaction {atomic_id}")
        result = self.fa.commit_transaction(atomic_id)
        final_result = self._collate_results("Commit transaction", final_result, result)
        print("Terminating the keep alive process")
        proc.kill()
        return final_result

    def _collate_results(self, action, final_result, result):
        result['action'] = action
        if not result['status']:
            final_result['status'] = False
        final_result['msg'].append(result)
        return final_result

    def _create_file(self, file_type):
        if file_type == 'metadata':
            return self.co.create_metadata_file()
        elif file_type == 'binary':
            return self.co.create_binary_file()
        elif file_type == 'large_binary':
            return self.co.create_large_binary_file()
        elif file_type == 'complex_binary':
            return self.co.create_complex_binary_file()
        elif file_type == 'very_large_binary':
            return self.co.create_very_large_binary_file()

    def _start_keep_alive_subprocess(self, atomic_id):
        cmd = ["python", "./ocfl_interfaces/fedora/keep_alive.py", atomic_id]
        proc = subprocess.Popen(cmd, shell=False, close_fds=True )# stdin=None, stdout=None, stderr=None, close_fds=True)
        return proc

