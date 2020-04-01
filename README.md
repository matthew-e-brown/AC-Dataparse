# BlathersDB

In Animal Crossing: New Horizons, the friendly museum curator Blathers offers
fun facts for each new Fish, Insect, and Fossil you bring him. The only issue is
that you can only hear them whenever you bring one of these items to him. When
you're dealing with incredibly rare or out-of-season Fish for example, you will
probably never hear each commentary once.

That's where BlathersDB comes in! 

## Building

To be able to run the Python scripts that read through the games files and
create the database, you will need to extract the following files from the
*Animal Crossing: New Horizons'* `.XCI` either by using [Switch
Toolbox](https://github.com/KillzXGaming/Switch-Toolbox) or by some other means:
 - `romfs/Message/App.msbt`
 - `romfs/Message/TalkSNpc_{LANG}.sarc.zs/owl/SP_owl_Comment_Fish.msbt`
 - `romfs/Message/TalkSNpc_{LANG}.sarc.zs/owl/SP_owl_Comment_Fossil.msbt`
 - `romfs/Message/TalkSNpc_{LANG}.sarc.zs/owl/SP_owl_Comment_Insect.msbt`
 - `romfs/Message/String_{LANG}.sarc.zs/Item/STR_ItemName_30_Insect.msbt`
 - `romfs/Message/String_{LANG}.sarc.zs/Item/STR_ItemName_31_Fish.msbt`
 - `romfs/Message/String_{LANG}.sarc.zs/Item/STR_ItemName_34_Fossil.msbt`