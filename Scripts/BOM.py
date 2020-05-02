#execfile(r'C:\Users\Admin\Documents\KiCad\Scripts\BOM.py')

#By Alan Samet
#This script generates a pipe-delimited BOM for Digikey based on a custom field in the 
#schematic editor. To use this script, open your schematic in the editor, right click
#the part you want to add a BOM component to and select "Edit" (or, just put your mouse 
#pointer over the component and press 'E' on the keyboard. Add a field called "Digikey"
#to the component and enter the part number. 
#
#If you have several components with the same value specified, you only need to assign a
#part number to one of them and the script assumes that all other components with the same
#value are the same part number. I don't yet have this script comparing packages, so
#if you have a 2.2u 1206 and a 2.2u 0805 package, for instance, you'll need to specify
#a different value to keep this script from complaining (e.g. 2.2u and 2.2uF)

import re, pcbnew
pcb = pcbnew.GetBoard()

sch_path = pcb.GetFileName().replace('.kicad_pcb', '.sch')#r'C:\Users\Admin\Documents\KiCad\Projects\MotorControl\Trinamic\BasicMo\BasicMo\BasicMo.sch'
fd_in = open(sch_path, 'r')
raw = fd_in.read()
fd_in.close()

rema = re.compile(r'\$Comp(.*?)\$EndComp', re.MULTILINE|re.DOTALL)

matches = rema.findall(raw)

valkeys = {}
bom = []

for m in matches:
    fields = [l.strip() for l in m.strip().split('\n') if l[0] == 'F']
    ref = fields[0].split()[2]
    val = fields[1].split()[2]
    pn = [f for f in fields if f.find('"Digikey"') > -1]
    if len(pn) > 0:
        pn = pn[0].replace('\xe2\x80\x8e', '').split()[2]
        if valkeys.has_key(val) and valkeys[val] != pn:
            print 'Same value, different part!', val, valkeys[pn], ref
        #print ref, val, pn
        else:
            valkeys[val] = pn

pnvals = {}
#for k in valkeys:
    #pnvals[valkeys[k]] = [k for k in valkeys if valkeys[k] == 

partcount = 0
for val in valkeys:
    components = []
    for m in matches:
        fields = [l.strip() for l in m.strip().split('\n') if l[0] == 'F']
        ref = fields[0].split()[2]
        v = fields[1].split()[2]
        if v == val:
            partcount += 1
            components.append(ref)
    print '%s|%s|%s|%s' % (len(components), ','.join([c.replace('"', '') for c in components]), val.replace('"', ''), valkeys[val].replace('"', ''))

print 'Total parts:', partcount
#print 'Unique parts:', cc

missing_parts = {}
for m in matches:
    fields = [l.strip() for l in m.strip().split('\n') if l[0] == 'F']
    ref = fields[0].split()[2]
    val = fields[1].split()[2]
    if valkeys.has_key(val):
        #print ref, val, valkeys[val]
        pass
    else:
        #print 'NO PART FOR: ', ref, val
        if ref in missing_parts.keys():
            raise Exception("Part already in missing parts: %s" % ref)
        missing_parts[ref] = val

keys = missing_parts.keys()
keys.sort()
for k in keys:
    print 'NO PART FOR: ', k, missing_parts[k]