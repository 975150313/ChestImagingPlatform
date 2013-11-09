import vtk
import math
import numpy as np
from optparse import OptionParser
from vtk.util.numpy_support import vtk_to_numpy

class DisplayVasculature:    
    def __init__(self, file_list, spacing_list, h1_th=-200,
                 glyph_type='Sphere', use_field_data=True, opacity_list=[],
                 color_list=[], lung=[]):
        self.mapper_list = list()
        self.actor_list = list()
        self.glyph_list = list()
        self.glyph_type = glyph_type
        self.file_list = file_list
        self.spacing_list = spacing_list
        self.opacity_list = opacity_list
        self.h1_th = h1_th
        self.color_list = color_list
        self.lung = lung
        self.use_field_data = use_field_data
        self.ren = vtk.vtkRenderer()

    
    def compute_radius (self,poly,spacing):
        if self.use_field_data == False:
            scale = poly.GetPointData().GetArray("scale")
            h1 = poly.GetPointData().GetArray("h1")
            val = poly.GetPointData().GetArray('val')
        else:
            scale=poly.GetFieldData().GetArray("scale")
            h1 = poly.GetFieldData().GetArray("h1")
            val = poly.GetFieldData().GetArray('val')
        np = poly.GetNumberOfPoints()
        print np
        radiusA=vtk.vtkDoubleArray()
        radiusA.SetNumberOfTuples(np)
        si=0.2
        
        arr = vtk_to_numpy(h1)
        print arr[0]
        for kk in range(np):
            ss=float(scale.GetValue(kk))
            #rad=math.sqrt(2.0) * ( math.sqrt(spacing**2.0 (ss**2.0 + si**2.0)) - 1.0*spacing*s0 )
            rad=math.sqrt(2)*spacing*ss
            if arr[kk] > self.h1_th:
                rad=0
            if rad < spacing:
                rad=0
            radiusA.SetValue(kk,rad)

        poly.GetPointData().SetScalars(radiusA)
        return poly

    def create_glyphs (self, poly):    
        if self.glyph_type == 'Sphere':
            glyph = vtk.vtkSphereSource()
            glyph.SetRadius(1)
            glyph.SetPhiResolution(8)
            glyph.SetThetaResolution(8)
        elif self.glyph_type == 'Cylinder':
            glyph = vtk.vtkCylinderSource()
            glyph.SetHeight(1.9)
            glyph.SetRadius(0.5)
            glyph.SetCenter(0,0,0)
            glyph.SetResolution(10)
            glyph.CappingOn()

        tt = vtk.vtkTransform()
        tt.RotateZ(90)
        tf = vtk.vtkTransformPolyDataFilter()
        tf.SetInput(glyph.GetOutput())
        tf.SetTransform(tt)
        tf.Update()

        glypher = vtk.vtkGlyph3D()
        glypher.SetInput(poly)
        glypher.SetSource(tf.GetOutput())
        glypher.SetVectorModeToUseNormal()
        glypher.SetScaleModeToScaleByScalar()
        glypher.SetScaleFactor(0.5)
        glypher.Update()

        return glypher

    def create_actor (self, glyph , opacity=1,color=[0.1,0.1,0.1], minrad=0,
                      maxrad=5):
        mapper=vtk.vtkPolyDataMapper()
        mapper.SetInput(glyph.GetOutput())
        mapper.SetColorModeToMapScalars()
        mapper.SetScalarRange(minrad,maxrad)
        if len(color) > 0:
            mapper.ScalarVisibilityOff()
        #mapper.SetScalarRange(minrad,maxrad)
            #else:
        #    mapper.SetColorModeToDefault()
        print color 
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        if len(color) > 0 :
            actor.GetProperty().SetColor(color)
        actor.GetProperty().SetOpacity(opacity)
        self.mapper_list.append(mapper)
        self.actor_list.append(actor)
        for aa in self.actor_list:
            self.ren.AddActor(aa)
            self.ren.SetBackground(1,1,1)
        return actor

    def add_color_bar(self):
        colorbar=vtk.vtkScalarBarActor()
        colorbar.SetMaximumNumberOfColors(400)
        colorbar.SetLookupTable(self.mapper_list[0].GetLookupTable())
        colorbar.SetWidth(0.09)
        colorbar.SetPosition(0.91,0.1)
        colorbar.SetLabelFormat("%.3g mm")
        colorbar.VisibilityOn()
        
        if len(self.color_list) == 0:
            self.ren.AddActor(colorbar)

    def render(self,widht=800,height=800):
        # create a rendering window and renderer
        renWin = vtk.vtkRenderWindow()
        renWin.AddRenderer(self.ren)
        renWin.SetSize(widht,height)
        renWin.SetAAFrames(0)

        # create a renderwindowinteractor
        iren = vtk.vtkRenderWindowInteractor()
        iren.SetRenderWindow(renWin)

        # enable user interface interactor
        iren.Initialize()
        renWin.Render()
        iren.Start()
                                
    def execute(self):
        for kk,file_name in enumerate(self.file_list):
            reader=vtk.vtkPolyDataReader()
            reader.SetFileName(file_name)
            reader.Update()
            
            poly = self.compute_radius(reader.GetOutput(),spacing_list[kk])
            if self.use_field_data == False:
                poly.GetPointData().\
                    SetNormals(poly.GetPointData().GetArray("hevec0"))
            else:
                poly.GetPointData().\
                    SetNormals(poly.GetFieldData().GetArray("hevec0"))
        
            glypher=self.create_glyphs(poly)
            if len(self.color_list) <= kk:
                color=[]
            else:
                color=self.color_list[kk]
            if len(self.opacity_list) <= kk:
                opacity=1
            else:
                opacity=self.opacity_list[kk]
            self.create_actor(glypher,color=color,opacity=opacity)
        
        if len(self.lung)>0:
            reader=vtk.vtkPolyDataReader()
            reader.SetFileName(self.lung)
            reader.Update()
            tt=vtk.vtkTransform()
            tt.Identity()
            tt.GetMatrix().SetElement(0,0,-1)
            tt.GetMatrix().SetElement(1,1,-1)
            tf=vtk.vtkTransformPolyDataFilter()
            tf.SetTransform(tt)
            tf.SetInput(reader.GetOutput())
            tf.SetTransform(tt)
            self.create_actor(tf,0.1,color=[0.8,0.4,0.01])

        self.add_color_bar()
        self.render()

    def capture_window(self):
        ff = vtkWindowToImageFilter()
        sf = vtkPNGWriter()

        ff.SetInput(self.renWin)
        ff.SetMagnification(4)
        sf.SetInput(ff.GetOutput)
        sf.SetFileName('/Users/rjosest/test.png')
        self.renWin.Render()
        ff.Modified()
        sf.Write()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", help='TODO', dest="file_name")
    parser.add_option("-s", help='TODO', dest="spacing")
    parser.add_option("--h1th", help='TODO', dest="h1th", default=0)
    parser.add_option("--color", help='TODO', dest="color_list", default="")
    parser.add_option("--opacity", help='TODO', dest="opacity_list", \
                      default="")
    parser.add_option("-l", help='TODO', dest="lung_filename", default="")
    parser.add_option("--useFieldData", help='TODO', dest="use_field_data", \
                      action="store_true")

    (options, args) = parser.parse_args()

    translate_color = dict()
    translate_color['red'] = [1, 0.1, 0.1]
    translate_color['green'] = [0.1, 0.8, 0.1]
    translate_color['orange'] = [0.95, 0.5, 0.01]
    translate_color['blue'] = [0.1, 0.1, 0.9]

    file_list = [i for i in str.split(options.file_name,',')]
    use_field_data = options.use_field_data
    spacing_list = [float(i) for i in str.split(options.spacing,',')]
    lung_filename = options.lung_filename

    if options.opacity_list == "":
        opacity_list=[]
    else:
        opacity_list = [float(i) for i in str.split(options.opacity_list,',')]
                           
    if options.color_list == "" :
        color_list=[]
    else:
        color_list = [translate_color[val] for val in str.split(options.color_list,',')]

    print color_list

    dv = DisplayVasculature(file_list, spacing_list, float(options.h1th), \
        'Cylinder', use_field_data, opacity_list, color_list, lung_filename)
    dv.execute()
