# coding: utf-8
import os
import sys
import time
import functools

try:
    import bpy
    import mathutils
except:
    pass

FS_ENCODING=sys.getfilesystemencoding()
if os.path.exists(os.path.dirname(sys.argv[0])+"/utf8"):
    INTERNAL_ENCODING='utf-8'
else:
    INTERNAL_ENCODING=FS_ENCODING

def register():
    pass

def unregister():
    pass

SCENE=None
def initialize(name, scene):
    global SCENE
    SCENE=scene
    progress_start(name)

def finalize():
    scene.update(SCENE)
    progress_finish()

def message(msg):
    print(msg)

def enterEditMode():
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

def enterObjectMode():
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

def enterPoseMode():
    bpy.ops.object.mode_set(mode='POSE', toggle=False)

def createVector(x, y, z):
    return mathutils.Vector([x, y, z])


class Writer(object):
    '''
    io wrapper
    '''
    def __init__(self, path, encoding):
        self.io=open(path, "wb")
        self.encoding=encoding

    def write(self, s):
        self.io.write(s.encode(self.encoding))

    def flush(self):
        self.io.flush()

    def close(self):
        self.io.close()


class ProgressBar(object):
    '''
    progress bar wrapper
    '''
    def __init__(self, base):
        print("#### %s ####" % base)
        self.base=base
        self.start=time.time() 
        self.set('<start>', 0)

    def advance(self, message, progress):
        self.progress+=float(progress)
        self._print(message)

    def set(self, message, progress):
        self.progress=float(progress)
        self._print(message)

    def _print(self, message):
        print(message)
        message="%s: %s" % (self.base, message)
        #Blender.Window.DrawProgressBar(self.progress, message)

    def finish(self):
        self.progress=1.0
        message='finished in %.2f sec' % (time.time()-self.start)
        self.set(message, 1.0)

def progress_start(base):
    global progressBar
    progressBar=ProgressBar(base)

def progress_finish():
    global progressBar
    progressBar.finish()

def progress_print(message, progress=0.05):
    global progressBar
    progressBar.advance(message, progress)

def progress_set(message, progress):
    global progressBar
    progressBar.set(message, progress)


class scene:
    @staticmethod
    def get():
        global SCENE
        return SCENE

    def update(scene):
        scene.update()


class object:
    @staticmethod
    def createEmpty(name):
        global SCENE
        empty=bpy.data.objects.new(name, None)
        SCENE.objects.link(empty)
        return empty

    @staticmethod
    def each():
        for o in SCENE.objects:
            yield o

    @staticmethod
    def makeParent(parent, child):
        child.parent=parent

    @staticmethod
    def duplicate(o):
        global SCENE
        bpy.ops.object.select_all(action='DESELECT')
        o.select=True
        SCENE.objects.active=o
        bpy.ops.object.duplicate()
        dumy=SCENE.objects.active
        #bpy.ops.object.rotation_apply()
        #bpy.ops.object.scale_apply()
        #bpy.ops.object.location_apply()
        return dumy.data, dumy

    @staticmethod
    def delete(o):
        global SCENE
        SCENE.objects.unlink(o)

    @staticmethod
    def getData(o):
        return o.data

    @staticmethod
    def select(o):
        o.select=True

    @staticmethod
    def activate(o):
        global SCENE
        o.select=True 
        SCENE.objects.active=o

    @staticmethod
    def getActive():
        global SCENE 
        return SCENE.objects.active

    @staticmethod
    def deselectAll():
        bpy.ops.object.select_all(action='DESELECT')

    @staticmethod
    def setLayerMask(object, layers):
        layer=[]
        for i in range(20):
            try:
                layer.append(True if layers[i]!=0 else False)
            except IndexError:
                layer.append(False)
        object.layers=layer

    @staticmethod
    def isVisible(o):
        return False if o.hide else True

    @staticmethod
    def getShapeKeys(o):
        return o.data.shape_keys.key_blocks

    @staticmethod
    def addShapeKey(o, name):
        try:
            return o.shape_key_add(name)
        except:
            return o.add_shape_key(name)

    @staticmethod
    def hasShapeKey(o):
        return o.data.shape_keys

    @staticmethod
    def pinShape(o, enable):
        o.show_only_shape_key=enable

    @staticmethod
    def setActivateShapeKey(o, index):
        o.active_shape_key_index=index

    @staticmethod
    def getPose(o):
        return o.pose

    @staticmethod
    def getVertexGroup(o, name):
        indices=[]
        for i, v in enumerate(o.data.vertices):
            for g in v.groups:
                if o.vertex_groups[g.group].name==name:
                    indices.append(i)
        return indices

    @staticmethod
    def getVertexGroupNames(o):
        for g in o.vertex_groups:
            yield g.name

    @staticmethod
    def addVertexGroup(o, name):
        o.vertex_groups.new(name)

    @staticmethod
    def assignVertexGroup(o, name, index, weight):
        o.vertex_groups[name].add([index], weight, 'ADD')

    @staticmethod
    def createBoneGroup(o, name, color_set='DEFAULT'):
        # create group
        object.activate(o)
        enterPoseMode()
        bpy.ops.pose.group_add()
        # set name
        pose=object.getPose(o)
        g=pose.bone_groups.active
        g.name=name
        g.color_set=color_set

    @staticmethod
    def boneGroups(o):
        return object.getPose(o).bone_groups


class modifier:
    @staticmethod
    def addMirror(mesh_object):
        return mesh_object.modifiers.new("Modifier", "MIRROR")

    @staticmethod
    def addArmature(mesh_object, armature_object):
        mod=mesh_object.modifiers.new("Modifier", "ARMATURE")
        mod.object = armature_object
        mod.use_bone_envelopes=False

    @staticmethod
    def hasType(mesh_object, type_name):
        for mod in mesh_object.modifiers:
                if mod.type==type_name.upper():
                    return True

    @staticmethod
    def isType(m, type_name):
        return m.type==type_name.upper()

    @staticmethod
    def getArmatureObject(m):
        return m.object


class shapekey:
    @staticmethod
    def assign(shapeKey, index, pos):
        shapeKey.data[index].co=pos

    @staticmethod
    def getByIndex(b, index):
        return b.data[index].co

    @staticmethod
    def get(b):
        for k in b.data:
            yield k.co


class texture:
    @staticmethod
    def create(path):
        texture=bpy.data.textures.new(os.path.basename(path), 'IMAGE')
        texture.use_mipmap=True
        texture.use_interpolation=True
        texture.use_alpha=True
        try:
            image=bpy.data.images.load(path)
        except RuntimeError:
            image=bpy.data.images.new('Image', width=16, height=16)
        texture.image=image
        return texture, image

    @staticmethod
    def getPath(t):
        if  t.type=="IMAGE":
            image=t.image
            if image:
                return image.filepath


class material:
    @staticmethod
    def create(name):
        return bpy.data.materials.new(name)

    @staticmethod
    def get(material_name):
        return bpy.data.materials[material_name]

    @staticmethod
    def addTexture(material, texture, enable=True):
        # search free slot
        index=None
        for i, slot in enumerate(material.texture_slots):
            if not slot:
                index=i
                break
        if index==None:
            return
        #
        #material.add_texture(texture, "UV", "COLOR")
        #slot=material.texture_slots.add()
        slot=material.texture_slots.create(index)
        slot.texture=texture
        slot.texture_coords='UV'
        slot.blend_type='MULTIPLY'
        slot.use_map_alpha=True
        slot.use=enable
        return index

    @staticmethod
    def getTexture(m, index):
        return m.texture_slots[index].texture

    @staticmethod
    def hasTexture(m):
        return m.texture_slots[0]

    @staticmethod
    def setUseTexture(m, index, enable):
        m.use_textures[index]=enable

    @staticmethod
    def eachTexturePath(m):
        for slot in m.texture_slots:
            if slot and slot.texture:
                texture=slot.texture
                if  texture.type=="IMAGE":
                    image=texture.image
                    if not image:
                        continue
                    yield image.filepath

    @staticmethod
    def eachEnalbeTexturePath(m):
        for i, slot in enumerate(m.texture_slots):
            if m.use_textures[i] and slot and slot.texture:
                texture=slot.texture
                if  texture.type=="IMAGE":
                    image=texture.image
                    if not image:
                        continue
                    yield image.filepath


class mesh:
    @staticmethod
    def create(name):
        global SCENE
        mesh=bpy.data.meshes.new("Mesh")
        mesh_object= bpy.data.objects.new(name, mesh)
        SCENE.objects.link(mesh_object)
        return mesh, mesh_object

    @staticmethod
    def addGeometry(mesh, vertices, faces):
        mesh.from_pydata(vertices, [], faces)
        """
        mesh.add_geometry(len(vertices), 0, len(faces))
        # add vertex
        unpackedVertices=[]
        for v in vertices:
            unpackedVertices.extend(v)
        mesh.vertices.foreach_set("co", unpackedVertices)
        # add face
        unpackedFaces = []
        for face in faces:
            if len(face) == 4:
                if face[3] == 0:
                    # rotate indices if the 4th is 0
                    face = [face[3], face[0], face[1], face[2]]
            elif len(face) == 3:
                if face[2] == 0:
                    # rotate indices if the 3rd is 0
                    face = [face[2], face[0], face[1], 0]
                else:
                    face.append(0)
            unpackedFaces.extend(face)
        mesh.faces.foreach_set("verts_raw", unpackedFaces)
        """
        assert(len(vertices)==len(mesh.vertices))
        assert(len(faces)==len(mesh.faces))

    @staticmethod
    def hasUV(mesh):
        return len(mesh.uv_textures)>0

    @staticmethod
    def useVertexUV(mesh):
        pass

    @staticmethod
    def addUV(mesh):
        mesh.uv_textures.new()

    @staticmethod
    def hasFaceUV(mesh, i, face):
        active_uv_texture=None
        for t in mesh.uv_textures:
            if t.active:
                active_uv_texture=t
                break
        return active_uv_texture and active_uv_texture.data[i]

    @staticmethod
    def getFaceUV(mesh, i, faces, count=3):
        active_uv_texture=None
        for t in mesh.uv_textures:
            if t.active:
                active_uv_texture=t
                break
        if active_uv_texture and active_uv_texture.data[i]:
            uvFace=active_uv_texture.data[i]
            if count==3:
                return (uvFace.uv1, uvFace.uv2, uvFace.uv3)
            elif count==4:
                return (uvFace.uv1, uvFace.uv2, uvFace.uv3, uvFace.uv4)
            else:
                print(count)
                assert(False)
        else:
            return ((0, 0), (0, 0), (0, 0), (0, 0))

    @staticmethod
    def setFaceUV(m, i, face, uv_array, image):
        uv_face=m.uv_textures[0].data[i]
        uv_face.uv=uv_array
        if image:
            uv_face.image=image
            uv_face.use_image=True

    @staticmethod
    def vertsDelete(m, remove_vertices):
        enterEditMode()
        bpy.ops.mesh.select_all(action='DESELECT')
        enterObjectMode()

        for i in remove_vertices:
            m.vertices[i].select=True

        enterEditMode()
        bpy.ops.mesh.delete(type='VERT')
        enterObjectMode()

    @staticmethod
    def setSmooth(m, smoothing):
        m.auto_smooth_angle=int(smoothing)
        m.use_auto_smooth=True

    @staticmethod
    def recalcNormals(mesh_object):
        bpy.ops.object.select_all(action='DESELECT')
        object.activate(mesh_object)
        enterEditMode()
        bpy.ops.mesh.normals_make_consistent()
        enterObjectMode()

    @staticmethod
    def flipNormals(m):
        m.flipNormals()

    @staticmethod
    def addMaterial(m, material):
        m.materials.append(material)

    @staticmethod
    def getMaterial(m, index):
        return m.materials[index]


class vertex:
    @staticmethod
    def setNormal(v, normal):
        v.normal=mathutils.Vector(normal)

    @staticmethod
    def getNormal(v):
        return v.normal

    @staticmethod
    def setUv(v, uv):
        # sticky ?
        pass


class face:
    @staticmethod
    def getVertexCount(face):
        return len(face.vertices)

    @staticmethod
    def getVertices(face):
        return face.vertices[:]

    @staticmethod
    def getIndices(face, count=3):
        if count==3:
            return [face.vertices[0], face.vertices[1], face.vertices[2]]
        elif count==4:
            return [face.vertices[0], face.vertices[1], face.vertices[2], face.vertices[3]]
        else:
            assert(False)

    @staticmethod
    def setMaterial(face, material_index):
        face.material_index=material_index

    @staticmethod
    def getMaterialIndex(face):
        return face.material_index

    @staticmethod
    def setNormal(face, normal):
        face.normal=normal

    @staticmethod
    def getNormal(face):
        return face.normal

    @staticmethod
    def setSmooth(face, isSmooth):
        face.use_smooth=True if isSmooth else False


class armature:
    @staticmethod
    def create():
        global SCENE
        armature = bpy.data.armatures.new('Armature')
        armature_object=bpy.data.objects.new('Armature', armature)
        SCENE.objects.link(armature_object)

        armature_object.show_x_ray=True
        armature.show_names=True
        #armature.draw_type='OCTAHEDRAL'
        armature.draw_type='STICK'
        armature.use_deform_envelopes=False
        armature.use_deform_vertex_groups=True
        armature.use_mirror_x=True

        return armature, armature_object

    @staticmethod
    def makeEditable(armature_object):
        global SCENE
        # select only armature object and set edit mode
        SCENE.objects.active=armature_object
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    @staticmethod
    def createIkConstraint(armature_object, p_bone, effector_name, ik):
        constraint = p_bone.constraints.new('IK')
        constraint.chain_count=len(ik.children)
        constraint.target=armature_object
        constraint.subtarget=effector_name
        constraint.use_tail=False
        # not used. place folder when export.
        constraint.weight=ik.weight
        constraint.iterations=ik.iterations * 10
        return constraint

    @staticmethod
    def createBone(armature, name):
        return armature.edit_bones.new(name)

    @staticmethod
    def update(armature):
        pass


class bone:
    @staticmethod
    def setConnected(bone):
        bone.use_connect=True

    @staticmethod
    def isConnected(bone):
        return bone.use_connect

    @staticmethod
    def setLayerMask(bone, layers):
        layer=[]
        for i in range(32):
            try:
                layer.append(True if layers[i]!=0 else False)
            except IndexError:
                layer.append(False)
        bone.layers=layer

    @staticmethod
    def getHeadLocal(b):
        return b.head_local[0:3]

    @staticmethod
    def getTailLocal(b):
        return b.tail_local[0:3]


class constraint:
    @staticmethod
    def ikChainLen(c):
        return c.chain_count

    @staticmethod
    def ikTarget(c):
        return c.subtarget

    @staticmethod
    def ikItration(c):
        return c.iterations

    @staticmethod
    def ikRotationWeight(c):
        return c.weight

    @staticmethod
    def isIKSolver(c):
        return c.type=='IK'
