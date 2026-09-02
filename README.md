3D Graphics engine:
A 3D graphics engine project with a simple UI allowing you to enter 3 dimensional points, which it transforms and displays to a graphics.py window to give the illusion of being 3D.

To use the graphics engine you will go through a simple prompting process where you are either presented with a numbered list of options and proceed by entering the number of one option, or you will be prompted to enter points or values, in which case you enter them like so: "x, y, z". When you are prompted to enter colours, you may enter the name of the colour in graphics.py, or you can enter an rgb value separated by commas: "r, g, b". Whenever you create a shape you must enter a name or you won't be able to access it later for the purposes of transforming the shape. Transformations (occur in order given ahead once told to runthe engine, NOT the order entered by the user): scale: scales the untransformed object about each axis (i.e. 2, 1, 1 scales it by 2 in the x-axis) rotate: rotates the scaled object about each axis. Uses Euler angles, rotating clockwise about THE ORIGIN'S AXES (i.e. 90, 0, 0 rotates 90 about the x-axis) position: translates the object how ever many units are entered for each axis (i.e. 200, 100, 10 is 200 right, 100 up, and 10 forward)

Other important things to note:

the z axis faces away from the camera, that means as z increases the object gets further away
because rotation is applied about the origin before translations, it may be easier to create the object, rotate it, and then put the desired coordinates in through the position option
the scale of the graphics window is 500 by 500, but this only comes into play when your points lie at z=0
the graphics engine is terribly optimized at the moment, so kick back and let it work
Resources Used and Credit: Video links: Understanding perspective projection and rasterization: - https://www.youtube.com/watch?v=cvcAjgMUPUA - https://www.youtube.com/watch?v=htSGrJJOtAk - https://www.youtube.com/watch?v=U0_ONQQ5ZNM - https://www.youtube.com/watch?v=nvWDgBGcAIM Mathematics help: - https://www.geeksforgeeks.org/dsa/check-whether-a-given-point-lies-inside-a-triangle-or-not/ - https://math.stackexchange.com/questions/28043/finding-the-z-value-on-a-plane-with-x-y-values - https://www.youtube.com/watch?v=gPnWm-IXoAY - https://www.youtube.com/watch?v=JCx3jeIhBr0 - https://www.w3schools.com/python/ref_math_isclose.asp - https://www.w3schools.com/python/ref_string_isnumeric.asp - most likely many more geeks4geeks, freecodecamp.org, and w3schools.com pages that have been lost due to accidental computer shutdowns/accidentally closing windows

The graphics window used is from the graphics.py import by John Zelle, and this project wouldn't have been possible without it

Finally, I would like to thank you for choosing to investigate my project.

If you would like a guide, then please visit the project page on the Summer of Hacking Website. GitHub and videos do not mix well.
