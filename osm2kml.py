#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# osm2kml.py-0.2.1
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

import sys
from OSM import *
from datetime import datetime
from xml.dom.minidom import parse, parseString, Document

if len(sys.argv) < 2:
  print 'Usage: {program} <file>'.format(program=sys.argv[0])
  sys.exit()

start = datetime.now()

# Read input file
ifile = sys.argv[1]
osmDoc = parse(ifile)

# Index nodes, ways and relations
nodes = dict()
for n in osmDoc.getElementsByTagName(OSM_NODE):
  node = OSMNode(n.getAttribute(OSM_ID), n.getAttribute(OSM_LATITUDE), n.getAttribute(OSM_LONGITUDE))
  for t in n.getElementsByTagName(OSM_TAG):
    node[t.getAttribute(OSM_KEY)] = t.getAttribute(OSM_VALUE)
  nodes[node.oid] = node

ways = dict()
for w in osmDoc.getElementsByTagName(OSM_WAY):
  way = OSMWay(w.getAttribute(OSM_ID))
  for t in w.getElementsByTagName(OSM_TAG):
    way[t.getAttribute(OSM_KEY)] = t.getAttribute(OSM_VALUE)
  for n in w.getElementsByTagName(OSM_ND):
    ref = n.getAttribute(OSM_REF)
    way.nds.append(nodes[ref])
  ways[way.oid] = way

relations = dict()
for r in osmDoc.getElementsByTagName(OSM_RELATION):
  rel = OSMRelation(r.getAttribute(OSM_ID))
  for t in r.getElementsByTagName(OSM_TAG):
    rel[t.getAttribute(OSM_KEY)] = t.getAttribute(OSM_VALUE)
  for m in r.getElementsByTagName(OSM_MEMBER):
    search = {
      OSM_NODE: nodes,
      OSM_WAY: ways,
      OSM_RELATION: relations
      }
    mtype = m.getAttribute(OSM_TYPE)
    index = search[mtype]
    ref = m.getAttribute(OSM_REF)
    if ref in index: # NOTE: incomplete members are taken off the relation
      obj = index[ref]
      member = OSMMember(obj, mtype, m.getAttribute(OSM_ROLE))
      rel.members[obj.oid] = member
  relations[rel.oid] = rel

# Create the basic KML structure and appearance
base = """
<kml>
  <Document>
    <name>Energy objects</name>
    <description>Converted from OSM data with osm2kml</description>
    <Style id="35kv">
		<IconStyle>
			<scale>0.8</scale>
			<Icon>
				<href>http://www.earthpoint.us/Dots/GoogleEarth/shapes/triangle.png</href>
			</Icon>
		</IconStyle>
      <LineStyle>
        <width>1.5</width>
        <color>ff326482</color>
      </LineStyle>
      <PolyStyle>
        <color>ff326482</color>
      </PolyStyle>
    </Style>
    <Style id="110kv">
		<IconStyle>
			<scale>0.8</scale>
			<Icon>
				<href>http://www.earthpoint.us/Dots/GoogleEarth/shapes/triangle.png</href>
			</Icon>
		</IconStyle>
      <LineStyle>
        <width>1.5</width>
        <color>ffc8b400</color>
      </LineStyle>
      <PolyStyle>
        <color>ffc8b400</color>
      </PolyStyle>
    </Style>

    <Style id="kl_connection">
		<IconStyle>
			<scale>0.8</scale>
			<Icon>
				<href>http://www.earthpoint.us/Dots/GoogleEarth/shapes/placemark_circle.png</href>
			</Icon>
		</IconStyle>
    </Style>

    <Style id="kl_end_connection">
		<IconStyle>
			<scale>0.8</scale>
			<Icon>
				<href>http://www.earthpoint.us/Dots/GoogleEarth/shapes/placemark_square.png</href>
			</Icon>
		</IconStyle>
    </Style>

  </Document>
</kml>
"""
kmlDoc = parseString(base)
doc = kmlDoc.documentElement.firstChild.nextSibling

for way in ways.values():
  if 'power' in way:
    placemark = kmlDoc.createElement('Placemark')
    if 'name' in way:
      name = kmlDoc.createElement('name')
      nameText = kmlDoc.createTextNode(way['name'])
      name.appendChild(nameText)
      placemark.appendChild(name)
    if 'operator' in way:
      description = kmlDoc.createElement('description')
      descriptionText = kmlDoc.createTextNode(way['operator'])
      description.appendChild(descriptionText)
      placemark.appendChild(description)
    if 'voltage' in way:
      StyleId="35kv"
      z=10
      if way['voltage']=="110000":
        StyleId="110kv"
        z=20
      description = kmlDoc.createElement('styleUrl')
      descriptionText = kmlDoc.createTextNode('#'+StyleId)
      description.appendChild(descriptionText)
      placemark.appendChild(description)
    if way["power"]=="station":
      polygon = kmlDoc.createElement('Polygon')
      extrude = kmlDoc.createElement('extrude')
      extrudeText = kmlDoc.createTextNode('1')
      extrude.appendChild(extrudeText)
      polygon.appendChild(extrude)
      altitude = kmlDoc.createElement('altitudeMode')
      altitudeText = kmlDoc.createTextNode('relativeToGround')
      altitude.appendChild(altitudeText)
      polygon.appendChild(altitude)
      outer = kmlDoc.createElement('outerBoundaryIs')
      ring = kmlDoc.createElement('LinearRing')
      coord = kmlDoc.createElement('coordinates')
 #     print("way.nds:",way.nds)
      nodelist = ''.join(['{x},{y},{z} '.format(x=node.lon, y=node.lat, z=10) for node in way.nds])
      coordText = kmlDoc.createTextNode(nodelist)
      coord.appendChild(coordText)
      ring.appendChild(coord)
      outer.appendChild(ring)
      polygon.appendChild(outer)
      placemark.appendChild(polygon)
    if way["power"]=="line":
      LineString = kmlDoc.createElement('LineString')
      altitude = kmlDoc.createElement('altitudeMode')
      altitudeText = kmlDoc.createTextNode('relativeToGround')
      altitude.appendChild(altitudeText)
      LineString.appendChild(altitude)
      coord = kmlDoc.createElement('coordinates')
 #     print("way.nds:",way.nds)
      nodelist = ''.join(['{x},{y},{z} '.format(x=node.lon, y=node.lat, z=z) for node in way.nds])
      coordText = kmlDoc.createTextNode(nodelist)
      coord.appendChild(coordText)
      LineString.appendChild(coord)
      placemark.appendChild(LineString)
    if way["power"]=="cable":
      z=0
      LineString = kmlDoc.createElement('LineString')
      altitude = kmlDoc.createElement('altitudeMode')
      altitudeText = kmlDoc.createTextNode('relativeToGround')
      altitude.appendChild(altitudeText)
      LineString.appendChild(altitude)
      coord = kmlDoc.createElement('coordinates')
 #     print("way.nds:",way.nds)
      nodelist = ''.join(['{x},{y},{z} '.format(x=node.lon, y=node.lat, z=z) for node in way.nds])
      coordText = kmlDoc.createTextNode(nodelist)
      coord.appendChild(coordText)
      LineString.appendChild(coord)
      placemark.appendChild(LineString)
    doc.appendChild(placemark)

for node in nodes.values():
  if 'power' in node:
    placemark = kmlDoc.createElement('Placemark')
    note=""
    operator=""
    if 'ref' in node:
      name = kmlDoc.createElement('name')
      nameText = kmlDoc.createTextNode(node['ref'])
      name.appendChild(nameText)
      placemark.appendChild(name)
    if 'note' in node:
      note=node["note"]
    if 'operator' in node:
      operator=node["operator"]
    if note != "" or operator != "":
      description = kmlDoc.createElement('description')
      descriptionText = kmlDoc.createTextNode(note + " (" + operator + ")")
      description.appendChild(descriptionText)
      placemark.appendChild(description)
    if 'voltage' in node:
      StyleId="35kv"
      z=10
      if node['voltage']=="110000":
        StyleId="110kv"
        z=20
      description = kmlDoc.createElement('styleUrl')
      descriptionText = kmlDoc.createTextNode('#'+StyleId)
      description.appendChild(descriptionText)
      placemark.appendChild(description)
    if node["power"]=="tower":
      tower = kmlDoc.createElement('Point')
      extrude = kmlDoc.createElement('extrude')
      extrudeText = kmlDoc.createTextNode('1')
      extrude.appendChild(extrudeText)
      tower.appendChild(extrude)
      altitude = kmlDoc.createElement('altitudeMode')
      altitudeText = kmlDoc.createTextNode('relativeToGround')
      altitude.appendChild(altitudeText)
      tower.appendChild(altitude)
      coord = kmlDoc.createElement('coordinates')
#     print("node:",node)
      nodelist = ''.join('{x},{y},{z} '.format(x=node.lon, y=node.lat, z=z))
      coordText = kmlDoc.createTextNode(nodelist)
      coord.appendChild(coordText)
      tower.appendChild(coord)
      placemark.appendChild(tower)
    if node["power"]=="link":
      z=0
      tower = kmlDoc.createElement('Point')
      extrude = kmlDoc.createElement('extrude')
      extrudeText = kmlDoc.createTextNode('1')
      extrude.appendChild(extrudeText)
      tower.appendChild(extrude)
      altitude = kmlDoc.createElement('altitudeMode')
      altitudeText = kmlDoc.createTextNode('relativeToGround')
      altitude.appendChild(altitudeText)
      tower.appendChild(altitude)
      StyleId = "kl_connection"
      if node["link"] == "connection":
        StyleId = "kl_connection"
      if node["link"] == "end_connection":
        StyleId = "kl_end_connection"
      style = kmlDoc.createElement('styleUrl')
      StyleText = kmlDoc.createTextNode('#'+StyleId)
      style.appendChild(StyleText)
      placemark.appendChild(style)
      coord = kmlDoc.createElement('coordinates')
#     print("node:",node)
      nodelist = ''.join('{x},{y},{z} '.format(x=node.lon, y=node.lat, z=z))
      coordText = kmlDoc.createTextNode(nodelist)
      coord.appendChild(coordText)
      tower.appendChild(coord)
      placemark.appendChild(tower)
    doc.appendChild(placemark)

#
## Add placemarks to document
#for rel in relations.values():
#  if 'power' in rel:
#    placemark = kmlDoc.createElement('Placemark')
#    if 'name' in rel:
#      name = kmlDoc.createElement('name')
#      nameText = kmlDoc.createTextNode(rel['name'])
#      name.appendChild(nameText)
#      placemark.appendChild(name)
#    if 'note' in rel:
#      description = kmlDoc.createElement('description')
#      descriptionText = kmlDoc.createTextNode(rel['note'])
#      description.appendChild(descriptionText)
#      placemark.appendChild(description)
#    if 'height' in rel:
#      height = rel['height'].replace(' ', '')
#    elif 'building:height' in rel:
#      height = rel['building:height'].replace(' ', '')
#    else:
#      height = '17'
#    polygon = kmlDoc.createElement('Polygon')
#    extrude = kmlDoc.createElement('extrude')
#    extrudeText = kmlDoc.createTextNode('1')
#    extrude.appendChild(extrudeText)
#    polygon.appendChild(extrude)
#    altitude = kmlDoc.createElement('altitudeMode')
#    altitudeText = kmlDoc.createTextNode('relativeToGround')
#    altitude.appendChild(altitudeText)
#    polygon.appendChild(altitude)
#    for m in rel.members.values():
#      if m.mtype == OSM_WAY:
#        role = m.role
#        if role == 'outer' or role == '':
#          outer = kmlDoc.createElement('outerBoundaryIs')
#          ring = kmlDoc.createElement('LinearRing')
#          coord = kmlDoc.createElement('coordinates')
#          nodelist = ''.join(['{x},{y},{z} '.format(x=node.lon, y=node.lat, z=height) for node in m.obj.nds])
#          coordText = kmlDoc.createTextNode(nodelist)
#          coord.appendChild(coordText)
#          ring.appendChild(coord)
#          outer.appendChild(ring)
#          polygon.appendChild(outer)
#        elif role == 'inner':
#          inner = kmlDoc.createElement('innerBoundaryIs')
#          ring = kmlDoc.createElement('LinearRing')
#          coord = kmlDoc.createElement('coordinates')
#          nodelist = ''.join(['{x},{y},{z} '.format(x=node.lon, y=node.lat, z=height) for node in m.obj.nds])
#          coordText = kmlDoc.createTextNode(nodelist)
#          coord.appendChild(coordText)
#          ring.appendChild(coord)
#          inner.appendChild(ring)
#          polygon.appendChild(inner)
#    placemark.appendChild(polygon)
#    doc.appendChild(placemark)
#
#for way in ways.values():
  #if 'building' in way:
    #placemark = kmlDoc.createElement('Placemark')
    #if 'name' in way:
      #name = kmlDoc.createElement('name')
      #nameText = kmlDoc.createTextNode(way['name'])
      #name.appendChild(nameText)
      #placemark.appendChild(name)
    #if 'alt_name' in way:
      #description = kmlDoc.createElement('description')
      #descriptionText = kmlDoc.createTextNode(way['alt_name'])
      #description.appendChild(descriptionText)
      #placemark.appendChild(description)
    #if 'height' in way:
      #height = way['height'].replace(' ', '')
    #elif 'building:height' in way:
      #height = way['building:height'].replace(' ', '')
    #else:
      #height = '17'
    #polygon = kmlDoc.createElement('Polygon')
    #extrude = kmlDoc.createElement('extrude')
    #extrudeText = kmlDoc.createTextNode('1')
    #extrude.appendChild(extrudeText)
    #polygon.appendChild(extrude)
    #altitude = kmlDoc.createElement('altitudeMode')
    #altitudeText = kmlDoc.createTextNode('relativeToGround')
    #altitude.appendChild(altitudeText)
    #polygon.appendChild(altitude)
    #outer = kmlDoc.createElement('outerBoundaryIs')
    #ring = kmlDoc.createElement('LinearRing')
    #coord = kmlDoc.createElement('coordinates')
    #nodelist = ''.join(['{x},{y},{z} '.format(x=node.lon, y=node.lat, z=height) for node in way.nds.values()])
    #coordText = kmlDoc.createTextNode(nodelist)
    #coord.appendChild(coordText)
    #ring.appendChild(coord)
    #outer.appendChild(ring)
    #polygon.appendChild(outer)
    #placemark.appendChild(polygon)
    #doc.appendChild(placemark)

# Output result
print kmlDoc.toprettyxml(indent="  ", encoding="utf-8")

#end = datetime.now()
#print '[ {d} ]\t{s}\t{t}\t{f}'.format(d=end.strftime("%Y-%m-%d %H:%M:%S"), s=sys.argv[0], t=(end - start), f=ifile)
