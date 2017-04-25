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

import warnings

from debtcollector import removals
from keystoneauth1 import plugin
from positional import positional
import six

from keystoneclient import _discover
from keystoneclient import exceptions
from keystoneclient.i18n import _
from keystoneclient import session as client_session
from keystoneclient.v2_0 import client as v2_client
from keystoneclient.v3 import client as v3_client


_CLIENT_VERSIONS = {2: v2_client.Client,
                    3: v3_client.Client}


# functions needed from the private file that can be made public

def normalize_version_number(version):
    """Turn a version representation into a tuple.

    Takes a string, tuple or float which represent version formats we can
    handle and converts them into a (major, minor) version tuple that we can
    actually use for discovery.

    e.g. 'v3.3' gives (3, 3)
         3.1 gives (3, 1)

    :param version: Inputted version number to try and convert.

    :returns: A usable version tuple
    :rtype: tuple

    :raises TypeError: if the inputted version cannot be converted to tuple.
    """
    return _discover.normalize_version_number(version)


def version_match(required, candidate):
    """Test that an available version satisfies the required version.

    To be suitable a version must be of the same major version as required
    and be at least a match in minor/patch level.

    eg. 3.3 is a match for a required 3.1 but 4.1 is not.

    :param tuple required: the version that must be met.
    :param tuple candidate: the version to test against required.

    :returns: True if candidate is suitable False otherwise.
    :rtype: bool
    """
    return _discover.version_match(required, candidate)


def available_versions(url, session=None, **kwargs):
    """Retrieve raw version data from a url."""
    if not session:
        session = client_session.Session._construct(kwargs)

    return _discover.get_version_data(session, url)


class Discover(_discover.Discover):
    """A means to discover and create clients.

    Clients are created depending on the supported API versions on the server.

    Querying the server is done on object creation and every subsequent method
    operates upon the data that was retrieved.

    The connection parameters associated with this method are the same format
    and name as those used by a client (see
    :py:class:`keystoneclient.v2_0.client.Client` and
    :py:class:`keystoneclient.v3.client.Client`). If not overridden in
    subsequent methods they will also be what is passed to the constructed
    client.

    In the event that auth_url and endpoint is provided then auth_url will be
    used in accordance with how the client operates.

    .. warning::

        Creating an instance of this class without using the session argument
        is deprecated as of the 1.7.0 release and may be removed in the 2.0.0
        release.

    :param session: A session object that will be used for communication.
                    Clients will also be constructed with this session.
    :type session: keystoneclient.session.Session
    :param string auth_url: Identity service endpoint for authorization.
                            (optional)
    :param string endpoint: A user-supplied endpoint URL for the identity
                            service. (optional)
    :param string original_ip: The original IP of the requesting user which
                               will be sent to identity service in a
                               'Forwarded' header. (optional) This is ignored
                               if a session is provided. Deprecated as of the
                               1.7.0 release and may be removed in the 2.0.0
                               release.
    :param boolean debug: Enables debug logging of all request and responses to
                          the identity service. default False (optional)
                          This is ignored if a session is provided. Deprecated
                          as of the 1.7.0 release and may be removed in the
                          2.0.0 release.
    :param string cacert: Path to the Privacy Enhanced Mail (PEM) file which
                          contains the trusted authority X.509 certificates
                          needed to established SSL connection with the
                          identity service. (optional) This is ignored if a
                          session is provided. Deprecated as of the 1.7.0
                          release and may be removed in the 2.0.0 release.
    :param string key: Path to the Privacy Enhanced Mail (PEM) file which
                       contains the unencrypted client private key needed to
                       established two-way SSL connection with the identity
                       service. (optional) This is ignored if a session is
                       provided. Deprecated as of the 1.7.0 release and may be
                       removed in the 2.0.0 release.
    :param string cert: Path to the Privacy Enhanced Mail (PEM) file which
                        contains the corresponding X.509 client certificate
                        needed to established two-way SSL connection with the
                        identity service. (optional) This is ignored if a
                        session is provided. Deprecated as of the 1.7.0 release
                        and may be removed in the 2.0.0 release.
    :param boolean insecure: Does not perform X.509 certificate validation when
                             establishing SSL connection with identity service.
                             default: False (optional) This is ignored if a
                             session is provided. Deprecated as of the 1.7.0
                             release and may be removed in the 2.0.0 release.
    :param bool authenticated: Should a token be used to perform the initial
                               discovery operations. default: None (attach a
                               token if an auth plugin is available).

    """

    @positional(2)
    def __init__(self, session=None, authenticated=None, **kwargs):
        if not session:
            warnings.warn(
                'Constructing a Discover instance without using a session is '
                'deprecated as of the 1.7.0 release and may be removed in the '
                '2.0.0 release.', DeprecationWarning)
            session = client_session.Session._construct(kwargs)
        kwargs['session'] = session

        url = None
        endpoint = kwargs.pop('endpoint', None)
        auth_url = kwargs.pop('auth_url', None)

        if endpoint:
            self._use_endpoint = True
            url = endpoint
        elif auth_url:
            self._use_endpoint = False
            url = auth_url
        elif session.auth:
            self._use_endpoint = False
            url = session.get_endpoint(interface=plugin.AUTH_INTERFACE)

        if not url:
            raise exceptions.DiscoveryFailure(
                _('Not enough information to determine URL. Provide'
                  ' either a Session, or auth_url or endpoint'))

        self._client_kwargs = kwargs
        super(Discover, self).__init__(session, url,
                                       authenticated=authenticated)

    @removals.remove(message='Use raw_version_data instead.', version='1.7.0',
                     removal_version='2.0.0')
    def available_versions(self, **kwargs):
        """Return a list of identity APIs available on the server.

        The list returned includes the data associated with them.

        .. warning::

            This method is deprecated as of the 1.7.0 release in favor of
            :meth:`raw_version_data` and may be removed in the 2.0.0 release.

        :param bool unstable: Accept endpoints not marked 'stable'. (optional)
                              Equates to setting allow_experimental
                              and allow_unknown to True.
        :param bool allow_experimental: Allow experimental version endpoints.
        :param bool allow_deprecated: Allow deprecated version endpoints.
        :param bool allow_unknown: Allow endpoints with an unrecognised status.

        :returns: A List of dictionaries as presented by the server. Each dict
                  will contain the version and the URL to use for the version.
                  It is a direct representation of the layout presented by the
                  identity API.
        """
        return self.raw_version_data(**kwargs)

    @removals.removed_kwarg(
        'unstable',
        message='Use allow_experimental and allow_unknown instead.',
        version='1.7.0', removal_version='2.0.0')
    def raw_version_data(self, unstable=False, **kwargs):
        """Get raw version information from URL.

        Raw data indicates that only minimal validation processing is performed
        on the data, so what is returned here will be the data in the same
        format it was received from the endpoint.

        :param bool unstable: equates to setting allow_experimental and
                              allow_unknown. This argument is deprecated as of
                              the 1.7.0 release and may be removed in the 2.0.0
                              release.
        :param bool allow_experimental: Allow experimental version endpoints.
        :param bool allow_deprecated: Allow deprecated version endpoints.
        :param bool allow_unknown: Allow endpoints with an unrecognised status.

        :returns: The endpoints returned from the server that match the
                  criteria.
        :rtype: List

        Example::

            >>> from keystoneclient import discover
            >>> disc = discover.Discovery(auth_url='http://localhost:5000')
            >>> disc.raw_version_data()
                [{'id': 'v3.0',
                    'links': [{'href': u'http://127.0.0.1:5000/v3/',
                               'rel': u'self'}],
                  'media-types': [
                      {'base': 'application/json',
                       'type': 'application/vnd.openstack.identity-v3+json'},
                      {'base': 'application/xml',
                       'type': 'application/vnd.openstack.identity-v3+xml'}],
                  'status': 'stable',
                  'updated': '2013-03-06T00:00:00Z'},
                 {'id': 'v2.0',
                  'links': [{'href': u'http://127.0.0.1:5000/v2.0/',
                             'rel': u'self'},
                            {'href': u'...',
                             'rel': u'describedby',
                             'type': u'application/pdf'}],
                  'media-types': [
                      {'base': 'application/json',
                       'type': 'application/vnd.openstack.identity-v2.0+json'},
                      {'base': 'application/xml',
                       'type': 'application/vnd.openstack.identity-v2.0+xml'}],
                  'status': 'stable',
                  'updated': '2013-03-06T00:00:00Z'}]
        """
        if unstable:
            kwargs.setdefault('allow_experimental', True)
            kwargs.setdefault('allow_unknown', True)

        return super(Discover, self).raw_version_data(**kwargs)

    def _calculate_version(self, version, unstable):
        version_data = None

        if version:
            version_data = self.data_for(version)
        else:
            # if no version specified pick the latest one
            all_versions = self.version_data(unstable=unstable)
            if all_versions:
                version_data = all_versions[-1]

        if not version_data:
            msg = _('Could not find a suitable endpoint')

            if version:
                msg = _('Could not find a suitable endpoint for client '
                        'version: %s') % str(version)

            raise exceptions.VersionNotAvailable(msg)

        return version_data

    def _create_client(self, version_data, **kwargs):
        # Get the client for the version requested that was returned
        try:
            client_class = _CLIENT_VERSIONS[version_data['version'][0]]
        except KeyError:
            version = '.'.join(str(v) for v in version_data['version'])
            msg = _('No client available for version: %s') % version
            raise exceptions.DiscoveryFailure(msg)

        # kwargs should take priority over stored kwargs.
        for k, v in six.iteritems(self._client_kwargs):
            kwargs.setdefault(k, v)

        # restore the url to either auth_url or endpoint depending on what
        # was initially given
        if self._use_endpoint:
            kwargs['auth_url'] = None
            kwargs['endpoint'] = version_data['url']
        else:
            kwargs['auth_url'] = version_data['url']
            kwargs['endpoint'] = None

        return client_class(**kwargs)

    def create_client(self, version=None, unstable=False, **kwargs):
        """Factory function to create a new identity service client.

        :param tuple version: The required version of the identity API. If
                              specified the client will be selected such that
                              the major version is equivalent and an endpoint
                              provides at least the specified minor version.
                              For example to specify the 3.1 API use (3, 1).
                              (optional)
        :param bool unstable: Accept endpoints not marked 'stable'. (optional)
        :param kwargs: Additional arguments will override those provided to
                       this object's constructor.

        :returns: An instantiated identity client object.

        :raises keystoneclient.exceptions.DiscoveryFailure: if the server
                                                            response is invalid
        :raises keystoneclient.exceptions.VersionNotAvailable: if a suitable
            client cannot be found.
        """
        version_data = self._calculate_version(version, unstable)
        return self._create_client(version_data, **kwargs)


def add_catalog_discover_hack(service_type, old, new):
    """Add a version removal rule for a particular service.

    Originally deployments of OpenStack would contain a versioned endpoint in
    the catalog for different services. E.g. an identity service might look
    like ``http://localhost:5000/v2.0``. This is a problem when we want to use
    a different version like v3.0 as there is no way to tell where it is
    located. We cannot simply change all service catalogs either so there must
    be a way to handle the older style of catalog.

    This function adds a rule for a given service type that if part of the URL
    matches a given regular expression in *old* then it will be replaced with
    the *new* value. This will replace all instances of old with new. It should
    therefore contain a regex anchor.

    For example the included rule states::

        add_catalog_version_hack('identity', re.compile('/v2.0/?$'), '/')

    so if the catalog retrieves an *identity* URL that ends with /v2.0 or
    /v2.0/ then it should replace it simply with / to fix the user's catalog.

    :param str service_type: The service type as defined in the catalog that
                             the rule will apply to.
    :param re.RegexObject old: The regular expression to search for and replace
                               if found.
    :param str new: The new string to replace the pattern with.
    """
    _discover._VERSION_HACKS.add_discover_hack(service_type, old, new)
