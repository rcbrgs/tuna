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
                        GL_MODELVIEW,
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
                        glGetUniformLocation,
                        glLinkProgram,
                        glLoadIdentity,
                        glMatrixMode,
                        glOrtho,
                        glPointSize,
                        glShaderSource,
                        glUniformMatrix4fv,
                        glUseProgram,
                        glVertexAttribPointer,
                        glViewport )
from PyQt4.QtCore import ( pyqtSignal,
                           Qt )
from PyQt4.QtGui import ( QDockWidget,
                          QGridLayout,
                          QKeyEvent,
                          QLabel,
                          QPalette,
                          QScrollArea )
from PyQt4.QtOpenGL import ( QGLWidget )

class widget_shader_points_from_ndarray ( QGLWidget ):
    def __init__ ( self, image_ndarray = numpy.ndarray, log = None ):
        super ( widget_shader_points_from_ndarray, self ).__init__ ( )
        if log is None:
            self.log = print
        else:
            self.log = log

        self.translation_array = [1.0, 0.0, 0.0, 0.00,
                                  0.0, 1.0, 0.0, 0.00,
                                  0.0, 0.0, 1.0, 0.00,
                                  0.0, 0.0, 0.0, 1.00]
        self.translation = numpy.array ( self.translation_array, dtype = numpy.float32 )
        self.translated_vertex_source_old = """
        #version 130
        in vec3 position;
        in vec3 color;
        uniform mat4 translation_matrix;
        out vec4 translated_position;
        out vec3 computed_color;

        void main ( void )
        {
            computed_color = color;
            translated_position = translation_matrix * vec4 ( position, 1.0 );
            gl_Position = translated_position;
        }
        """
        self.translated_vertex_source = """
        #version 130
        in vec3 position;
        in vec3 color;
        uniform mat4 translation_matrix;
        uniform mat4 centered_frustrum_view_matrix;
        out vec4 viewed_translated_position;
        out vec3 computed_color;

        void main ( void )
        {
            computed_color = color;
            //translated_position = translation_matrix * vec4 ( position, 1.0 );
            viewed_translated_position = centered_frustrum_view_matrix * translation_matrix * vec4 ( position, 1.0 );
            //gl_Position = translated_position;
            gl_Position = viewed_translated_position;
        }
        """
        self.scaled_translated_vertex_source = """
        #version 130
        in vec3 position;
        in vec3 color;
        uniform mat4 translation_matrix;
        uniform mat4 centered_frustrum_view_matrix;
        uniform mat4 scale_matrix;
        out vec4 viewed_translated_position;
        out vec3 computed_color;

        void main ( void )
        {
            computed_color = color;
            //gl_Position = scale_matrix * centered_frustrum_view_matrix * translation_matrix * vec4 ( position, 1.0 );
            gl_Position = scale_matrix * translation_matrix * vec4 ( position, 1.0 );
        }
        """
        self.fragment = """
        #version 130
        in  vec3 computed_color;
        out vec4 fout_color;
        
        void main(void)
        {
            fout_color = vec4 ( computed_color, 1.0 );
        }
        """

        self.scale_array = [1.0, 0.0, 0.0, 0.0,
                            0.0, 1.0, 0.0, 0.0,
                            0.0, 0.0, 1.0, 0.0,
                            0.0, 0.0, 0.0, 1.0]

        self.scale = numpy.array ( self.scale_array, dtype = numpy.float32 )

        self.__image_ndarray = image_ndarray
        if self.__image_ndarray.ndim == 3:
            self.height = self.__image_ndarray.shape[1]
            self.width  = self.__image_ndarray.shape[2]
        if self.__image_ndarray.ndim == 2:
            self.height = self.__image_ndarray.shape[0]
            self.width  = self.__image_ndarray.shape[1]
        self.depth  = numpy.amax ( self.__image_ndarray ) - numpy.amin ( self.__image_ndarray )
        self.log ( "self.depth = %d." % self.depth )
        self.z_near = 10
        self.z_far  = self.z_near + self.depth + 10
        
        centered_frustrum_view_array = [ self.z_near / ( self.width / 2 ), 0.0, 0.0, 0.0,
                                             0.0, self.z_near / ( self.height / 2 ), 0.0, 0.0,
                                             0.0, 0.0, - ( self.z_far + self.z_near ) / ( self.z_far - self.z_near ), 2 * self.z_far * self.z_near / ( self.z_far - self.z_near ), 
                                             0.0, 0.0, -1.0, 0.0 ]
        print ( centered_frustrum_view_array )
        self.centered_frustrum_view = numpy.array ( centered_frustrum_view_array, dtype = numpy.float32 )
        new_vertex_data = []
        new_color_data = []
        channel_max = numpy.amax ( image_ndarray )
        height_max = image_ndarray.shape[0]
        width_max = image_ndarray.shape[1]
        for height in range ( height_max ):
            for width in range ( width_max ):
                new_vertex_data.append ( float ( width  / width_max  ) * 2 - 1 )
                new_vertex_data.append ( float ( height / height_max ) * 2 - 1 )
                new_vertex_data.append ( float ( image_ndarray[height][width] / channel_max ) )
                #new_color_data.append ( float ( image_ndarray[height][width] / channel_max ) )
                #new_color_data.append ( float ( image_ndarray[height][width] / channel_max ) )
                new_color_data.append ( 0.0 )
                new_color_data.append ( 0.0 )
                new_color_data.append ( float ( image_ndarray[height][width] / channel_max ) )
        self.vertex_data = numpy.array ( new_vertex_data, dtype = numpy.float32 )
        self.color_data  = numpy.array ( new_color_data,  dtype = numpy.float32 )

    def initializeGL ( self ):
        glClearColor ( 1.0, 0.5, 1.0, 1.0 )
        glClearDepth ( 1.0 )

    def paintGL ( self ):
        program = link_shaders_into_program ( fragment_source = self.fragment, vertex_source = self.scaled_translated_vertex_source )
        vao_id = glGenVertexArrays ( 1 )
        glBindVertexArray ( vao_id )
        vbo_id = glGenBuffers ( 2 )

        glBindBuffer ( GL_ARRAY_BUFFER, vbo_id[0] )
        glBufferData ( GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount ( self.vertex_data ), self.vertex_data, GL_STATIC_DRAW )
        glVertexAttribPointer ( program.attribute_location ( 'position' ), 3, GL_FLOAT, GL_FALSE, 0, None )
        glEnableVertexAttribArray ( 0 )
        
        glBindBuffer ( GL_ARRAY_BUFFER, vbo_id[1] )
        glBufferData ( GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount ( self.color_data ), self.color_data, GL_STATIC_DRAW )
        glVertexAttribPointer ( program.attribute_location ( 'color' ), 3, GL_FLOAT, GL_FALSE, 0, None )
        glEnableVertexAttribArray ( 1 )

        glUseProgram ( program.program_id )
        glUniformMatrix4fv ( program.uniform_location ( 'translation_matrix' ), 1, GL_FALSE, self.translation )
        glUniformMatrix4fv ( program.uniform_location ( 'centered_frustrum_view_matrix' ), 1, GL_FALSE, self.centered_frustrum_view )
        glUniformMatrix4fv ( program.uniform_location ( 'scale_matrix' ), 1, GL_FALSE, self.scale )

        glBindBuffer ( GL_ARRAY_BUFFER, 0 )
        glBindVertexArray ( 0 )
        glClear ( GL_COLOR_BUFFER_BIT )

        glBindVertexArray ( vao_id )
        glPointSize ( 5.0 )
        glDrawArrays ( GL_POINTS, 0, 512*512 )
        glUseProgram ( 0 )
        glBindVertexArray ( 0 )

    def resizeGL ( self, width, height ):
        if width > height:
            glViewport ( 0, 0, height, height )
        else:
            glViewport ( 0, 0, width, width )
        #glMatrixMode ( GL_PROJECTION )
        #glLoadIdentity ( )
        #  glOrtho( left , right , bottom , top , zNear , zFar ) 
        #glOrtho ( -1.0, 1.0,
        #          -1.0, 1.0,
        #          -10.0, 10.0 )
        #glMatrixMode ( GL_MODELVIEW )

    def move_left ( self ):
        self.translation_array[3] += 0.1
        self.translation = numpy.array ( self.translation_array, dtype = numpy.float32 )
        self.updateGL ( )

    def move_right ( self ):
        self.translation_array[3] -= 0.1
        self.translation = numpy.array ( self.translation_array, dtype = numpy.float32 )
        self.updateGL ( )

    def move_up ( self ):
        self.translation_array[7] += 0.1
        self.translation = numpy.array ( self.translation_array, dtype = numpy.float32 )
        self.updateGL ( )

    def move_down ( self ):
        self.translation_array[7] -= 0.1
        self.translation = numpy.array ( self.translation_array, dtype = numpy.float32 )
        self.updateGL ( )

    def scale_bigger ( self ):
        self.scale_array[0] += 0.1
        self.scale_array[4] += 0.1
        self.scale_array[7] += 0.1
        self.scale = numpy.array ( self.scale_array, dtype = numpy.float32 )
        self.updateGL ( )

    def scale_smaller ( self ):
        self.scale_array[0] -= 0.1
        self.scale_array[4] -= 0.1
        self.scale_array[7] -= 0.1
        self.scale = numpy.array ( self.scale_array, dtype = numpy.float32 )
        self.updateGL ( )

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
        #self.closed.emit ( str ( self.image_canvas.cacheKey ( ) ) )
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

    def keyPressEvent ( self, event = QKeyEvent ):
        #print ( "Key pressed. Code: ", event.key ( ), " string: ", event.text ( ) )
        #if event.key ( ) == 81:
        #    self.__canvas_widget.move_left ( )
        #if event.key ( ) == 68:
        #    self.__canvas_widget.move_right ( )
        #if event.key ( ) == 90:
        #    self.__canvas_widget.move_up ( )
        #if event.key ( ) == 83:
        #    self.__canvas_widget.move_down ( )
        keyboard_event_callback = { 81 : self.__canvas_widget.move_left,
                                    68 : self.__canvas_widget.move_right,
                                    90 : self.__canvas_widget.move_up,
                                    83 : self.__canvas_widget.move_down,
                                    43 : self.__canvas_widget.scale_bigger,
                                    45 : self.__canvas_widget.scale_smaller }
        if event.key ( ) in keyboard_event_callback.keys ( ):
            keyboard_event_callback [ event.key ( ) ] ( )
        else:
            self.log ( "Key %s (code %d) pressed." % ( event.text ( ), event.key ( ) ) )
    

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

