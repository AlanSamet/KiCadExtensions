#execfile(r'C:\Users\Admin\Documents\KiCad\Scripts\PlaceComponents.py')

#By Alan Samet
#
#This is a handful of useful scripts that I wrote for placing components in pcbnew. It is important to note that the Edit >> Undo menu command doesn't
#seem to add these steps to the undo buffer, so you'll probably want to save your PCB before experimenting with this. 

import pcbnew
import re
pcb = pcbnew.GetBoard()

#Conversions to/from KiCad format. Yes, I know, there are built-in ones. I discovered those after writing these and haven't refactored. 
def mm_to_nm(v):
    return int(v * 1000000)
    
def nm_to_mm(v):
    return v / 1000000.0

def get_all_component_names():
    return [x.GetReference() for x in pcb.GetModules()]

#Finds all components based on a wildcard.
#Example, if you want to list all resistors in a circuit, you can say: print(get_wildcard_component_names('R*')
def get_wildcard_component_names(pattern, all_names = None):
    if all_names == None:
        all_names = get_all_component_names() #Optimization to pass all component names for efficiency. 
    exp = re.compile('^%s$' % pattern.replace('*', '.*'))
    return [n for n in all_names if not exp.match(n) is None]

def get_component(name):
    return [x for x in pcb.GetModules() if x.GetReference() == name][0]

'''
suppress_refresh parameter is for when this is called in a loop. 

Example Usage:

for i in range(5):
    place_component_relative_mm('D%s' % (i + 1), 'R%s' % (i + 13), 0, 2)

'''
def place_component_relative_mm(reference_component_name, component_to_move, relative_x, relative_y, suppress_refresh = False):
    a = get_component(reference_component_name)
    b = get_component(component_to_move)

    pos_a = a.GetPosition()
    b.SetPosition(pcbnew.wxPoint(pos_a[0] + mm_to_nm(relative_x), pos_a[1] + mm_to_nm(relative_y)))
    if not suppress_refresh:
        pcbnew.Refresh()

#Same as above, only you can provide a list of components as the first parameter. 
def place_components_relative_mm(components_list, relative_x, relative_y, suppress_refresh = False):
    for i in range(len(components_list) - 1):
        place_component_relative_mm(components_list[i], components_list[i+1], relative_x, relative_y, True)
    if not suppress_refresh:
        pcbnew.Refresh()
    
#You can pass a list of component names to this function as the first parameter. 
'''for m in [m for m in pcb.GetModules() if m.GetReference()[:2] == 'JP' and m.GetReference() not in ['JP1', 'JP2', 'JP3']]: 
    set_component_reference_position(m.GetReference(), 0, -4)'''
def place_component_reference_position(component_name, relative_x, relative_y, justification = None, suppress_refresh = False):
    if isinstance(component_name, list):
        for c in component_name:
            place_component_reference_position(c, relative_x, relative_y, justification, True)
    else:
        a = get_component(component_name)
        b = a.Reference()
        pos_a = a.GetPosition()
        b.SetPosition(pcbnew.wxPoint(pos_a[0] + mm_to_nm(relative_x), pos_a[1] + mm_to_nm(relative_y)))    
        if justification <> None:
            if justification.lower() == 'left':
                justification = pcbnew.GR_TEXT_HJUSTIFY_LEFT
            elif justification.lower() == 'right':
                justification = pcbnew.GR_TEXT_HJUSTIFY_RIGHT
            elif justification.lower() == 'center':
                justification = pcbnew.GR_TEXT_HJUSTIFY_CENTER
            b.SetHorizJustify(justification)
    if not suppress_refresh:
        pcbnew.Refresh()

def place_component_value_position(component_name, relative_x, relative_y, justification = None):
    a = get_component(component_name)
    b = a.Value()
    pos_a = a.GetPosition()
    b.SetPosition(pcbnew.wxPoint(pos_a[0] + mm_to_nm(relative_x), pos_a[1] + mm_to_nm(relative_y)))    
    if justification <> None:
        if justification.lower() == 'left':
            justification = pcbnew.GR_TEXT_HJUSTIFY_LEFT
        elif justification.lower() == 'right':
            justification = pcbnew.GR_TEXT_HJUSTIFY_RIGHT
        elif justification.lower() == 'center':
            justification = pcbnew.GR_TEXT_HJUSTIFY_CENTER
        b.SetHorizJustify(justification)
    pcbnew.Refresh()

#Moves the value to the silkscreen layer. Say you want to decorate your PCB with all your resistor values
#Example: 
#for r in get_wildcard_component_names('R*'):
#    place_component_value_to_silk_layer(r)
def place_component_value_to_silk_layer(component_name):
    layers = [pcb.GetLayerName(l) for l in pcb.GetLayerSet().AllLayersMask().Seq()]
    c = get_component(component_name)
    c.Value().SetLayer(layers.index(c.GetLayerName().replace('.Cu', '.SilkS')))
    pcbnew.Refresh()

#Lock and unlock track functions. Useful if you're going to run an external autorouter and want to be able to delete all the tracks that it routed. 
def lock_tracks_with_signal_name(signal_names_list, min_width_mm = 0):
    signal_tracks = [t for t in pcb.GetTracks() if t.GetNetname() in signal_names_list and t.GetWidth() >= mm_to_nm(min_width_mm)]
    for st in signal_tracks:
        st.SetLocked(True)
    pcbnew.Refresh()

def unlock_tracks_with_signal_name(signal_names_list, min_width_mm = 0):
    signal_tracks = [t for t in pcb.GetTracks() if t.GetNetname() in signal_names_list and t.GetWidth() >= mm_to_nm(min_width_mm)]
    for st in signal_tracks:
        st.SetLocked(False)
    pcbnew.Refresh()

'''Use this to lock down all hand routed tracks before going to autoroute'''
def lock_all_tracks(min_width_mm = 0):
    signal_tracks = [t for t in pcb.GetTracks() if t.GetWidth() >= mm_to_nm(min_width_mm)]
    for st in signal_tracks:
        st.SetLocked(True)
    pcbnew.Refresh()
    
'''
select_all_areas: Useful for selecting areas if you have to move them all off board so freerouting can work
'''
def select_all_areas():
    for i in range(pcb.GetAreaCount()):
        a = pcb.GetArea(i)
        a.SetSelected()
    pcbnew.Refresh()

'''Creates a text element, does not place it'''
def create_text_element(text, justification = None):
    te = pcbnew.TEXTE_PCB(pcb)
    #te.SetPosition (pcbnew.wxPoint(x,y))
    #te.SetLayer (pcbnew.F_SilkS)
    te.SetVisible (True)
    te.SetThickness (mm_to_nm(.1524))
    te.SetText (text)
    if justification <> None:
        if justification.lower() == 'left':
            justification = pcbnew.GR_TEXT_HJUSTIFY_LEFT
        elif justification.lower() == 'right':
            justification = pcbnew.GR_TEXT_HJUSTIFY_RIGHT
        elif justification.lower() == 'center':
            justification = pcbnew.GR_TEXT_HJUSTIFY_CENTER
        te.SetHorizJustify(justification)
    return te

#This dumps a legend of component names and values for silk screen on the top or bottom layer. 
#I use this while hand assembling PCBs so I don't have to keep going back to my layout or print a separate BOM for assembly. 
'''Creates a legend for component names/values to put on the silkscreen layer. Mirror it in the UI to put it on the back of the PCB'''
def bom_value_legend(x, y, footprints_to_ignore = [], bottom_silk = False):
    all_names = get_all_component_names()
    l = []
    for f in footprints_to_ignore:
        l.extend([n for n in get_wildcard_component_names(f, all_names) if n not in l])
    footprints_to_ignore = l

    all_names = [n for n in all_names if n not in footprints_to_ignore]
    all_names.sort()

    footprints_to_ignore.sort()
    for f in footprints_to_ignore:
        print 'Ignoring: %s' % f

    names = []
    values = []
    column_width = 0
    row_height = 0
    for n in all_names:
        te = create_text_element(n, 'right')
        if bottom_silk:
            te.SetLayer(pcbnew.B_SilkS)
            te.SetMirrored(True)
        else:
            te.SetLayer(pcbnew.F_SilkS)
        #print n
        names.append(te)
        column_width = max(column_width, te.GetBoundingBox().GetWidth())
        row_height = max(row_height, te.GetBoundingBox().GetHeight())

        v = get_component(n).Value().GetText()
        #print v
        te = create_text_element(v, 'left')
        if bottom_silk:
            te.SetLayer(pcbnew.B_SilkS)
            te.SetMirrored(True)
        values.append(te)
        column_width = max(column_width, te.GetBoundingBox().GetWidth())
        row_height = max(row_height, te.GetBoundingBox().GetHeight())

    offset = mm_to_nm(1)
    if bottom_silk:
        offset *= -1
    x,y = mm_to_nm(x),mm_to_nm(y)
    for i in range(len(names)):
        names[i].SetPosition(pcbnew.wxPoint(x, y + i * row_height))

        values[i].SetPosition(pcbnew.wxPoint(x + offset, y + i * row_height))
        
        pcb.Add(names[i])
        pcb.Add(values[i])

    #Doesn't work correctly. Requires you to select and then deselect to do anything
    #for n in names:
    #    n.SetSelected()
    #for v in values:
    #    v.SetSelected()
    pcbnew.Refresh()