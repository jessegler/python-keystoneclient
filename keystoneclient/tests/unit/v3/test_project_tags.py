
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
from keystoneclient.v3 import projects


class ProjectTagsTests(utils.ClientTestCase, utils.CrudTests):
    def setUp(self):
        super(ProjectTagsTests, self).setUp()
        self.key = 'project_tag'
        self.collection_key = 'tags'
        self.model = project_tags.ProjectTag
        self.manager = self.client.project_tags

    def new_ref(self, **kwargs):
        kwargs = super(ProjectTagsTests, self).new_ref(**kwargs)
        kwargs.setdefault('project_id', uuid.uuid4().hex)
        kwargs.setdefault('tag_id', uuid.uuid4().hex)
        kwargs.setdefault('name', uuid.uuid4().hex)
        return kwargs

    def _tag_create(self, project_id=None, name=None):
        project_tag = project_tags.ProjectTag
        if project_id is None:
            project_id = uuid.uuid4().hex
        if name is None:
            name = uuid.uuid4().hex
        project_tag.project_id = project_id
        project_tag.name = name
        return project_tag

    def test_create_tag(self):
        ref = self.new_ref()
        request = {'tag': {'project_id': ref['project_id'], 'name': ref['name']}}
        body = {'tag': {'tag_id': ref['tag_id']}}
        self.stub_url('POST',
                      base_url=self.TEST_URL+'/projects/%s' % ref['project_id'],
                      parts=[self.collection_key],
                      json=body,
                      status_code=204)

        self.manager.create(project_id=ref['project_id'], name=ref['name'])
        self.assertRequestBodyIs(json=request)

    def test_delete_tag(self):
        ref = self.new_ref()
        request = {'tag': {'project_id': ref['project_id'], 'tag_id': ref['tag_id']}}
        body = {'tag': {'tag_id': ref['tag_id']}}
        self.stub_url('DELETE',
                      base_url=self.TEST_URL + '/projects/%s' % ref['project_id'],
                      parts=[self.collection_key, ref['tag_id']],
                      # TODO(jess): no body?
                      json=body,
                      # TODO(jess): spec says 204
                      status_code=200)

        self.manager.delete(project_id=ref['project_id'], tag_id=ref['tag_id'])

    def test_update_tag(self):
        ref = self.new_ref()
        body = {"tag": {"tag_id": ref['tag_id']}}
        self.stub_url('PATCH',
                      base_url=self.TEST_URL + '/projects/%s' % 'jess',
                      parts=['tags', ref['tag_id']],
                      json=body,
                      status_code=204)
        self.manager.update(project_id='jess', tag_id=ref['tag_id'],
                            name=ref['name'])

    def test_list(self):
        ref = self.new_ref()
        project = projects.Project
        project.id = ref['project_id']
        body = ['blue', 'red', 'green']

        self.stub_url('GET',
                      base_url=self.TEST_URL + '/projects/%s' % project.id,
                      parts=['tags'],
                      body=body,
                      status_code=200)

        self.manager.list(project=project)
