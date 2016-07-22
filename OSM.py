# -*- coding: utf-8 -*-
#
#Copyright © 2011, Germán Márquez Mejía
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# constants
OSM_NODE = 'node'
OSM_WAY = 'way'
OSM_RELATION = 'relation'
OSM_MEMBER = 'member'
OSM_ND = 'nd'
OSM_ID = 'id'
OSM_REF = 'ref'
OSM_TYPE = 'type'
OSM_TAG = 'tag'
OSM_KEY = 'k'
OSM_VALUE = 'v'
OSM_ROLE = 'role'
OSM_LATITUDE = 'lat'
OSM_LONGITUDE = 'lon'

# classes
class OSMObject(dict):
  def __init__(self, oid):
    self.oid = oid # only OSM_ID is of interest for now

class OSMNode(OSMObject):
  def __init__(self, oid, lat, lon):
    super(OSMNode, self).__init__(oid)
    self.lon = lon
    self.lat = lat

class OSMWay(OSMObject):
  def __init__(self, oid):
    super(OSMWay, self).__init__(oid)
    self.nds = list() # a dictionary won't keep the nodes sorted

class OSMMember:
  def __init__(self, obj, mtype):
    self.obj = obj
    self.mtype = mtype
    self.role = ''
  def __init__(self, obj, mtype, role):
    self.obj = obj
    self.mtype = mtype
    self.role = role

class OSMRelation(OSMObject):
  def __init__(self, oid):
    super(OSMRelation, self).__init__(oid)
    self.members = dict()