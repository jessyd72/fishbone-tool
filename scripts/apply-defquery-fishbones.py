'''
author: J. Beasley
date: 02/2022

filters fishbone resutls to only show 
those related to a selected road centerline.
Works with multiple selections. 
'''

import arcpy

def preCheck(flag_lyr):
    
    desc = arcpy.da.Describe(flag_lyr)
    if desc['FIDSet']:
        arcpy.AddMessage('{0} flags are selected...'.format(str(len(desc['FIDSet']))))
    else:
        arcpy.AddError('PROBLEM!! No flags are selected!')
        exit()


def createDefQuery(map_name, flags, flag_id, fishbone, fishbone_id):

    arcpy.AddMessage('Compiling unique IDs...')
    ids = list({"'{}'".format(x[0]) for x in arcpy.da.SearchCursor(flags, [flag_id])})
    ids_s = ', '.join(ids)

    arcpy.AddMessage('Creating query...')
    query_name = 'Query {0}'.format(ids_s)
    query = '{0} IN ({1})'.format(fishbone_id, ids_s)

    aprx = arcpy.mp.ArcGISProject('CURRENT')
    curr_map = [m for m in aprx.listMaps(map_name)]
    if curr_map:
        fishbone_lyr = [l for l in curr_map[0].listLayers() if l.name == fishbone]
        if fishbone_lyr:
            cim = fishbone_lyr[0].getDefinition('V2')
            cim.featureTable.definitionExpressionName = query_name
            cim.featureTable.definitionExpression = query
            arcpy.AddMessage('Applying definition query...')
            fishbone_lyr[0].setDefinition(cim)


if __name__ == "__main__":

    map = arcpy.GetParameterAsText(0)
    flag_lyr = arcpy.GetParameterAsText(1)
    flag_id_fld = arcpy.GetParameterAsText(2)
    fishbone_lyr = arcpy.GetParameterAsText(3)
    fishbone_id_fld = arcpy.GetParameterAsText(4)

    preCheck(flag_lyr)
    createDefQuery(map, flag_lyr, flag_id_fld, fishbone_lyr, fishbone_id_fld)

    