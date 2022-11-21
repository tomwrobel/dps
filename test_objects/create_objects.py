#!/usr/bin/python
import os


class CreateObjects:
    def __init__(self, test_data_dir):
        if not os.path.isdir(test_data_dir):
            raise NotADirectoryError
        self.test_data_dir = test_data_dir
        # ToDo - Should they always be written to disk or can they just be held in memory?

    def create_file(self, fileName, fileSize=0):
        # Create a file with given name and size (in bytes)
        if fileSize <= 0:
            return
        filePath = os.path.join(self.test_data_dir, fileName)
        # ToDo if the file with the same name and same size already exists, maybe just return that?
        if os.path.exists(filePath):
            fS = os.stat(filePath).st_size
            if fS == fileSize:
                return filePath
        with open(filePath, "wb") as f:
            f.write(os.urandom(fileSize))
        return filePath

    def create_metadata_file(self, uuid):
        # a single 2Kb metadata file
        fileName = f"{uuid}_metadata.json"  # ToDo - check this
        return self.create_file(fileName, 2 * 1024)

    def create_binary_file(self, fileName="binary.bin"):
        # 5Mb in size
        return self.create_file(fileName, 5 * 1024 * 1024)

    def create_complex_binary_file(self, fileName="complexBinary.bin"):
        # 500Mb in size
        return self.create_file(fileName, 500 * 1024 * 1024)

    def create_large_binary_file(self, fileName="largeBinary.bin"):
        # 1Gb in size
        # ToDo: How slow is the system in creating this file?
        return self.create_file(fileName, 1 * 1024 * 1024 * 1024)

    def create_very_large_binary_file(self, fileName="complexBinary.bin"):
        # 256Gb in size
        # ToDo: How slow is the system in creating this file?
        return self.create_file(fileName, 256 * 1024 * 1024 * 1024)

    def cleanup(self):
        # ToDo
        return
