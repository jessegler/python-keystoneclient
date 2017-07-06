
# Copyright 2012 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock
import uuid

from keystoneclient import exceptions
from keystoneclient.tests.unit.v3 import utils
from keystoneclient.v3 import project_tags


class ProjectTagsTests(utils.ClientTestCase, utils.CrudTests):
    def setUp(self):
        super(ProjectTagsTests, self).setUp()
        self.key = 'project_tag'
        self.collection_key = 'project_tags'
        self.model = project_tags.ProjectTag
        self.manager = self.client.project_tags

    def new_ref(self, **kwargs):
        kwargs = super(ProjectTagsTests, self).new_ref(**kwargs)
        kwargs.setdefault('id', uuid.uuid4().hex)
        kwargs.setdefault('project_id', uuid.uuid4().hex)
        kwargs.setdefault('name', uuid.uuid4().hex)
        return kwargs

    def test_create_tag_on_project(self):
        project_id = uuid.uuid4().hex
        ref = self.new_ref()
        self.stub_url('PUT',
                      ['projects', project_id, self.collection_key, ref['id']],
                      status_code=204)

        self.manager.create(id=ref['id'], project_id=ref['project_id'], name=ref['name'])
        self.assertRaises(exceptions.ValidationError,
                          self.manager.delete,
                          project_tag=ref,
                          project=None)
