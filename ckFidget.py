####################
##
##   ckfidget.py
##   written by Carl Keifer
##
## fidget allows the user to collect single attributes from multiple
## objects on one interface and adjust values by increment or percentage
#####################


import sys
import pymel.all as pm

ckFidgetList = []
ckFidgetSav = []
ckFidgetPrim = []
pm.melGlobals.initVar( 'float','gckFidgetBump')
pm.melGlobals['gckFidgetBump'] = 0.1

def ckAddFidget():
    atribSel = pm.mel.eval('selectedChannelBoxAttributes();')
    slectItm = pm.ls( selection = True )
    newAttr =  slectItm.pop() + '.' + atribSel.pop()
    newVal = pm.getAttr( newAttr )
    print newVal
    ckFidgetList.append( newAttr )
    ckFidgetSav.append( newVal )
    ckFidgetPrim.append( newVal )
    print ckFidgetSav
    print ckFidgetList
    ckFidget()
    
def ckFidgetBumpAllUp(bumpBy):
    print "bumping all up "
    for i in ckFidgetList: 
        ckFidgetBumpUp( i, bmpBy)
        
def ckFidgetBumpAllDwn(bmpBy):
    print "bumping all down"
    for i in ckFidgetList:
        ckFidgetBumpDwn( i, bmpBy)
     
def ckFidgetBumpDwn(bumpAttr, bmpBy):
    print "bumping down", bumpAttr
    if(bmpBy == True):
        print " by percent"
        bumpAmt = pm.melGlobals.get('gckFidgetBump') / 100
        bumpAmt = pm.getAttr( bumpAttr ) - bumpAmt 
    else:
        print " by integer"
        bumpAmt = pm.melGlobals.get('gckFidgetBump') * -1
        bumpAmt = bumpAmt + pm.getAttr( bumpAttr )
    pm.setAttr( bumpAttr, bumpAmt)

def ckFidgetBumpUp(bumpAttr, bumpBy):
    print "bumping up ", bumpAttr 
    if(bmpBy == True):
        print " by percent"
        bumpAmt = pm.melGlobals.get('gckFidgetBump') / 100
        bumpAmt = bumpAmt + pm.getAttr( bumpAttr )
    else:
        print " by integer"
        bumpAmt = pm.melGlobals.get('gckFidgetBump') + pm.getAttr( bumpAttr )
    print bumpAmt
    pm.setAttr( bumpAttr, bumpAmt)

def ckSaveAll():
    print "restoring all default values"
    for i in ckFidgetList:
        ckFidgetSave(i)

def ckFidgetSave(saveAttr):
    print "saving entry for, ", saveAttr
    i = ckFidgetList.index( saveAttr )
    ckFidgetSav[i] = pm.getAttr( saveAttr )

def ckRestoreAll():
    print "restoring all default values"
    for i in ckFidgetList:
        ckFidgetRestore(i)
        
def ckFidgetRestore(restoreAttr):
    print "restoring saved value"
    # need to locate the restoreVal by searching the fidget list
    i = ckFidgetList.index( restoreAttr )
    restoreVal = ckFidgetSav[i]
    pm.setAttr( restoreAttr, restoreVal)
   
def ckFidget():
    if pm.mel.eval('window -ex "fidgetMainWin" ;'):
        pm.mel.eval('deleteUI "fidgetMainWin";' )
    fidgetWin = pm.mel.eval('window -title "attribute fidgeter" -width 200 fidgetMainWin;')
    pm.columnLayout( adjustableColumn=True )
    pm.frameLayout( label = "Build Fidget", borderStyle='in', collapsable=True )
    pm.rowLayout( numberOfColumns=4, columnWidth=(75,75) )
    pm.button( label = 'Add Fidget', command = 'ckAddFidget()' )
    pm.button( label = 'refresh UI', command = 'ckFidget()' )
    pm.button( label = 'Save All', command = 'ckSaveAll()')
    pm.button( label = 'Restore All', command = 'ckRestoreAll()')
    pm.setParent( '..' )
    pm.setParent( '..' )
    pm.frameLayout( label = "Master Fidget", borderStyle='in', collapsable=True )
    pm.rowLayout( numberOfColumns=6, columnWidth=(75,75) )
    pm.mel.eval( 'floatField -value $gckFidgetBump -min 0 -changeCommand "$gckFidgetBump = `floatField -q -v masterBump`" masterBump;' )
    pm.button( label = '<', command = 'ckFidgetBumpAllDwn( bmpBy)')
    pm.button( label = '>', command = 'ckFidgetBumpAllUp( bmpBy)')
    bmpBy = False
    pm.radioButtonGrp( label='Bump by:', labelArray2=['0.0', '%'], numberOfRadioButtons=2, sl=2, on1= 'bmpBy=False', on2= 'bmpBy=True')
    pm.setParent( '..' )
    pm.setParent( '..' )
    pm.frameLayout( label = "Fidget Attributes", borderStyle='in', collapsable=True )
    e = 0
    for i in ckFidgetList:
        print "i, ",i
        print "e, ",e
        print "stored Save, ", ckFidgetSav[e]
        currentName = i.split('.')
        print currentName
        pm.rowLayout( numberOfColumns=7, columnWidth=(75,75) )
        pm.text( label = currentName[0])
        pm.attrFieldSliderGrp( min=-10.0, max=10.0, at = i )
        pm.button( label = '<', command = 'ckFidgetBumpDwn(\"'+i+'\", bmpBy)' )
        pm.button( label = '>', command = 'ckFidgetBumpUp( \"'+i+'\", bmpBy)' )
        pm.button( label = 'save', command = 'ckFidgetSave( \"'+i+'\")')
        pm.button( label = 'zero', command = 'pm.setAttr( \"'+i+'\", 0)' )
        pm.button( label = 'restore', command = 'ckFidgetRestore( \"'+i+'\")')
        pm.setParent( '..' )
        e += 1
    pm.setParent( '..' )
    pm.setParent( '..' )
    pm.showWindow(fidgetWin)
    
ckFidget()