import Rhino.Geometry as rg
import clr
clr.AddReference("Grasshopper")
import Grasshopper
clr.AddReferenceToFileAndPath(Grasshopper.Folders.DefaultAssemblyFolder + "Plankton.dll")
clr.AddReferenceToFileAndPath(Grasshopper.Folders.DefaultAssemblyFolder + "Plankton.gha")
import Plankton
import PlanktonGh
clr.ImportExtensions(PlanktonGh.RhinoSupport)

oPoint=[]
def grow(r, environment):
    r = rg.Point3d(r)
    crv = environment.curve
    t = crv.ClosestPoint(r)
    t = t[1]
    point = crv.PointAt(t)
    d = r.DistanceTo(point)
    result = d < 2
    return result

 

if 'meshh' not in globals() or reset:
    meshh = PMesh
    iterationCount = 0

elif iterationCount < n:
    for i in range(meshh.Halfedges.Count):
        vertices = meshh.Halfedges.GetVertices(i)
        vertices = [meshh.Vertices[vertices[0]], meshh.Vertices[vertices[1]]]
        firstVert, secondVert = vertices[0].ToPoint3d(), vertices[1].ToPoint3d()
        r = (firstVert + secondVert)/2

        
        if grow(r, iEnvironment) and (meshh.Halfedges.GetLength(i)>2):
            meshh.Halfedges.TriangleSplitEdge(i)

    mesh=PlanktonGh.RhinoSupport.ToRhinoMesh(meshh)
    pts = mesh.Vertices
    
    counts = [0]*len(pts)
    vecs = [rg.Vector3d.Zero]*len(pts)
    
    for i in range(len(pts)):
        for j in range(i+1, len(pts)):
            d = pts[i].DistanceTo(pts[j])
            if d < 2:
                counts[i] += 1
                counts[j] += 1
                vec = pts[i]-pts[j]
                vec.Unitize()
                vecc = rg.Vector3d(vec.X,vec.Y,vec.Z)
                factor = (2-d)*0.5
                vecc *= factor
                vecs[i] += vecc
                vecs[j] -= vecc
    
    for i in range(len(pts)):
        if counts[i] > 0:
            grw = grow(pts[i], iEnvironment)
            vecs[i] = vecs[i]/counts[i]+0.1*grw*vecs[i]
        ptx = pts[i].X + vecs[i].X
        pty = pts[i].Y + vecs[i].Y
        ptz = pts[i].Z + zScale * vecs[i].Z
        
        pts[i]=rg.Point3f(ptx,pty,ptz)
        

    newMesh = rg.Mesh()
    
    for i in range(0, len(pts)):
        newMesh.Vertices.Add(pts[i])
    
    for i in range(0, mesh.Faces.Count):
        newMesh.Faces.AddFace(mesh.Faces[i])
    
    newMesh.RebuildNormals()
    oMesh = newMesh
    meshh = newMesh.ToPlanktonMesh()
    

    
    iterationCount += 1
    oIterations = iterationCount

else:
    mesh = oMesh
    
    
#Should we control and vary the growth using the vectors in the sphere packing 
#Or using a function for the division input at the start?