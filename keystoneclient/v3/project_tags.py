# Copyright 2011 OpenStack Foundation
# Copyright 2011 Nebula, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from positional import positional

from keystoneclient import base


class ProjectTag(base.Resource):
    """Represents an Identity project.

    Attributes:
        * tag_id: a uuid that identifies the tag
        * project_id: a uuid of the project the tag is attached to
        * name: project tag name

    """

    pass


class ProjectTagManager(base.CrudManager):
    """Manager class for manipulating Identity projects."""

    resource_class = ProjectTag
    collection_key = 'tags'
    key = 'tag'

    @positional(enforcement=positional.WARN)
    # TODO: Do we want to take a project or a project id here?
    def create(self, project_id, name=None, **kwargs):
        """Create a project tag."""
        return super(ProjectTagManager, self).create(
            project_id=project_id,
            name=name,
            base_url = '/projects/%s' % project_id,
            **kwargs)

    @positional(enforcement=positional.WARN)
    def list(self, project, **kwargs):
        """List project tags."""
        base_url = '/projects/%s' % base.getid(project)
        return super(ProjectTagManager, self).list(
            base_url=base_url,
            **kwargs)

    def check_in_project(self, project, project_tag):
        """Check if the project_tag is a member of the specified project."""
        #TODO improve doc string returns __ if project tag is in project, otherwise __
        #TODO needs unit test
        # TODO do we need this?
        base_url = '/projects/%s' % base.getid(project)
        return super(ProjectTagManager, self).head(
            base_url=base_url,
            user_id=base.getid(project))

    def update(self, project_id, tag_id, name=None, **kwargs):
        base_url = '/projects/%s' % project_id
        return super(ProjectTagManager, self).update(
            # TODO remove tag_id, mandatory name
            tag_id=base.getid(project_tag),
            project_id=project_id,
            name=name,
            base_url=base_url,
            **kwargs)

    def modify_list(self, project, project_tags):
        """Modify project tag list on a project."""
        #TODO needs unit test
        self.delete_all_tags(project)
        for project_tag in project_tags:
            self.create(
                tag_id=project_tag.tag_id,
                project_id=project_tag.project_id,
                name=project_tag.name)

    def delete(self, project_id, tag_id):
        """Delete a project tag from a project."""
        return super(ProjectTagManager, self).delete(
            project_id=project_id,
            tag_id=tag_id,
            base_url='/projects/%s' % project_id)

    def delete_all_tags(self, project):
        """Delete all project tags from a project."""
        for project_tag in self.list(project):
            self.delete(project, project_tag)

    # TODO needs tag search
