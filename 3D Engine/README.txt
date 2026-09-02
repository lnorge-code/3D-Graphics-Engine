# 3D Graphics Engine with graphics.py

## A proof of concept 3D graphics engine made using a graphics.py window, allowing for the creation, transformation, and displaying of simple 3D shapes

This project is a proof of concept 3D graphics engine that was made for the purposes of learning about the processes used by 3D software such as game engines and
slicing software to display images. Much of the math regarding transforming 3D objects onto the 2D plane was made possible through Brendan Galea's YouTube tutorial
on perspective projection (https://www.youtube.com/watch?v=U0_ONQQ5ZNM). While this tutorial is intended for Vulkan, I HIGHLY recommend watching it to understand the 
math behind the perspective projection matrix. For this project, I simply wanted to see if I could apply the math behind projection and rasterization to a simple python 
project and as such the project is devoid of many optimization techniques used in more advanced programs such as backface culling or occlusion culling. In addition, the
project uses python's built-in memory manager and is not optimized for speed, opting to redraw the window after every object added/transformed. I also wanted to
steer clear of the more efficient yet complicated topic of barycentric coordinates when rasterizing, and have opted for a much simpler, less optimal solution using the
intersections of lines and planes. I hope to come back to this project in the future, and program a much faster and far more up to standard version of this project in Vulkan.
A couple of changes I would add would be more culling modes, barycentric rasterization, shaders, real-time window updates, more intuitive transformation methods, and a slightly
different perspective projection matrix implementation (For this project, I did not use homogenous coordinates, or a commonly used mathematical simplification intentionally made
to reduce z fighting when using other graphics APIs).

project features:
    -creating, deleting, and transforming simple 3D objects
    -applying the perspective projection matrix onto objects
    -rasterizing objects onto the screen using the plane equation of each shape and using z-buffering to know what should be brought to the front

## Recommended Resources:
    -https://www.youtube.com/watch?v=U0_ONQQ5ZNM -> perspective projection matrix and brief mention of rasterization
    -https://math.stackexchange.com/questions/28043/finding-the-z-value-on-a-plane-with-x-y-values -> the math used when rasterizing to get a z-value given the x and y coordinates
    -https://www.youtube.com/watch?v=JCx3jeIhBr0 -> The math used in both fringe cases when rasterizing where planes present as lines
    -https://www.youtube.com/watch?v=h9OWnuarYuc -> explains the math behind how the engine performs rotations

## Installation and Usage:
    Installation:
        -Installation is as simple as downloading the file engine.py to your system and ensuring you have the correct dependencies
        -You must ensure you have python (version 2.0 or greater should work) installed to run the file, and you must ensure you have the graphics import installed 
            by using the command "pip install graphics.py" in your terminal
    
    Usage:
        -The program makes use of the terminal to gather user input, so the file must be run from there, or from the code editor of your choice
        -Using the program involves following the prompts given to you to select which command is to be run and what the values of points/transformations to the objects are:
            ->You will first be prompted with a list of numbered commands. Enter the number of the command you will want to run
            ->When creating a shape, you will be asked to enter points making up that shape, a colour, and a name.
                *when entering points, you enter the x, y, and z coordinates of the point separated by commas. If less than three values are given, the rest of them become 0.
                    Every value after the third is ignored. x increases to the right, y increases upwards, and z increases going into the screen. Some shapes, like quadrilaterals 
                    or the bases of square based pyramids will prompt for points in a certain order, and require you to enter them as they appear or they may come out wrong. When
                    it specifies which one, they will be described as the top/bottom left/right vertice WHEN LOOKING AT THE SHAPE HEAD ON, so pick which side of the face you are
                    looking from, and enter them in the correct order, from that same side.
                *when entering colours, you may enter the name of any colour available in graphics.py, or you may make your own with RGB values. When entering RGB values, the
                    same rules apply for more/less values as points
                *shape names are case-sensitive
            ->When scaling, rotating, or positioning a shape, it will ask for the name of the shape, and the magnitude of transformation about each axis separated by commas
                *the magnitudes follow the same rules as entering points/RGB colours for more/less values
                *all transformations are about the world, NOT about the shape (global, NOT local)
                *x increases to the right, y increases upwards, and z increases going into the screen
                *rotations increase going clockwise about each axis, and are always applied in the order of X, then Y, then Z, so extra consideration for this order must be done
                *ALL TRANSFORMATIONS ARE SET VALUES FROM THE OBJECT'S STARTING POSITION, NOT ADDED TOGETHER, so for example, positioning the shape by 30, 0, 0, and then
                    repositioning the shape again by 60, 0, 0, only moves the shape 30 pixels to the right
                *objects are first scaled, then rotated, then translated. This is the recommended order about which you should do your transformations.
            ->When deleting an object, it will ask for the object's name, delete it, and then that name becomes available to use again
        -The window is automatically re-drawn every time a shape is made, transformed, or deleted
        -Other notes about operating the program:
            ->Any parts of a shape outside of the canonical view volume for the program (watch perspective projection video) will not be drawn. For this program, the canonical view
                volume is 500 pixels x 500 pixels x 250 pixels, and the origin lies in the center of the screen, on the near viewing plane. This means values that will be drawn lie
                between -250-250, -250-250, and 0-250 will be drawn (after the perspective proection matrix is applied).
            ->A wireframe of a shape will also be drawn to help discern each face or to know when parts of a shape were cut off
            ->If an inappropriate value for a point, colour, etc. is given (i.e. a letter in place of a number), the program will allow you to re-enter it

## How to tweak code for yourself

I encourage you to tweak the code for this project if you are interested. I would recommend familiarizing yourself with rasterization concepts and the perspective
projection matrix to gain an understanding of what goes on behind the scenes. Otherwise, there are a couple of things of note when understanding//working with this
project:
    -The shape class: The shape class simply holds a pointList and planeList responsible for tracking the points and triangles associated with the shape. All other
classes are derived from it and must set their pointList and triangleList upon initialization, so that the correct points and triangles are modified whenever the shape
is transformed.
    -The point class: This class stores real and transformed x, y, and z values, and a method to calculate the post-transform values of each coordinate on the point
(must be called before rasterization). Intended for use with the triangle class.
    -The triangle class: This class stores 3 points, and coefficients for the standard form equation for the plane on which it resides. It contains methods for calculating
the aforementioned planar coordinates (must be called ahead of rasterization), a method to determine whether a point lies within a triangle (called during rasterization,
note it wouldn't be necessary if I used barycentric coordinates/standard rasterization methods), and methods for finding the z value of the plane given an x and y value (there
are actually two, one used under normal circumstances, and one used in the event the triangle makes up a line or is a plane aligned with the screen).
    -Differences in my perspective projection method and the standard perspective projection method: In the standard perspective projection method, a perspective projection
matrix is defined using two volumes: an orthographic view volume which accounts for scaling and repositioning of the camera, and a perspective view volume, which is a frustrum
representing perspective distortion. When this method is done, it is performed using matrices and a mathematical cheat which makes values intentionally off a little to help combat
z fighting. My method skips the orthographic view volume and assumes a static camera, because it is easier for my purposes. It also is done purely algrabraically using the math found
in Brendan Galea's YouTube tutorial, around the 8:30 mark (https://www.youtube.com/watch?v=U0_ONQQ5ZNM), using the same similar triangle laws but using trigonometry to find the distance
of the observer with the fov and window height.
    -Difference in rasterization from standard: it is standard to use barycentric rasterization methods, but my method is not built for speed and is simply a proof of concept, so I simply
use the standard form equation of the plane formed by each triangle, and plug in an x and y value corresponding to the pixel being checked to find the z value.