"""
    ckFidget.py

    written by: Carl Keifer

    This tool allows users to modify sets of data while tracking revisions. it can
    operate on a set of data channels by increment or percent.

    CK - I need to go through this and clean up the comments first
         then I need to get it working cleanly once and for all.
         extension of the tool to include storage of revisions.
         currently the tool only works for mel based windows.
         it would be great to do the same thing with QT.

"""
#from PyQt4 import QtGui, QtCore, uic
import maya.OpenMayaUI as apiUI
import sip
import sys
import pymel.all as pm

# contains a list of  "object.attribute" that we will be working with
ckFidgetList = []
# contains a list of saved values for a single step
ckFidgetSav = []
# contains the value listed in the attribute when entered onto the list
ckFidgetPrim = []

# this is the amount by default that will be affecting the attributes
pm.melGlobals.initVar( 'float','gckFidgetBump')
pm.melGlobals['gckFidgetBump'] = 0.1

def ckAddFidget():
    """
        ckAddFidget( )

        description: this function collects the selected attribute and adds it
          to the list of data that fidget will work with

        inputs: None

        outputs: rebuilds the interface including the added attribute

        CK - this would be a great place to add data to a persistent node in the
        maya file
    """

    # fist we are collecting the selected attribute
    atribSel = pm.mel.eval('selectedChannelBoxAttributes();')
    # then we get the object said attribute belongs to
    slectItm = pm.ls( selection = True )
    # the two are added together so we can work with the information
    # inside the maya context
    newAttr =  slectItm.pop() + '.' + atribSel.pop()

    # this is a test to ensure that we are in fact getting some kind of data from
    # the attribute
    newVal = pm.getAttr( newAttr )
    print newVal

    # given that has worked  we will add the data to the lists
    ckFidgetList.append( newAttr )
    ckFidgetSav.append( newVal )
    ckFidgetPrim.append( newVal )

    # printing the saved data as a check

    #CK - I should clean this up it looks terrible and is not usefull for editing
    print ckFidgetSav
    print ckFidgetList

    # now issue the call to rebuild the interface
    ckFidgetWin()
    
def ckFidgetBumpAllUp(bumpBy):
    """
        ckFidgetBumpAllUp( bumpBy )

        description: this function iterates the list of attributes and increments them
           using the value bumpBy

        inputs:
            bumpBy:

        outputs:

    """
    print "bumping all up "
    for i in ckFidgetList: 
        ckFidgetBumpUp( i, bumpBy)
        
def ckFidgetBumpAllDwn(bumpBy):
    """
        ckFidgetBumpAllUp( bumpBy )

        description: this function iterates the list of attributes and increments them
           using the value bumpBy

        inputs:
            bumpBy:

        outputs:

    """
    print "bumping all down"
    for i in ckFidgetList:
        ckFidgetBumpDwn( i, bumpBy)
     
def ckFidgetBumpDwn(bumpAttr, bumpBy):
    """
        ckFidgetBumpAllUp( bumpBy )

        description: this function iterates the list of attributes and increments them


        inputs:
            bumpBy:

        outputs:

    """
    print "bumping down", bumpAttr
    if(bumpBy == True):
        print " by percent"
        bumpAmt = pm.melGlobals.get('gckFidgetBump') / 100
        bumpAmt = pm.getAttr( bumpAttr ) - bumpAmt 
    else:
        print " by integer"
        bumpAmt = pm.melGlobals.get('gckFidgetBump') * -1
        bumpAmt = bumpAmt + pm.getAttr( bumpAttr )
    pm.setAttr( bumpAttr, bumpAmt)

def ckFidgetBumpUp(bumpAttr, bumpBy):
    """
        ckFidgetBumpAllUp( bumpBy )

        description: this function iterates the list of attributes and increments them
           using the value bumpBy

        inputs:
            bumpBy:

        outputs:

    """
    print "bumping up ", bumpAttr 
    if(bumpBy == True):
        print " by percent"
        bumpAmt = pm.melGlobals.get('gckFidgetBump') / 100
        bumpAmt = bumpAmt + pm.getAttr( bumpAttr )
    else:
        print " by integer"
        bumpAmt = pm.melGlobals.get('gckFidgetBump') + pm.getAttr( bumpAttr )
    print bumpAmt
    pm.setAttr( bumpAttr, bumpAmt)

def ckSaveAll():
    """
        ckFidgetBumpAllUp( bumpBy )

        description: this function iterates the list of attributes and increments them
           using the value bumpBy

        inputs:
            bumpBy:

        outputs:

    """
    print "restoring all default values"
    for i in ckFidgetList:
        ckFidgetSave(i)

def ckFidgetSave(saveAttr):
    """
        ckFidgetBumpAllUp( bumpBy )

        description: this function iterates the list of attributes and increments them
           using the value bumpBy

        inputs:
            bumpBy:

        outputs:

    """
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
   
def ckFidgetWin():
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
    pm.mel.eval( 'floatField -value $gckFidgetBump -min 0 -changeCommand "$gckFidgetBump = `floatField -q -v  masterBump`"  masterBump;' )
    pm.button( label = '<', command = 'ckFidgetBumpAllDwn( bumpBy)')
    pm.button( label = '>', command = 'ckFidgetBumpAllUp( bumpBy)')
    bumpBy = False
    pm.radioButtonGrp( label='Bump by:', labelArray2=['0.0', '%'], numberOfRadioButtons=2, sl=2, on1= 'bumpBy=False', on2= 'bumpBy=True')
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
        pm.button( label = '<', command = 'ckFidgetBumpDwn(\"'+i+'\", bumpBy)' )
        pm.button( label = '>', command = 'ckFidgetBumpUp( \"'+i+'\", bumpBy)' )
        pm.button( label = 'save', command = 'ckFidgetSave( \"'+i+'\")')
        pm.button( label = 'zero', command = 'pm.setAttr( \"'+i+'\", 0)' )
        pm.button( label = 'restore', command = 'ckFidgetRestore( \"'+i+'\")')
        pm.setParent( '..' )
        e += 1
    pm.setParent( '..' )
    pm.setParent( '..' )
    pm.showWindow(fidgetWin)

