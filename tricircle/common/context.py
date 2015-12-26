# Copyright 2015 Huawei Technologies Co., Ltd.
# All Rights Reserved
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

from pecan import request

import oslo_context.context as oslo_ctx

from tricircle.db import core


def get_db_context():
    return Context()


def get_admin_context():
    ctx = Context()
    ctx.is_admin = True
    return ctx


def is_admin_context(ctx):
    return ctx.is_admin


def extract_context_from_environ():
    context_paras = {'auth_token': 'HTTP_X_AUTH_TOKEN',
                     'user': 'HTTP_X_USER_ID',
                     'tenant': 'HTTP_X_TENANT_ID',
                     'user_name': 'HTTP_X_USER_NAME',
                     'tenant_name': 'HTTP_X_PROJECT_NAME',
                     'domain': 'HTTP_X_DOMAIN_ID',
                     'user_domain': 'HTTP_X_USER_DOMAIN_ID',
                     'project_domain': 'HTTP_X_PROJECT_DOMAIN_ID',
                     'request_id': 'openstack.request_id'}

    environ = request.environ

    for key in context_paras:
        context_paras[key] = environ.get(context_paras[key])
    role = environ.get('HTTP_X_ROLE')

    context_paras['is_admin'] = role == 'admin'
    return Context(**context_paras)


def get_context_from_neutron_context(context):
    ctx = Context()
    ctx.auth_token = context.auth_token
    ctx.user = context.user_id
    ctx.tenant = context.tenant_id
    ctx.tenant_name = context.tenant_name
    ctx.user_name = context.user_name
    ctx.resource_uuid = context.resource_uuid
    return ctx


class ContextBase(oslo_ctx.RequestContext):
    def __init__(self, auth_token=None, user_id=None, tenant_id=None,
                 is_admin=False, request_id=None, overwrite=True,
                 user_name=None, tenant_name=None, **kwargs):
        super(ContextBase, self).__init__(
            auth_token=auth_token,
            user=user_id or kwargs.get('user', None),
            tenant=tenant_id or kwargs.get('tenant', None),
            domain=kwargs.get('domain', None),
            user_domain=kwargs.get('user_domain', None),
            project_domain=kwargs.get('project_domain', None),
            is_admin=is_admin,
            read_only=kwargs.get('read_only', False),
            show_deleted=kwargs.get('show_deleted', False),
            request_id=request_id,
            resource_uuid=kwargs.get('resource_uuid', None),
            overwrite=overwrite)
        self.user_name = user_name
        self.tenant_name = tenant_name

    def to_dict(self):
        ctx_dict = super(ContextBase, self).to_dict()
        ctx_dict.update({
            'user_name': self.user_name,
            'tenant_name': self.tenant_name
        })
        return ctx_dict

    @classmethod
    def from_dict(cls, ctx):
        return cls(**ctx)


class Context(ContextBase):
    def __init__(self, **kwargs):
        super(Context, self).__init__(**kwargs)
        self._session = None

    @property
    def session(self):
        if not self._session:
            self._session = core.get_session()
        return self._session