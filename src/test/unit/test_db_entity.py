# Copyright (c) 2021-2022 José Manuel Barroso Galindo <theypsilon@gmail.com>

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

import unittest

from downloader.config import default_config
from downloader.constants import K_BASE_PATH
from downloader.db_entity import DbEntityValidationException, zip_mandatory_fields
from test.fake_db_entity import DbEntity
from test.objects import raw_db_empty_descr, db_empty
from zip_objects import zipped_nes_palettes_id, zipped_nes_palettes_desc


class TestDbEntity(unittest.TestCase):

    def test_construct_db_entity___with_correct_props___returns_db(self):
        self.assertIsNotNone(DbEntity(raw_db_empty_descr(), db_empty))

    def test_construct_db_entity___with_wrong_section___raises_db_entity_validation_exception(self):
        self.assertRaises(DbEntityValidationException, lambda: DbEntity(raw_db_empty_descr(), 'different section'))

    def test_construct_db_entity___with_wrong_db___raises_db_entity_validation_exception(self):
        self.assertRaises(DbEntityValidationException, lambda: DbEntity("wrong", db_empty))

    def test_construct_db_entity___with_none_db___raises_db_entity_validation_exception(self):
        self.assertRaises(DbEntityValidationException, lambda: DbEntity(None, db_empty))

    def test_construct_db_entity___with_correct_props_but_uppercase_db_id___returns_db_with_lowercase_id(self):
        raw_db = {'db_id': 'BiG', 'files': {}, 'folders': {}, 'timestamp': 0}
        expected = {'db_id': 'big', 'base_files_url': '', 'db_files': [], 'files': {}, 'folders': {}, 'zips': {}, 'default_options': {}, 'timestamp': 0}

        self.assertEqual(DbEntity(expected, 'big').testable, DbEntity(raw_db, 'bIg').testable)

    def test_construct_db_entity___with_wrong_field___raises_db_entity_validation_exception(self):
        for field in ['db_id', 'files', 'folders', 'timestamp']:
            with self.subTest(field):
                raw_db = raw_db_empty_descr()
                raw_db.pop(field)
                self.assertRaises(DbEntityValidationException, lambda: DbEntity(raw_db, db_empty))

    def test_construct_db_entity___with_wrong_zip_property___raises_db_entity_validation_exception(self):
        raw_db = raw_db_empty_descr()
        raw_db['zips'] = []
        self.assertRaises(DbEntityValidationException, lambda: DbEntity(raw_db, db_empty))

    def test_construct_db_entity___with_wrong_zip_field___raises_db_entity_validation_exception(self):
        for field in zip_mandatory_fields():
            with self.subTest(field):
                raw_db = raw_db_empty_descr()
                raw_db['zips'] = {zipped_nes_palettes_id: zipped_nes_palettes_desc()}
                raw_db['zips'][zipped_nes_palettes_id].pop(field)
                self.assertRaises(DbEntityValidationException, lambda: DbEntity(raw_db, db_empty))

    def test_construct_db_entity___with_wrong_zip_because_no_summary___raises_db_entity_validation_exception(self):
        raw_db = raw_db_empty_descr()
        raw_db['zips'] = {zipped_nes_palettes_id: zipped_nes_palettes_desc()}
        raw_db['zips'][zipped_nes_palettes_id].pop('summary_file')
        self.assertRaises(DbEntityValidationException, lambda: DbEntity(raw_db, db_empty))

    def test_construct_db_entity___with_wrong_zip_kind___raises_db_entity_validation_exception(self):
        for wrong_field in ['', None, 'wrong']:
            with self.subTest(wrong_field):
                raw_db = raw_db_empty_descr()
                raw_db['zips'] = {zipped_nes_palettes_id: zipped_nes_palettes_desc()}
                raw_db['zips'][zipped_nes_palettes_id]['kind'] = wrong_field
                self.assertRaises(DbEntityValidationException, lambda: DbEntity(raw_db, db_empty))

    def test_construct_db_entity___with_zip_kind_extract_all_contents_but_no_target_folder_path___raises_db_entity_validation_exception(self):
        raw_db = raw_db_empty_descr()
        raw_db['zips'] = {zipped_nes_palettes_id: zipped_nes_palettes_desc()}
        raw_db['zips'][zipped_nes_palettes_id].pop('target_folder_path')
        self.assertRaises(DbEntityValidationException, lambda: DbEntity(raw_db, db_empty))

    def test_construct_db_entity___with_wrong_options___raises_db_entity_validation_exception(self):
        raw_db = raw_db_empty_descr()
        raw_db['default_options'] = {K_BASE_PATH: default_config()[K_BASE_PATH]}
        self.assertRaises(DbEntityValidationException, lambda: DbEntity(raw_db, db_empty))
