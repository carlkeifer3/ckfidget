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

# this is the amount by default that will be affecting the attributes
pm.melGlobals.initVar( 'float','gckFidgetBump')
pm.melGlobals['gckFidgetBump'] = 0.1

def ckGetList( fdgAttr ):
    """
        ckGetList( fdgAttr )

        description: returns list from the fidget data
            assumes list always ends with ;

        inputs:
            fdgAttr: the object.attribute that we will be looking for data in

        outputs: returns list of data that lives in fdgAttr
    """
    ckList = pm.getAttr(fdgAttr)
    ckList =  ckList.split(";")
    ckList.pop()
    return ckList

def ckAddToList(fdgAttr, fdgVal):
    """
        ckAddToList(fdgAttr, fdgVal):

        description: adds value in fdgVal to the list located at fdgAttr
            assumes the list always ends with ;

        inputs:
            fdgAttr: the object.attribute that we will be looking for data in

            fdgVal: the data we will be adding to the list

        outputs: None
    """
    ckAttr = pm.getAttr(fdgAttr)
    ckAttr = ckAttr + str(fdgVal) + ";"
    pm.setAttr(fdgAttr, ckAttr )

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
        # should pop up a dialog and ask the name of the new fidget
        pm.addAttr( longName="ckFidgetList", dataType='string', keyable=False )
        pm.addAttr( longName="ckFidgetSav", dataType='string', keyable=False )
        pm.setAttr( "ckFidget_GRP.ckFidgetList","" )
        pm.setAttr( "ckFidget_GRP.ckFidgetSav","" )
    ckFidgetWin()

def ckAddFidget():
    """
        ckAddFidget( )

        description: this function collects the selected attribute and adds it
          to the list of data that fidget will work with

        inputs: None

        outputs: None

        CK - this would be a great place to add data to a persistent node in the
        maya file(working)
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
    ckAddToList( "ckFidget_GRP.ckFidgetList", newAttr)
    ckAddToList( "ckFidget_GRP.ckFidgetSav", newVal)
    # now issue the call to rebuild the interface
    ckFidgetWin()

def ckFidgetBumpAll(bumpDir):
    """
        ckFidgetBumpAll(bumpDir)

        description: evaluates list of fidgets

        inputs:
            bumpDir: determines if the operation is add or subtract

        outputs: None
    """
    print "bumping all fidgets " + str(bumpDir)
    ckList = ckGetList("ckFidget_GRP.ckFidgetList")
    for fdg in ckList:
        ckFidgetBump(fdg, bumpDir)

def ckFidgetBump( fdgAttr, bumpDir):
    """
        ckFidgetBump( fdgAttr, bumpDir )

        description: evaluates fidget for given attribute, adds or subtracts
            by percent or increment

        inputs:
            fdgAttr: the object.attribute that we will be looking for data in

            bumpDir: determines if the operation is add or subtract

        outputs: None

    """
    print "bumping " + str(bumpDir)+ " " + str(fdgAttr)
    bumpBy = pm.getAttr("ckFidget_GRP.bumpBy")
    fdgVal = pm.getAttr( fdgAttr )
    bumpAmt = pm.melGlobals.get('gckFidgetBump')
    # bumping by percentage, figure out percentage and adjust fdgVal attribute
    if(bumpBy == True):
        print " by percent"
        bumpAmt = bumpAmt / 100
        bumpAmt = fdgVal * bumpAmt
    if bumpDir == "Up":
        fdgVal = fdgVal + bumpAmt
    else:
        fdgVal = fdgVal - bumpAmt
    # store adjustment
    pm.setAttr( fdgAttr, fdgVal)

def ckSavRstZerAll( fdgOps ):
    """
        ckSavRstZerAll( fdgAttr, fdgOps )

        description: saves, restores, or zeros all attributes listed in fidget set.

        inputs:
            fdgOps: the operation to complete, save or restore

        outputs: None
    """
    print fdgOps + "ing all fidgets in dataset"
    ckList = ckGetList("ckFidget_GRP.ckFidgetList")
    for fdg in ckList:
        if fdgOps == "save":
            ckSavRst(fdg, fdgOps)
        elif fdgOps == "restore":
            ckSavRst(fdg, fdgOps)
        else:
            pm.setAttr(fdg, 0)

def ckSavRst(fdgAttr, fdgOps ):
    """
        ckSavRst()

        description: saves or restores values from fidget data

        inputs:
            fdgAttr: the object.attribute pair we will be working with

            fdgOps: the operation to complete, save or restore

        outputs: None

    """
    print str(fdgOps) + "ing entry for, ", fdgAttr
    fdgList = ckGetList( "ckFidget_GRP.ckFidgetList" )
    fdgSav = ckGetList( "ckFidget_GRP.ckFidgetSav" )
    i = 0
    for fdg in fdgList:
        print fdg + ";" + fdgSav[i]
        if fdg == fdgAttr:
            break
        i = i +1
    if fdgOps == "save":
        fdgSav[i] = pm.getAttr(fdgAttr)
        newSav = ""
        for sav in fdgSav:
            newSav = newSav + str(sav) + ";"
        pm.setAttr("ckFidget_GRP.ckFidgetSav", newSav)
    else:

        pm.setAttr(fdgAttr, float(fdgSav[i]))

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
    fidgetWin = pm.mel.eval('window -title "Carl Keifer attribute fidgeter" -width 150 fidgetMainWin;')
    pm.columnLayout( adjustableColumn=True )
    pm.frameLayout( label = "Build Fidget", borderStyle='in', collapsable=True )
    pm.rowLayout( numberOfColumns=5, columnWidth=(75,75) )
    pm.button( label = 'Add Fidget', command = 'ckAddFidget()' )
    pm.button( label = 'refresh UI', command = 'ckFidget()' )
    pm.button( label = 'Save All', command = 'ckSavRstZerAll( "save" )')
    pm.button( label = 'Zero All', command = 'ckSavRstZerAll( "zero" )')
    pm.button( label = 'Restore All', command = 'ckSavRstZerAll( "restore" )')
    pm.setParent( '..' )
    pm.setParent( '..' )
    pm.frameLayout( label = "Master Fidget", borderStyle='in', collapsable=True )
    pm.rowLayout( numberOfColumns=6, columnWidth=(75,75) )
    pm.mel.eval( 'floatField -value $gckFidgetBump -min 0 -changeCommand "$gckFidgetBump = `floatField -q -v  masterBump`"  masterBump;' )
    pm.button( label = '<', command = 'ckFidgetBumpAll("Down")')
    pm.button( label = '>', command = 'ckFidgetBumpAll("Up")')
    pm.radioButtonGrp( label='Bump by:', labelArray2=['0.0', '%'], numberOfRadioButtons=2, sl=1, on1= 'pm.setAttr("ckFidget_GRP.bumpBy", False)', on2= 'pm.setAttr("ckFidget_GRP.bumpBy", True)')
    pm.setParent( '..' )
    pm.setParent( '..' )
    pm.frameLayout( label = "Fidget Attributes", borderStyle='in', collapsable=True )
    e = 0
    # this iterates the list of fidgets we have
    ckList = ckGetList("ckFidget_GRP.ckFidgetList")
    for i in ckList:
        print "i, ",i
        pm.rowLayout( numberOfColumns=6, columnWidth=(75,75) )
        pm.attrFieldSliderGrp( l=str(i), min=-10.0, max=10.0, at = i )
        pm.button( label = '<', command = 'ckFidgetBump(\"'+i+'\", "Down")' )
        pm.button( label = '>', command = 'ckFidgetBump( \"'+i+'\","Up")' )
        pm.button( label = 'save', command = 'ckSavRst( \"'+i+'\", "save")')
        pm.button( label = 'zero', command = 'pm.setAttr( \"'+i+'\", 0)' )
        pm.button( label = 'restore', command = 'ckSavRst( \"'+i+'\", "restore")')
        pm.setParent( '..' )
    pm.setParent( '..' )
    pm.setParent( '..' )
    pm.showWindow(fidgetWin)
    # I should now connect the master fidget value to the fidget group