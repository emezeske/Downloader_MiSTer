# Copyright (c) 2021 José Manuel Barroso Galindo <theypsilon@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# You can download the latest version of this tool from:
# https://github.com/MiSTer-devel/Downloader_MiSTer
from typing import List
import pathlib

from downloader.constants import file_MiSTer
from downloader.file_system import FileSystem as ProductionFileSystem
from test.objects import file_a, file_a_descr, file_mister_descr, hash_MiSTer_old, file_test_json_zip, \
    file_test_json_zip_descr
from test.fake_logger import NoLogger

fake_temp_file = '/tmp/temp_file'


class TestDataFileSystem:
    def __init__(self, files, folders):
        self._files = files
        self._folders = folders

    def with_file(self, file, description):
        self._files.add(file, description)
        return self

    def with_folders(self, folders):
        for f in folders:
            self._folders.add(f, True)
        return self

    def with_file_a(self, description=None):
        self._files.add(file_a, description if description is not None else file_a_descr())
        return self

    def with_mister_binary(self, description=None):
        self._files.add(file_MiSTer, description if description is not None else file_mister_descr())

    def with_old_mister_binary(self):
        self.with_mister_binary({'hash': hash_MiSTer_old})

    def with_test_json_zip(self, description=None):
        self._files.add(file_test_json_zip, description if description is not None else file_test_json_zip_descr())
        return self


def make_production_filesystem(config) -> ProductionFileSystem:
    return ProductionFileSystem(config, NoLogger())


class FileSystem(ProductionFileSystem):
    def __init__(self):
        self._files = CaseInsensitiveDict()
        self._folders = CaseInsensitiveDict()
        self._system_paths = list()

    @property
    def test_data(self) -> TestDataFileSystem:
        return TestDataFileSystem(self._files, self._folders)

    @property
    def system_paths(self) -> List[str]:
        return self._system_paths.copy()

    def add_system_path(self, path):
        self._system_paths.append(path)

    def resolve(self, path):
        return path

    def temp_file(self):
        return fake_temp_file

    def is_file(self, path):
        return self._files.has(path)

    def is_folder(self, path):
        return True

    def read_file_contents(self, path):
        if not self._files.has(path):
            return 'unknown'
        return self._files.get(path)['content']

    def write_file_contents(self, path, content):
        if not self._files.has(path):
            self._files.add(path, {})
        self._files.get(path)['content'] = content

    def touch(self, path):
        self._files.add(path, {'hash': path})

    def move(self, source, target):
        self._files.add(target, {'hash': target})
        self._files.pop(source)

    def copy(self, source, target):
        self._files.add(target, self._files.get(source))

    def hash(self, path):
        return self._files.get(path)['hash']

    def make_dirs(self, path):
        self._folders.add(path, True)

    def make_dirs_parent(self, path):
        self._folders.add(str(pathlib.Path(path).parent), True)

    def folder_has_items(self, _path):
        return False

    def folders(self):
        return list(sorted(self._folders.keys()))

    def remove_folder(self, path):
        self._folders.pop(path)

    def download_target_path(self, path):
        return path

    def unlink(self, path):
        if self._files.has(path):
            self._files.pop(path)

    def delete_previous(self, file):
        pass

    def save_json_on_zip(self, db, path):
        pass

    def load_dict_from_file(self, path, suffix=None):
        file_description = self._files.get(path)
        unzipped_json = file_description['unzipped_json']
        file_description.pop('unzipped_json')
        return unzipped_json

    def unzip_contents(self, file, target):
        file_description = self._files.get(file)
        for path, description in file_description['zipped_files'].items():
            self._files.add(path, {'hash': description['hash']})
        file_description.pop('zipped_files')


class CaseInsensitiveDict:
    def __init__(self):
        self._dict = dict()

    def add(self, key, value):
        self._dict[key.lower()] = value

    def get(self, key):
        return self._dict[key.lower()]

    def has(self, key):
        return key.lower() in self._dict

    def pop(self, key):
        self._dict.pop(key.lower())

    def keys(self):
        return self._dict.keys()
