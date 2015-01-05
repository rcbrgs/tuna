"""
widget_viewer_3d displays 3d images in a dock.
"""

import numpy
from OpenGL.arrays import ArrayDatatype
from OpenGL.GL import ( GL_ARRAY_BUFFER,
                        GL_COLOR_BUFFER_BIT,
                        GL_COMPILE_STATUS,
                        GL_FALSE,
                        GL_FLOAT,
                        GL_FRAGMENT_SHADER,
                        GL_LINK_STATUS,
                        GL_POINTS,
                        GL_PROJECTION,
                        GL_STATIC_DRAW,
                        GL_TRIANGLES,
                        GL_TRUE,
                        GL_VERTEX_SHADER,
                        glAttachShader,
                        glBindBuffer,
                        glBindVertexArray,
                        glBufferData,
                        glClear,
                        glClearColor,
                        glClearDepth,
                        glCompileShader,
                        glCreateProgram,
                        glCreateShader,
                        glDeleteProgram,
                        glDeleteShader,
                        glDrawArrays,
                        glEnableVertexAttribArray,
                        glGenBuffers,
                        glGenVertexArrays,
                        glGetAttribLocation,
                        glGetProgramiv,
                        glGetProgramInfoLog,
                        glGetShaderInfoLog,
                        glGetShaderiv,
                        glLinkProgram,
                        glLoadIdentity,
                        glMatrixMode,
                        glOrtho,
                        glPointSize,
                        glShaderSource,
                        glUseProgram,
                        glVertexAttribPointer,
                        glViewport )
from PyQt4.QtCore import ( pyqtSignal,
                           Qt )
from PyQt4.QtGui import ( QDockWidget,
                          QGridLayout,
                          QLabel,
                          QPalette,
                          QScrollArea )
from PyQt4.QtOpenGL import ( QGLWidget )

class widget_shader_points_from_ndarray ( QGLWidget ):
    def __init__ ( self, image_ndarray = numpy.ndarray ):
        super ( widget_shader_points_from_ndarray, self ).__init__ ( )
        self.vertex = """
        #version 130
        in vec3 vin_position;
        in vec3 vin_color;
        out vec3 vout_color;
        
        void main(void)
        {
        vout_color = vin_color;
        gl_Position = vec4(vin_position, 1.0);
        }
        """
        self.fragment = """
        #version 130
        in vec3 vout_color;
        out vec4 fout_color;
        
        void main(void)
        {
        fout_color = vec4(vout_color, 1.0);
        }
        """
        self.vertex_data = numpy.array([0.75, 0.75, 0.0,
                                0.75, -0.75, 0.0,
                                -0.75, -0.75, 0.0], dtype=numpy.float32)
        self.color_data = numpy.array([1, 0, 0,
                               0, 1, 0,
                               0, 0, 1], dtype=numpy.float32)
        self.__image_ndarray = image_ndarray
        new_vertex_data = []
        new_color_data = []
        channel_max = numpy.amax ( image_ndarray )
        height_max = image_ndarray.shape[0]
        width_max = image_ndarray.shape[1]
        for height in range ( image_ndarray.shape[0] ):
            for width in range ( image_ndarray.shape[1] ):
                new_vertex_data.append ( float ( height / height_max ) - 0.5 )
                new_vertex_data.append ( float ( width  / width_max  ) - 0.5 )
                new_vertex_data.append ( float ( image_ndarray[height][width] / channel_max ) - 0.5 )
                new_color_data.append ( float ( image_ndarray[height][width] / channel_max ) )
                new_color_data.append ( 0 )
                new_color_data.append ( 0 )
        self.vertex_data = numpy.array ( new_vertex_data, dtype = numpy.float32 )
        self.color_data  = numpy.array ( new_color_data,  dtype = numpy.float32 )
        #print ( self.vertex_data )

    def initializeGL ( self ):
        glClearColor ( 0.5, 0.5, 1.0, 1.0 )
        glClearDepth ( 1.0 )
        glMatrixMode ( GL_PROJECTION )
        glLoadIdentity ( )
        glOrtho ( -0.15, 50, -50, 50, -50.0, 50.0 )

    def paintGL ( self ):
        program = link_shaders_into_program ( fragment_source = self.fragment, vertex_source = self.vertex )
        vao_id = glGenVertexArrays(1)
        glBindVertexArray(vao_id)
        vbo_id = glGenBuffers(2)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_id[0])
        glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(self.vertex_data), self.vertex_data, GL_STATIC_DRAW)
        glVertexAttribPointer(program.attribute_location('vin_position'), 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_id[1])
        glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(self.color_data), self.color_data, GL_STATIC_DRAW)
        glVertexAttribPointer(program.attribute_location('vin_color'), 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(program.program_id)
        glBindVertexArray(vao_id)
        glPointSize ( 5.0 )
        glDrawArrays(GL_POINTS, 0, 512*512)
        glUseProgram(0)
        glBindVertexArray(0)

    def resizeGL ( self, width, height ):
        glViewport ( 0, 0, width, height )
        glMatrixMode ( GL_PROJECTION )
        glLoadIdentity ( )
        #aspect_ratio = float ( width ) / float ( height )
        #print ( "aspect_ratio = %s." % aspect_ratio )

class widget_viewer_3d ( QDockWidget ):
    opened = pyqtSignal ( str )
    closed = pyqtSignal ( str )
    def __init__ ( self, image_ndarray = numpy.ndarray, log = None, *args, **kwargs ):
        super ( widget_viewer_3d, self ).__init__ ( *args, **kwargs )
        self.setFloating ( True )
        self.__image_ndarray = image_ndarray
        self.__canvas_widget = widget_shader_points_from_ndarray ( image_ndarray = self.__image_ndarray )
        if log:
            self.log = log
        else:
            self.log = print
        
    def set_image_ndarray ( self, image_ndarray = numpy.ndarray ):
        self.__image_ndarray = image_ndarray
        # populate shaders
        self.__canvas_widget.set_image_ndarray ( self.__image_ndarray )

    def set_title ( self, title = str ):
        self.__title = title 

    def closeEvent ( self, event ):
        self.closed.emit ( str ( self.image_canvas.cacheKey ( ) ) )
        super ( widget_viewer_3d, self ).closeEvent ( event )

    def display ( self ):
        self.__title_label = QLabel ( self.__title )

        self.__layout = QGridLayout ( )	
        self.__layout.addWidget ( self.__title_label )
        self.__layout.addWidget ( self.__canvas_widget )

        self.__scroll_area = QScrollArea ( )
        self.__scroll_area.setBackgroundRole ( QPalette.Dark )
        self.__scroll_area.setLayout ( self.__layout )

        self.setWidget ( self.__scroll_area )


class link_shaders_into_program ( object ):
    """
    Based on code publicly available at: https://gist.github.com/deepankarsharma/3494203
    """
    def __init__ ( self, vertex_source, fragment_source ):
        self.program_id = glCreateProgram ( )
        vertex_shader_id   = self.add_shader ( vertex_source, GL_VERTEX_SHADER )
        fragment_shader_id = self.add_shader ( fragment_source, GL_FRAGMENT_SHADER )
        glAttachShader ( self.program_id, vertex_shader_id )
        glAttachShader ( self.program_id, fragment_shader_id )
        glLinkProgram  ( self.program_id )
        if glGetProgramiv ( self.program_id, GL_LINK_STATUS ) != GL_TRUE:
            info = glGetProgramInfoLog ( self.program_id )
            glDeleteProgram ( self.program_id )
            glDeleteShader ( vertex_shader_id )
            glDeleteShader ( fragment_shader_id )
            raise RuntimeError ( 'Error linking program: %s' % ( info ) )
        glDeleteShader ( vertex_shader_id )
        glDeleteShader ( fragment_shader_id )
 
    def add_shader(self, source, shader_type):
        """ 
        Helper function for compiling a GLSL shader

        Parameters
        ----------
        source : str
            String containing shader source code

        shader_type : valid OpenGL shader type
            Type of shader to compile

        Returns
        -------
        value : int
            Identifier for shader if compilation is successful

        """
        try:
            shader_id = glCreateShader ( shader_type )
            glShaderSource ( shader_id, source )
            glCompileShader ( shader_id )
            if glGetShaderiv ( shader_id, GL_COMPILE_STATUS ) != GL_TRUE:
                info = glGetShaderInfoLog ( shader_id )
                raise RuntimeError ( 'Shader compilation failed: %s' % ( info ) )
            return shader_id
        except:
            glDeleteShader ( shader_id )
            raise
 
    def uniform_location ( self, name ):
        """ 
        Helper function to get location of an OpenGL uniform variable

        Parameters
        ----------
        name : str
            Name of the variable for which location is to be returned

        Returns
        -------
        value : int
            Integer describing location

        """
        return glGetUniformLocation ( self.program_id, name )
 
    def attribute_location ( self, name ):
        """ 
        Helper function to get location of an OpenGL attribute variable

        Parameters
        ----------
        name : str
            Name of the variable for which location is to be returned

        Returns
        -------
        value : int
            Integer describing location

        """
        return glGetAttribLocation ( self.program_id, name )

