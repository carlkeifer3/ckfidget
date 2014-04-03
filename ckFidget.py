"""
    ckFidget.py

    written by: Carl Keifer

    This tool allows users to modify sets of data while tracking revisions. it can
    operate on a set of data channels by increment or percent. fidget data is stored
    in a group node so that it persists from save to save.

    CK - then I need to get it working cleanly once and for all.
         currently the tool only works for mel based windows.
         it would be great to do the same thing with QT.

"""
import maya.OpenMayaUI as apiUI
import sip
import sys
import pymel.all as pm

# I should create an initialize fidget function that can load persistent data from
# a previous fidget session.

# contains a list of  "object.attribute" that we will be working with
ckFidgetList = []
# contains a list of saved values for a single step
ckFidgetSav = []
# contains the value listed in the attribute when entered onto the list
ckFidgetPrim = []

# this is the amount by default that will be affecting the attributes
pm.melGlobals.initVar( 'float','gckFidgetBump')
pm.melGlobals['gckFidgetBump'] = 0.1

def ckFidgetInit():
    """
        ckFidgetInit()

        description: this function should initialize ckFidget
            it should check for existing persistent data
            and create a new node if none exists
            then it creates the interface

        inputs: None

        outputs: initializes ckFidget
    """
    try:
        print "checking for persistent fidget data"
        pm.select("ckFidget_GRP")
        isFidget = pm.getAttr("ckFidget_GRP.ckIsFidget")
        if isFidget == True:
            print "Data Found!"
            ckList = pm.getAttr("ckFidget_GRP.ckFidgetList")
            ckList = ckList.split(";")
            ckSav = pm.getAttr("ckFidget_GRP.ckFidgetSav")
            ckSav = ckSav.split(";")
            ckPrim = pm.getAttr("ckFidget_GRP.ckFidgetPrim")
            ckPrim = ckPrim.split(";")
            i = 0
            while i < len(ckList)-1:
                print "appending ckFidgetList with " + str(ckList[i])
                ckFidgetList.append( ckList[i] )
                ckFidgetSav.append( float(ckSav[i]) )
                ckFidgetPrim.append( float(ckPrim[i]) )
                i = i + 1
            print ckFidgetSav
            print ckFidgetPrim
            pm.setAttr("ckFidget_GRP.bumpBy", False)
    except:
        print "data not found initializing new ckFidget instance"
        pm.group(empty=True, name="ckFidget_GRP")
        pm.addAttr( longName="ckIsFidget", attributeType='bool', keyable=False )
        pm.setAttr("ckFidget_GRP.ckIsFidget", True)
        pm.addAttr( longName="bumpBy", attributeType='bool', keyable=False )
        pm.setAttr("ckFidget_GRP.bumpBy", False)
        pm.addAttr( longName="ckFidgetBump", attributeType='float', keyable=False, defaultValue=0.1 )

        print "here is where I should ask about starting a new fidget"
        pm.addAttr( longName="ckFidgetList", dataType='string', keyable=False )
        pm.addAttr( longName="ckFidgetSav", dataType='string', keyable=False )
        pm.addAttr( longName="ckFidgetPrim", dataType='string', keyable=False )
        pm.setAttr( "ckFidget_GRP.ckFidgetList","" )
        pm.setAttr( "ckFidget_GRP.ckFidgetSav","" )
        pm.setAttr( "ckFidget_GRP.ckFidgetPrim","" )
    ckFidgetWin()

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
    ckList = pm.getAttr("ckFidget_GRP.ckFidgetList")
    ckList = ckList + newAttr + ";"
    pm.setAttr("ckFidget_GRP.ckFidgetList", ckList )
    ckFidgetSav.append( newVal )
    ckSav = pm.getAttr("ckFidget_GRP.ckFidgetSav")
    ckSav = ckSav + str(newVal) + ";"
    pm.setAttr("ckFidget_GRP.ckFidgetSav", ckSav )
    ckFidgetPrim.append( newVal )
    ckPrim = pm.getAttr("ckFidget_GRP.ckFidgetPrim")
    ckPrim = ckPrim + str(newVal) + ";"
    pm.setAttr("ckFidget_GRP.ckFidgetPrim", ckPrim )

    # printing the saved data as a check

    #CK - I should clean this up it looks terrible and is not usefull for editing
    print ckFidgetSav
    print ckFidgetList

    # now issue the call to rebuild the interface
    ckFidgetWin()
    
def ckFidgetBumpAllUp(bumpBy):
    """
        ckFidgetBumpAllUp( bumpBy )

        description: adjusts list of attributes up ( adds to ) by percentage or increment

        inputs:
            bumpBy: indicates percentage or increment

        outputs: all attributes in fidget set are adjusted

    """
    print "bumping all up "
    for i in ckFidgetList: 
        ckFidgetBumpUp( i, bumpBy)
        
def ckFidgetBumpAllDwn(bumpBy):
    """
        ckFidgetBumpAllUp( bumpBy )

        description: adjusts list of attributes down ( subtracts from ) by
            percentage or increment

        inputs:
            bumpBy: indicates percentage or increment

        outputs: all attributes in fidget set are adjusted

    """
    print "bumping all down"
    for i in ckFidgetList:
        ckFidgetBumpDwn( i, bumpBy)
     
def ckFidgetBumpDwn(bumpAttr, bumpBy):
    """
        ckFidgetBumpDwn( bumpAttr, bumpBy )

        description: adjusts single attribute down ( subtracts from )
            by percentage or increment

        inputs:
            bumpBy: indicates percentage or increment

            bumpAttr: the attribute to be adjusted

        outputs: adjusts attribute named in bumpAttr

    """
    print "bumping down", bumpAttr
    # bumping by percentage, figure out percentage and adjust attribute
    if(bumpBy == True):
        print " by percent"
        bumpAmt = pm.melGlobals.get('gckFidgetBump') / 100
        bumpAmt = pm.getAttr( bumpAttr ) - bumpAmt 
    # bumping by integer value, get value and adjust attribute
    else:
        print " by integer"
        bumpAmt = pm.melGlobals.get('gckFidgetBump') * -1
        bumpAmt = bumpAmt + pm.getAttr( bumpAttr )
    # store adjustment
    pm.setAttr( bumpAttr, bumpAmt)

def ckFidgetBumpUp(bumpAttr, bumpBy):
    """
        ckFidgetBumpDwn( bumpAttr, bumpBy )

        description: adjusts single attribute up ( adds to ) by percentage or increment

        inputs:
            bumpBy: indicates percentage or increment

            bumpAttr: the attribute to be adjusted

        outputs: adjusts attribute named in bumpAttr

    """
    print "bumping up ", bumpAttr 
    # bumping by percentage, figure out percentage and adjust attribute
    if(bumpBy == True):
        print " by percent"
        bumpAmt = pm.melGlobals.get('gckFidgetBump') / 100
        bumpAmt = bumpAmt + pm.getAttr( bumpAttr )
    # bumping by integer value, get value and adjust attribute
    else:
        print " by integer"
        bumpAmt = pm.melGlobals.get('gckFidgetBump') + pm.getAttr( bumpAttr )
    print bumpAmt
    # store adjustment
    pm.setAttr( bumpAttr, bumpAmt)

def ckSaveAll():
    """
        ckSaveAll( )

        description: iterates list of currently active attributes to store
            all values current state


        inputs: None

        outputs: saves current state of all fidget attributes

    """
    print "restoring all default values"
    for i in ckFidgetList:
        ckFidgetSave(i)

def ckFidgetSave(saveAttr):
    """
        ckFidgetSave( saveAttr )

        description: stores the value listed in a single attribute

        inputs:
            saveAttr: the attribute whose value we will store

        outputs: stores the value currently listed at the saveAttr attribute

    """
    print "saving entry for, ", saveAttr
    i = ckFidgetList.index( saveAttr )
    ckFidgetSav[i] = pm.getAttr( saveAttr )

def ckZeroAll():
    """
        ckZeroAll()

        description: sets all active fidget attributes to zero

        inputs: None

        outputs: resets all active fidget attributes to zero
    """
    print "Zeroing all default values"
    for i in ckFidgetList:
            pm.setAttr(i, 0)

def ckRestoreAll():
    """
        ckRestoreAll()

        description: sets all active fidget attributes to their original value

        inputs: None

        outputs: sets all active fidget attributes to their original value

    """
    print "restoring all default values"
    for i in ckFidgetList:
        ckFidgetRestore(i)
        
def ckFidgetRestore(restoreAttr):
    """
        ckFidgetRestore( restoreAttr)

        description: restores single fidget attribute listed in restoreAttr
            to its starting value

        inputs:
            restoreAttr: the attribute whose value will be reset to it's starting
                value

        outputs: restores single fidget attribute listed in restoreAttr
            to its starting value

    """
    print "restoring saved value"
    # need to locate the restoreVal by searching the fidget list
    i = ckFidgetList.index( restoreAttr )
    restoreVal = ckFidgetSav[i]
    pm.setAttr( restoreAttr, restoreVal)
   
def ckFidgetWin():
    """
        ckFidgetWin()

        description: creates interface for ckFidget tool. the list is built dynamically
            from the list of active fidgets on load, so the more fidgets you add. the
            longer the tool window will become.

        inputs:

        outputs: the main fidget window.

        CK - I should add some menus to this that have basic falloffs
         for common tasks, like cloth, sss, or lighting.

    """
    if pm.mel.eval('window -ex "fidgetMainWin" ;'):
        pm.mel.eval('deleteUI "fidgetMainWin";' )
    fidgetWin = pm.mel.eval('window -title "attribute fidgeter" -width 150 fidgetMainWin;')
    pm.columnLayout( adjustableColumn=True )
    pm.frameLayout( label = "Build Fidget", borderStyle='in', collapsable=True )
    pm.rowLayout( numberOfColumns=5, columnWidth=(75,75) )
    pm.button( label = 'Add Fidget', command = 'ckAddFidget()' )
    pm.button( label = 'refresh UI', command = 'ckFidget()' )
    pm.button( label = 'Save All', command = 'ckSaveAll()')
    pm.button( label = 'Zero All', command = 'ckZeroAll()')
    pm.button( label = 'Restore All', command = 'ckRestoreAll()')
    pm.setParent( '..' )
    pm.setParent( '..' )
    pm.frameLayout( label = "Master Fidget", borderStyle='in', collapsable=True )
    pm.rowLayout( numberOfColumns=6, columnWidth=(75,75) )
    pm.mel.eval( 'floatField -value $gckFidgetBump -min 0 -changeCommand "$gckFidgetBump = `floatField -q -v  masterBump`"  masterBump;' )
    pm.button( label = '<', command = 'ckFidgetBumpAllDwn( pm.getAttr("ckFidget_GRP.bumpBy"))')
    pm.button( label = '>', command = 'ckFidgetBumpAllUp( pm.getAttr("ckFidget_GRP.bumpBy"))')
    pm.radioButtonGrp( label='Bump by:', labelArray2=['0.0', '%'], numberOfRadioButtons=2, sl=1, on1= 'pm.setAttr("ckFidget_GRP.bumpBy", False)', on2= 'pm.setAttr("ckFidget_GRP.bumpBy", True)')
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
        pm.rowLayout( numberOfColumns=6, columnWidth=(75,75) )
        pm.attrFieldSliderGrp( l=ckFidgetList[e], min=-10.0, max=10.0, at = i )
        pm.button( label = '<', command = 'ckFidgetBumpDwn(\"'+i+'\", pm.getAttr("ckFidget_GRP.bumpBy"))' )
        pm.button( label = '>', command = 'ckFidgetBumpUp( \"'+i+'\", pm.getAttr("ckFidget_GRP.bumpBy"))' )
        pm.button( label = 'save', command = 'ckFidgetSave( \"'+i+'\")')
        pm.button( label = 'zero', command = 'pm.setAttr( \"'+i+'\", 0)' )
        pm.button( label = 'restore', command = 'ckFidgetRestore( \"'+i+'\")')
        pm.setParent( '..' )
        e += 1
    pm.setParent( '..' )
    pm.setParent( '..' )
    pm.showWindow(fidgetWin)
    # I should now connect the master fidget value to the fidget group