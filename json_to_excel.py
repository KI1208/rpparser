# -*- coding: utf-8 -*-

from config import UPLOAD_FOLDER

import xlsxwriter
import json

def json_to_excel(filename):
    jsonfile = open(filename,'r')
    config = json.load(jsonfile)
    group_config = config['groupsSettings']
    outputfile = 'demo.xlsx'

    templist=[]
    for x in group_config:
        array = [len(row['journal']['journalVolumes']) for row in x['groupCopiesSettings']]
        a = max(array + [len(x['replicationSetsSettings'])])
        x['rowspan'] = a
        x['copynum'] = len(x['groupCopiesSettings'])
        templist = templist + [x['copynum']]
        copymax = max(templist)

    book = xlsxwriter.Workbook(UPLOAD_FOLDER + outputfile)
    ws1=book.add_worksheet('CGinfo')
    bold = book.add_format({'bold': True})

    # Header
    ws1.write(0,0,'CG name')
    ws1.write(0,1,'Enabled')
    ws1.write(0,2,'Primary RPA')
    ws1.write(0,3,'Replication Set name')

    for i in range(copymax):
        ws1.write(0,4 + i * 3, 'Site')
        ws1.write(0,5 + i * 3, 'Role')
        ws1.write(0,6 + i * 3, 'Journal')

    # Content
    rowidx = 0
    for idx,entry in enumerate(group_config):
        if entry['rowspan'] == 0:
            rowidx += 1

            ws1.write(rowidx, 0, entry['name'])
            ws1.write(rowidx, 1, entry['enabled'])
            ws1.write(rowidx, 2, entry['policy']['primaryRPANumber'])

            for j in range(copymax):
                ws1.write(rowidx, 4 + j * 3, 'Blank')
                ws1.write(rowidx, 5 + j * 3, 'Blank')
                ws1.write(rowidx, 6 + j * 3, 'Blank')

        for i in range(entry['rowspan']):
            rowidx += 1

            ws1.write(rowidx, 0, entry['name'])
            ws1.write(rowidx, 1, entry['enabled'])
            ws1.write(rowidx, 2, entry['policy']['primaryRPANumber'])

            try:
                ws1.write(rowidx, 3, entry['replicationSetsSettings'][i]['replicationSetName'])
            except IndexError:
                ws1.write(rowidx, 3, 'Blank')
            except:
                print 'Unexpected Error'

            for j in range(copymax):
                try:
                    ws1.write(rowidx, 4 + j*3, entry['groupCopiesSettings'][j]['name'])
                    ws1.write(rowidx, 5 + j*3, entry['groupCopiesSettings'][j]['roleInfo']['role'])
                    ws1.write(rowidx, 6 + j*3, entry['groupCopiesSettings'][j]['journal']['journalVolumes'][i]['volumeInfo']['volumeName'])
                except IndexError:
                    ws1.write(rowidx, 4 + j*3, 'Blank')
                    ws1.write(rowidx, 5 + j*3, 'Blank')
                    ws1.write(rowidx, 6 + j*3, 'Blank')
                except:
                    print 'Unexpected Error'

    book.close()
    return outputfile


