
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

import logging
from keystoneclient import exceptions
from keystoneclient.tests.unit.v3 import utils
from keystoneclient.v3 import project_tags


class ProjectTagsTests(utils.ClientTestCase, utils.CrudTests):
    def setUp(self):
        super(ProjectTagsTests, self).setUp()
        self.key = 'project_tag'
        self.collection_key = 'tags'
        self.model = project_tags.ProjectTag
        self.manager = self.client.project_tags

    def new_ref(self, **kwargs):
        kwargs = super(ProjectTagsTests, self).new_ref(**kwargs)
        kwargs.setdefault('tag_id', uuid.uuid4().hex)
        kwargs.setdefault('project_id', uuid.uuid4().hex)
        kwargs.setdefault('name', uuid.uuid4().hex)
        return kwargs

    def test_create(self):
        project_id = uuid.uuid4().hex
        ref = self.new_ref()
        body = {"tag" : {"tag_id" : ref['tag_id']}}
        url = self.stub_url('POST',
                      #['projects', project_id, self.collection_key, ref['tag_id']],
                      #base_url='/projects/%s/tags/%s' % (ref['project_id'], ref['tag_id']),
                      base_url=self.TEST_URL+'/projects/%s' % 'jess',
                      parts=['tags', ref['tag_id']],
                      json=body,
                      status_code=204)
        #self.assertTrue(False, msg= url)
        #self.assertRequestBodyIs <-- do this
        self.manager.create(tag_id=ref['tag_id'], project_id='jess',
                            name=ref['name'])
        self.assertRaises(exceptions.ValidationError,
                          self.manager.delete,
                          project_tag=ref,
                          project=None)
