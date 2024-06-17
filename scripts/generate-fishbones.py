'''
author: J. Beasley
date: 05/2021

hi!

Generates fishbones using a
locator built from road centerlines.
Locator and address points should be 
in same spatial reference. 
'''

import arcpy

arcpy.env.overwriteOutput = True 
scratch_gdb = arcpy.env.scratchGDB

def generateFishbones(ap, loc, geocode_flds, out_fishbone, rcl_id=''):

    arcpy.AddMessage('Copying address points for processing...')
    ap_copy = arcpy.CopyFeatures_management(ap, r'in_memory\ap_copy')

    arcpy.AddMessage('Calculating XY values for existing address points...')
    arcpy.AddGeometryAttributes_management(ap_copy, 'POINT_X_Y_Z_M')

    arcpy.AddMessage('Converting points to db table...')
    ap_table = arcpy.TableToTable_conversion(ap_copy, 'in_memory', 'ap_copy_table')

    geocode_fieldmap = "'Address or Place' {} VISIBLE NONE;".format(geocode_flds[0]) \
                        + "Address2 <None> VISIBLE NONE;" \
                        + "Address3 <None> VISIBLE NONE;" \
                        + "Neighborhood <None> VISIBLE NONE;" \
                        + "City {} VISIBLE NONE;".format(geocode_flds[1]) \
                        + "County <None> VISIBLE NONE;" \
                        + "State {} VISIBLE NONE;".format(geocode_flds[2]) \
                        + "ZIP {} VISIBLE NONE;".format(geocode_flds[3]) \
                        + "ZIP4 <None> VISIBLE NONE;" \
                        + "Country <None> VISIBLE NONE"

    arcpy.AddMessage('Geocoding addresses...')
    geocode = arcpy.GeocodeAddresses_geocoding(ap_table, loc, geocode_fieldmap, scratch_gdb + r'\geocoderesult', output_fields='ALL')

    where = 'DisplayX IS NOT NULL AND DisplayX <> 0'
    select = arcpy.SelectLayerByAttribute_management(geocode, 'NEW_SELECTION', where)

    fld_l = [n.name for n in arcpy.ListFields(geocode)]
    if rcl_id not in fld_l:
        rcl_id = ''

    arcpy.AddMessage('Generating fishbones...')
    fishbone = arcpy.XYToLine_management(select, out_fishbone, 'USER_POINT_X', 'USER_POINT_Y', 'DisplayX', 'DisplayY', 'Geodesic', id_field=rcl_id)

    field_rename = [['USER_POINT_X', 'Orig_X'], 
                    ['USER_POINT_Y', 'Orig_Y'], 
                    ['DisplayX', 'Geocode_X'], 
                    ['DisplayY', 'Geocode_Y']]
    
    arcpy.AddMessage('Cleaning fields...')
    for f in field_rename:
        arcpy.AlterField_management(fishbone, f[0], f[1], f[1].replace('_', ' '))


if __name__ == '__main__':

    ap_fc = arcpy.GetParameterAsText(0)
    rcl_loc = arcpy.GetParameterAsText(1)
    rcl_uid = arcpy.GetParameterAsText(2)

    add_fld = arcpy.GetParameterAsText(3)
    city_fld = arcpy.GetParameterAsText(4)
    state_fld = arcpy.GetParameterAsText(5)
    zipcode = arcpy.GetParameterAsText(6)
    gc_flds = [add_fld, city_fld, state_fld, zipcode]

    fishbone = arcpy.GetParameterAsText(7)

    try:
        generateFishbones(ap_fc, rcl_loc, gc_flds, fishbone, rcl_uid)

    except Exception as e:
        arcpy.AddError(e)
