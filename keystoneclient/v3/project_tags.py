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
        * id: a uuid that identifies the project
        * project_id: a uuid of the project the tag is attached to
        * name: project tag name

    """

    pass


class ProjectTagManager(base.CrudManager):
    """Manager class for manipulating Identity projects."""

    resource_class = ProjectTag
    collection_key = 'project_tags'
    key = 'project_tag'

    @positional(enforcement=positional.WARN)
    def create(self, id, project_id=None, name=None, **kwargs):
        """Create a project tag."""
        return super(ProjectTagManager, self).create(
            id=id,
            project_id=project_id,
            name=name,
            **kwargs)

    @positional(enforcement=positional.WARN)
    def list(self, project=None, **kwargs):
        """List project tags."""
        base_url = '/projects/%s' % base.getid(project) if project else None
        return super(ProjectTagManager, self).list(
            base_url=base_url,
            **kwargs)

    def get(self, project_tag):
        return super(ProjectTagManager, self).get(
            project_tag_id=base.getid(project_tag))

    def check_in_project(self, project, project_tag):
        """Check if the project_tag is a member of the specified project."""
        base_url = '/projects/%s' % base.getid(project)
        return super(ProjectTagManager, self).head(
            base_url=base_url,
            user_id=base.getid(project))

    def update(self, project_tag, project_id=None, name=None, **kwargs):
        return super(ProjectTagManager, self).update(
            id=id,
            project_id=project_id,
            name=name,
            **kwargs)

    def modify_list(self, project, project_tags):
        """Modify project tag list on a project."""
        self.delete_all_tags(project)
        for project_tag in project_tags:
            self.create(
                id=project_tag.id,
                project_id=project_tag.project_id,
                name=project_tag.name)

    def delete(self, project_tag, project=None):
        """Delete a project tag from a project."""
        return super(ProjectTagManager, self).delete(
            user_id=base.getid(project_tag))

    def delete_all_tags(self, project):
        """Delete all project tags from a project."""
        for project_tag in self.list(project):
            self.delete(project, project_tag)
