import unreal
import os

def CreateBaseImportTask(importPath):
    importTask = unreal.AssetImportTast()
    importTask.filename = importPath

    
    fileName = os.path.basename(importPath).split('.')[0]
    importTask.destination_path = '/Game/' + fileName

    importTask.automated = True
    importTask.save = True
    importTask.replace_existing = True

    return importTask

def importSkeletalMesh(meshPath):
    importTask = CreateBaseImportTask(meshPath)

    importOption = unreal.FbxImportUI()
    importOption.import_mesh = True
    importOption.import_as_skeletal = True
    importOption.skeletal_mesh_import_data.set_editor_property('import_morph_targets', True)
    importOption.skeletal_mesh_import_data.set_editor_property('use_t0_ask_ref_pose', True)

    importTask.options = importOption

    unreal.AssetToolsHelper.get_asset_tool().import_asset_task([importTask])
    return importTask.get_objects()[-1]

def ImportAnimation(mesh: unreal.SkeletalMesh, animPath):
    importTask = CreateBaseImportTask(animPath)
    meshDir = os.path.dirname(mesh.get_path_name())
    importTask.destination_path = meshDir + "/animations"

    importOption = unreal.FbxImportUI()
    importOption.import_mesh = False
    importOption.import_as_skeletal = True
    importOption.import_animations = True
    importOption.skeleton = mesh.skeleton

    importOption.set_editor_property('automated_import_should_detect_type', False)
    importOption.set_editor_property('orginal_import_type', unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    importOption.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_ANIMATION)

    importTask.options = importOption

    unreal.AssetToolsHelper.get_asset_tool().import_asset_task([importTask])

def ImportMeshAndAnimations(meshPath, animDir):
    mesh = importSkeletalMesh(meshPath)
    print(mesh)

    for file in os.listdir(animDir):
        animPath = os.path.join(animDir, file)
        ImportAnimation(mesh, animPath)



ImportMeshAndAnimations("")

#what ever you names your file locations