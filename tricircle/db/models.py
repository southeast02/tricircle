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


from oslo_db.sqlalchemy import models
import sqlalchemy as sql
from sqlalchemy.dialects import mysql
from sqlalchemy import schema

from tricircle.db import core


def MediumText():
    return sql.Text().with_variant(mysql.MEDIUMTEXT(), 'mysql')


# Resource Model
class Aggregate(core.ModelBase, core.DictBase, models.TimestampMixin):
    """Represents a cluster of hosts that exists in this zone."""
    __tablename__ = 'aggregates'
    attributes = ['id', 'name', 'created_at', 'updated_at']

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String(255), unique=True)


class AggregateMetadata(core.ModelBase, core.DictBase, models.TimestampMixin):
    """Represents a metadata key/value pair for an aggregate."""
    __tablename__ = 'aggregate_metadata'
    __table_args__ = (
        sql.Index('aggregate_metadata_key_idx', 'key'),
        schema.UniqueConstraint(
            'aggregate_id', 'key',
            name='uniq_aggregate_metadata0aggregate_id0key'),
    )
    attributes = ['id', 'key', 'value', 'aggregate_id',
                  'created_at', 'updated_at']

    id = sql.Column(sql.Integer, primary_key=True)
    key = sql.Column(sql.String(255), nullable=False)
    value = sql.Column(sql.String(255), nullable=False)
    aggregate_id = sql.Column(sql.Integer,
                              sql.ForeignKey('aggregates.id'), nullable=False)


class InstanceTypes(core.ModelBase, core.DictBase, models.TimestampMixin):
    """Represents possible flavors for instances.

    Note: instance_type and flavor are synonyms and the term instance_type is
    deprecated and in the process of being removed.
    """
    __tablename__ = 'instance_types'
    attributes = ['id', 'name', 'memory_mb', 'vcpus', 'root_gb',
                  'ephemeral_gb', 'flavorid', 'swap', 'rxtx_factor',
                  'vcpu_weight', 'disabled', 'is_public', 'created_at',
                  'updated_at']

    # Internal only primary key/id
    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String(255), unique=True)
    memory_mb = sql.Column(sql.Integer, nullable=False)
    vcpus = sql.Column(sql.Integer, nullable=False)
    root_gb = sql.Column(sql.Integer)
    ephemeral_gb = sql.Column(sql.Integer)
    # Public facing id will be renamed public_id
    flavorid = sql.Column(sql.String(255), unique=True)
    swap = sql.Column(sql.Integer, nullable=False, default=0)
    rxtx_factor = sql.Column(sql.Float, default=1)
    vcpu_weight = sql.Column(sql.Integer)
    disabled = sql.Column(sql.Boolean, default=False)
    is_public = sql.Column(sql.Boolean, default=True)


class InstanceTypeProjects(core.ModelBase, core.DictBase,
                           models.TimestampMixin):
    """Represent projects associated instance_types."""
    __tablename__ = 'instance_type_projects'
    __table_args__ = (schema.UniqueConstraint(
        'instance_type_id', 'project_id',
        name='uniq_instance_type_projects0instance_type_id0project_id'),
    )
    attributes = ['id', 'instance_type_id', 'project_id', 'created_at',
                  'updated_at']

    id = sql.Column(sql.Integer, primary_key=True)
    instance_type_id = sql.Column(sql.Integer,
                                  sql.ForeignKey('instance_types.id'),
                                  nullable=False)
    project_id = sql.Column(sql.String(255))


class InstanceTypeExtraSpecs(core.ModelBase, core.DictBase,
                             models.TimestampMixin):
    """Represents additional specs as key/value pairs for an instance_type."""
    __tablename__ = 'instance_type_extra_specs'
    __table_args__ = (
        sql.Index('instance_type_extra_specs_instance_type_id_key_idx',
                  'instance_type_id', 'key'),
        schema.UniqueConstraint(
            'instance_type_id', 'key',
            name='uniq_instance_type_extra_specs0instance_type_id0key'),
        {'mysql_collate': 'utf8_bin'},
    )
    attributes = ['id', 'key', 'value', 'instance_type_id', 'created_at',
                  'updated_at']

    id = sql.Column(sql.Integer, primary_key=True)
    key = sql.Column(sql.String(255))
    value = sql.Column(sql.String(255))
    instance_type_id = sql.Column(sql.Integer,
                                  sql.ForeignKey('instance_types.id'),
                                  nullable=False)


class KeyPair(core.ModelBase, core.DictBase, models.TimestampMixin):
    """Represents a public key pair for ssh / WinRM."""
    __tablename__ = 'key_pairs'
    __table_args__ = (
        schema.UniqueConstraint('user_id', 'name',
                                name='uniq_key_pairs0user_id0name'),
    )
    attributes = ['id', 'name', 'user_id', 'fingerprint', 'public_key', 'type',
                  'created_at', 'updated_at']

    id = sql.Column(sql.Integer, primary_key=True, nullable=False)
    name = sql.Column(sql.String(255), nullable=False)
    user_id = sql.Column(sql.String(255))
    fingerprint = sql.Column(sql.String(255))
    public_key = sql.Column(MediumText())
    type = sql.Column(sql.Enum('ssh', 'x509', name='keypair_types'),
                      nullable=False, server_default='ssh')


class Quota(core.ModelBase, core.DictBase, models.TimestampMixin):
    """Represents a single quota override for a project.

    If there is no row for a given project id and resource, then the
    default for the quota class is used.  If there is no row for a
    given quota class and resource, then the default for the
    deployment is used. If the row is present but the hard limit is
    Null, then the resource is unlimited.
    """
    __tablename__ = 'quotas'
    __table_args__ = (
        schema.UniqueConstraint('project_id', 'resource',
                                name='uniq_quotas0project_id0resource'),
    )
    attributes = ['id', 'project_id', 'resource', 'hard_limit',
                  'created_at', 'updated_at']

    id = sql.Column(sql.Integer, primary_key=True)
    project_id = sql.Column(sql.String(255))
    resource = sql.Column(sql.String(255), nullable=False)
    hard_limit = sql.Column(sql.Integer)


class VolumeTypes(core.ModelBase, core.DictBase, models.TimestampMixin):
    """Represent possible volume_types of volumes offered."""
    __tablename__ = "volume_types"
    attributes = ['id', 'name', 'description', 'qos_specs_id', 'is_public',
                  'created_at', 'updated_at']

    id = sql.Column(sql.String(36), primary_key=True)
    name = sql.Column(sql.String(255), unique=True)
    description = sql.Column(sql.String(255))
    # A reference to qos_specs entity
    qos_specs_id = sql.Column(sql.String(36),
                              sql.ForeignKey('quality_of_service_specs.id'))
    is_public = sql.Column(sql.Boolean, default=True)


class QualityOfServiceSpecs(core.ModelBase, core.DictBase,
                            models.TimestampMixin):
    """Represents QoS specs as key/value pairs.

    QoS specs is standalone entity that can be associated/disassociated
    with volume types (one to many relation).  Adjacency list relationship
    pattern is used in this model in order to represent following hierarchical
    data with in flat table, e.g, following structure

    qos-specs-1  'Rate-Limit'
         |
         +------>  consumer = 'front-end'
         +------>  total_bytes_sec = 1048576
         +------>  total_iops_sec = 500

    qos-specs-2  'QoS_Level1'
         |
         +------>  consumer = 'back-end'
         +------>  max-iops =  1000
         +------>  min-iops = 200

    is represented by:

      id       specs_id       key                  value
    ------     --------   -------------            -----
    UUID-1     NULL       QoSSpec_Name           Rate-Limit
    UUID-2     UUID-1       consumer             front-end
    UUID-3     UUID-1     total_bytes_sec        1048576
    UUID-4     UUID-1     total_iops_sec           500
    UUID-5     NULL       QoSSpec_Name           QoS_Level1
    UUID-6     UUID-5       consumer             back-end
    UUID-7     UUID-5       max-iops               1000
    UUID-8     UUID-5       min-iops               200
    """
    __tablename__ = 'quality_of_service_specs'
    attributes = ['id', 'specs_id', 'key', 'value', 'created_at', 'updated_at']

    id = sql.Column(sql.String(36), primary_key=True)
    specs_id = sql.Column(sql.String(36), sql.ForeignKey(id))
    key = sql.Column(sql.String(255))
    value = sql.Column(sql.String(255))


# Site Model
class Site(core.ModelBase, core.DictBase):
    __tablename__ = 'cascaded_sites'
    attributes = ['site_id', 'site_name', 'az_id']

    site_id = sql.Column('site_id', sql.String(length=64), primary_key=True)
    site_name = sql.Column('site_name', sql.String(length=64), unique=True,
                           nullable=False)
    az_id = sql.Column('az_id', sql.String(length=64), nullable=False)


class SiteServiceConfiguration(core.ModelBase, core.DictBase):
    __tablename__ = 'cascaded_site_service_configuration'
    attributes = ['service_id', 'site_id', 'service_type', 'service_url']

    service_id = sql.Column('service_id', sql.String(length=64),
                            primary_key=True)
    site_id = sql.Column('site_id', sql.String(length=64),
                         sql.ForeignKey('cascaded_sites.site_id'),
                         nullable=False)
    service_type = sql.Column('service_type', sql.String(length=64),
                              nullable=False)
    service_url = sql.Column('service_url', sql.String(length=512),
                             nullable=False)


# AZ pod mapping model
class PodMap(core.ModelBase, core.DictBase, models.TimestampMixin):
    __tablename__ = 'pod_map'
    __table_args__ = (
        schema.UniqueConstraint(
            'az_name', 'pod_name',
            name='pod_map0az_name0pod_name'),
    )
    attributes = ['id', 'az_name', 'dc_name', 'pod_name', 'pod_az_name',
                  'created_at', 'updated_at']

    id = sql.Column(sql.String(36), primary_key=True)
    az_name = sql.Column('az_name', sql.String(length=255), nullable=True)
    dc_name = sql.Column('dc_name', sql.String(length=255), nullable=True)
    pod_name = sql.Column('pod_name', sql.String(length=255), nullable=False)
    pod_az_name = sql.Column('pod_az_name', sql.String(length=255),
                             nullable=True)


# Tenant and pod binding model
class PodBinding(core.ModelBase, core.DictBase, models.TimestampMixin):
    __tablename__ = 'pod_binding'
    __table_args__ = (
        schema.UniqueConstraint(
            'tenant_id', 'az_pod_map_id',
            name='pod_binding0tenant_id0az_pod_map_id'),
    )
    attributes = ['id', 'tenant_id', 'az_pod_map_id',
                  'created_at', 'updated_at']

    id = sql.Column(sql.String(36), primary_key=True)
    tenant_id = sql.Column('tenant_id', sql.String(36), nullable=False)
    az_pod_map_id = sql.Column('az_pod_map_id', sql.String(36),
                               sql.ForeignKey('pod_map.id'),
                               nullable=False)


# Routing Model
class ResourceRouting(core.ModelBase, core.DictBase, models.TimestampMixin):
    __tablename__ = 'cascaded_sites_resource_routing'
    __table_args__ = (
        schema.UniqueConstraint(
            'top_id', 'site_id',
            name='cascaded_sites_resource_routing0top_id0site_id'),
    )
    attributes = ['id', 'top_id', 'bottom_id', 'site_id', 'project_id',
                  'resource_type', 'created_at', 'updated_at']

    id = sql.Column('id', sql.Integer, primary_key=True)
    top_id = sql.Column('top_id', sql.String(length=36), nullable=False)
    bottom_id = sql.Column('bottom_id', sql.String(length=36))
    site_id = sql.Column('site_id', sql.String(length=64),
                         sql.ForeignKey('cascaded_sites.site_id'),
                         nullable=False)
    project_id = sql.Column('project_id', sql.String(length=36))
    resource_type = sql.Column('resource_type', sql.String(length=64),
                               nullable=False)