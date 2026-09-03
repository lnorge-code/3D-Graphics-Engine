"""
ABOUT THIS CODE:

This code is an attempt at making a highly simplified graphics engine with the help of the graphics.py import

The code contains all of the relevant functionality for:
    -points, triangles, and other shapes formed by combining said triangles
    -transforming points belonging to any shape in accordance with the viewing
fustrum as described in the YouTube video (https://www.youtube.com/watch?v=U0_ONQQ5ZNM)
and the "explanation" text document
    -rasterizing the newly transformed triangles by drawing bounding boxes around each
triangle and using math for the intersections of planes and vectors
    -a input/output loop allowing for the user to define their own shapes, transform, or
delete them, after which the window will be re-drawn

A more detailed explanation of how to interact with the code is available in the file "README.txt"
A more in-depth explanation of how the code works is available in "explanation.txt"
"""
# importing graphics to be able to draw to a window, and math for some of it's built in functions
import graphics
import math

# class to store all the values of the vertices of each triangle, both original and transformed
class point:
    # a classwide list for all of the points created
    pointList = []
    def __init__(self, realX, realY, realZ):
        # both real and transformed values for x, y, and z are used (defaulted to the real ones but changed later)
        self.realX = realX
        self.realY = realY
        self.realZ = realZ
        self.transformedX = realX # transformed X, Y, and Z values will default to the real values
        self.transformedY = realY
        self.transformedZ = realZ
        self.rotation = [0, 0, 0] # each value in these arrays corresponds to the rotation/translation/scaling about the x, y, and z axes respectively
        self.translation = [0, 0, 0]
        self.scale = [1, 1, 1]
        self.pointList.append(self) # adds the point created to the list
    
    # a repr which outputs all attributes of the point
    def __repr__(self):
        return str(self.transformedX) + ", " + str(self.transformedY) + ", " + str(self.realZ)
    
    def transformToPerspective(self):
        # pre-frustum values for x, y, and z so that we don't alter the real values again and again with each redraw when we don't want to
        tempX = self.realX
        tempY = self.realY
        tempZ = self.realZ

        # factoring in the scale
        tempX *= self.scale[0]
        tempY *= self.scale[1]
        tempZ *= self.scale[2]

        # rotations. Note that for the calculations I had to store variables so when one was set it wouldn't affect future calculations until after the rotation calculations are fully complete. I also made the calculations use negative values because otherwise my rotations would be counterclockwise
        # NOTE: the rotation array inputted by the user will be applied in order of x -> y -> z, which is important as rotations are non-communicative so this order must be factored in.
        # NOTE: the rotations are also applied relative to the world rather than locally, making it ideal to center objects along the origin so they aren't moved behind/outside the view field, and moving them later
        yPrime = tempZ * math.sin(0 - math.radians(self.rotation[0])) + tempY * math.cos(0 - math.radians(self.rotation[0])) # x rotation
        zPrime = tempZ * math.cos(0 - math.radians(self.rotation[0])) - tempY * math.sin(0 - math.radians(self.rotation[0]))
        tempY = yPrime
        tempZ = zPrime

        xPrime = tempX * math.cos(0 - math.radians(self.rotation[1])) - tempZ * math.sin(0 - math.radians(self.rotation[1])) # y rotation
        zPrime = tempX * math.sin(0 - math.radians(self.rotation[1])) + tempZ * math.cos(0 - math.radians(self.rotation[1]))
        tempX = xPrime
        tempZ = zPrime

        xPrime = tempX * math.cos(0 - math.radians(self.rotation[2])) - tempY * math.sin(0 - math.radians(self.rotation[2])) # z rotation
        yPrime = tempX * math.sin(0 - math.radians(self.rotation[2])) + tempY * math.cos(0 - math.radians(self.rotation[2]))
        tempX = xPrime
        tempY = yPrime

        # translations
        tempX += self.translation[0]
        tempY += self.translation[1]
        tempZ += self.translation[2]

        # finally the frustum can be applied and saved to new variables
        # the original math used to find these transformations can be found in the video https://www.youtube.com/watch?v=U0_ONQQ5ZNM. The math in the video was intended for the Vulkan game engine, so involves the use of matrices. I have adapted my code to perform these calculations without matrices (more in explanation.txt).
        self.transformedX = tempX * (0.5 * frustumHeight / math.tan(0.5 * fov)) / abs(tempZ + 0.5 * frustumHeight / math.tan(0.5 * fov)) # NOTE: abs is in the denominator because if the point is far enough behind the window, it will have x and y values inverted from what they should be. We use abs here to make the denominator always be positive, which means they are always only scaled down, not inverted
        self.transformedY = tempY * (0.5 * frustumHeight / math.tan(0.5 * fov)) / abs(tempZ + 0.5 * frustumHeight / math.tan(0.5 * fov))
        
        # now translate the transformedX and Y by 250 to center them in the drawing window
        self.transformedX += 250
        self.transformedY += 250

        # finally, setting transformedZ to tempZ
        self.transformedZ = tempZ

# shape parent class to make creating other shape classes easier
class shape:
    # only attributes for the shape class are a pointslist so that you can set the rotation and position of a whole object, and a planeList to know what triangle objects must be deleted when an object is deleted
    def __init__(self, *points):
        self.pointList = list(points)
        self.planeList = []

# a triangle class to store multiple points, with methods to help with calculating later
class triangle(shape):
    triangleList = [] # list of every triangle made for later
    def __init__(self, p1, p2, p3, colour = "black"):
        shape.__init__(self, p1, p2, p3)
        self.p1 = p1 # point 1, 2, and 3
        self.p2 = p2
        self.p3 = p3
        self.colour = colour # the colour of the triangle
        self.triangleList.append(self) # adding the triangle to the triangleList
        self.planeList = [self] # adding itself to the planeList of the object
        self.xCP = None # these last four are the coefficients of the standard form equation for a plane and need to be calculated later (used to find the z value given an x and y coordinate later)
        self.yCP = None
        self.zCP = None
        self.k = None

    # a function to calculate the area given 3 points (used to make the pointWithin function below more readable)
    def area(self, p1, p2, p3):
        return abs((p1.transformedX * (p2.transformedY - p3.transformedY) + p2.transformedX * (p3.transformedY - p1.transformedY) + p3.transformedX * (p1.transformedY - p2.transformedY)) / 2)
    
    # a function to calculate whether a point is within the triangle
    def pointWithin(self, point):
        # checks if on triangle ABC point P is inside by seeing if the area of ABP, ACP, and BCP all add up to the area of the overall triangle
        # NOTE: when comparing them it uses the math.isclose method to add a small tolerance, because on really skinny triangles the pixel just barely doesn't exist inside which can cause the edges to look like dashed lines, so there needs to be some flexibility in the values it will accept. Most game engines will treat each pixel as an average of the raw colours of itself and surrounding pixels to get around this, but the engine is computationally expensive enough and this is a much simpler approach.
        if(math.isclose(self.area(self.p1, self.p2, point) + self.area(self.p1, self.p3, point) + self.area(self.p2, self.p3, point), self.area(self.p1, self.p2, self.p3), abs_tol=100)):
            return True
        return False
    
    # a function to calculate the coefficients of the plane equation for the triangle, called whenever one is created or transformed
    def calculatePlanarCoefficients(self):
        # With 3 points on the triangle, it creates a vector for AB and AC and calculates the cross product (I simplified it all in one step). With the cross product's equation (k = ax + by + cz) it plugs in one of the vertices to solve for k.
        # This gives us the coefficients of the standard form equation for the plane the triangle represents
        self.xCP = (self.p2.transformedY - self.p1.transformedY) * (self.p3.transformedZ - self.p1.transformedZ) - (self.p2.transformedZ - self.p1.transformedZ) * (self.p3.transformedY - self.p1.transformedY)
        self.yCP = -1 * ((self.p2.transformedX - self.p1.transformedX) * (self.p3.transformedZ - self.p1.transformedZ) - (self.p2.transformedZ - self.p1.transformedZ) * (self.p3.transformedX - self.p1.transformedX))
        self.zCP = (self.p2.transformedX - self.p1.transformedX) * (self.p3.transformedY - self.p1.transformedY) - (self.p2.transformedY - self.p1.transformedY) * (self.p3.transformedX - self.p1.transformedX)
        self.k = self.p1.transformedX * self.xCP + self.p1.transformedY * self.yCP + self.p1.transformedZ * self.zCP

    # a function which uses the x and y values and some math to calculate where a point on the triangle is on the z axis
    def calculateZ(self, x, y):
        # two exceptions occur: 1. if xCP, yCP, and zCP are all 0 that means the points don't form a plane (two vectors are parralell, this triangle is a line) 2. If just zCP is 0 that means there isn't a unique value of z that goes with the x and y values inputted (the plane is perfectly aligned with the window, there will either be no working value (will not arise here because we already checked if the value contacts the triangle) or infinitely many)
        if(self.zCP == 0):
            if(self.xCP == 0 and self.yCP == 0): # if all are 0 then it is a line so we need to calculate z assuming it is a 3D line
                if(self.p2.transformedX - self.p1.transformedX == 0 and self.p2.transformedY - self.p1.transformedY == 0 and self.p2.transformedZ - self.p1.transformedZ == 0): # one error can occur if two points of the triangle lie on top of each other, and would as such create a line of 0, 0, 0. We just have to use another line
                    return self.zWithLine(x, y, self.p1, self.p3)    
                return self.zWithLine(x, y, self.p1, self.p2)
            else: # If just the z of the cross product is 0 there is infinite solutions for the plane (so we must plug in the minimum z value for each of the lines forming that triangle, or 0 if the triangle intersects the viewing plane)
                # for there to be multiple z values that work the plane must be perfectly in line with the camera. This means we can just use the closest z value for each line comprising our triangle at x, y
                return max(min(self.zWithLine(x, y, self.p1, self.p2), self.zWithLine(x, y, self.p1, self.p3), self.zWithLine(x, y, self.p2, self.p3)), 0) # returns the maximum of the minimum z value of each line and 0 (so that if it intersects the viewing plane it will draw it as being right on the plane)
        return (self.k - x * self.xCP - y * self.yCP) / self.zCP

    # a function which uses the x and y values and some math to calculate where a point on a triangle is on the z axis, in the event the triangle is actually a line
    def zWithLine(self, x, y, p1, p2):
        # NOTE: normally, I would have to check that the x and y value given lies along the line, but it is guaranteed to be on the line, or at least be very close to it, as we check if it lies on the triangle ahead of time
        # note that the equations I found work with only one variable plugged in. This means that if a line is vertical we can plug in the y instead to get a working value
        if(math.isclose(p2.transformedX - p1.transformedX, 0, abs_tol=1)): # If lineX is 0 that means it's vertical and can't be found using the x coordinate, so we can use y instead
            if(p2.transformedY - p1.transformedY == 0): # if both of them are on top of each other, will just return the z of one of them. I've taken steps so this shouldn't be a problem, but just in case
                return p2.transformedZ
            z = p1.transformedZ + ((p2.transformedZ - p1.transformedZ) * (y - p1.transformedY) / (p2.transformedY - p1.transformedY)) # a formula found by rearranging the equation for 3D lines
        else: # otherwise use the x coordinate
            z = p1.transformedZ + ((p2.transformedZ - p1.transformedZ) * (x - p1.transformedX) / (p2.transformedX - p1.transformedX)) # a formula found by rearranging the equation for 3D lines
        return z

# rectangular prism that takes two corner vertices and stretches out the faces between them
class rectangularPrism(shape):
    def __init__(self, fBL, bTR, colour = "black"):
        self.bottomLeftFront = fBL
        self.topRightBack = bTR
        fBR = point(bTR.realX, fBL.realY, fBL.realZ) # names go in order of front/back, top/bottom, left/right
        fTR = point(bTR.realX, bTR.realY, fBL.realZ)
        fTL = point(fBL.realX, bTR.realY, fBL.realZ)
        bTL = point(fBL.realX, bTR.realY, bTR.realZ)
        bBL = point(fBL.realX, fBL.realY, bTR.realZ)
        bBR = point(bTR.realX, fBL.realY, bTR.realZ)
        shape.__init__(self, fBL, fTR, fTL, bTL, bBL, bBR, fBR, bTR)
        # this next line is responsible for creating and storing the triangles related to the front, right, left, top, bottom, and back faces respectively
        self.planeList = quadrilateral(fTL, fTR, fBL, fBR, colour).planeList + quadrilateral(fTR, bTR, fBR, bBR, colour).planeList + quadrilateral(bTL, fTL, bBL, fBL, colour).planeList + quadrilateral(bTL, bTR, fTL, fTR, colour).planeList + quadrilateral(bBL, bBR, fBL, fBR, colour).planeList + quadrilateral(bTL, bTR, bBL, bBR, colour).planeList
    
    def __repr__(self):
        return "rectangular prism with corners " + self.bottomLeftFront.__repr__() + " and " + self.topRightBack.__repr__()

# quadrilateral class that makes a simple quadrilateral given 4 points for bottom left, right, and top left and right values
class quadrilateral(shape):
    def __init__(self, topLeft, topRight, bottomLeft, bottomRight, colour = "black"):
        shape.__init__(self, topLeft, topRight, bottomLeft, bottomRight)
        # this next line is responsible for both creating the surfaces needed and storing the list of triangles for when the object is deleted
        self.planeList = triangle(topLeft, bottomLeft, topRight, colour).planeList + triangle(bottomRight, bottomLeft, topRight, colour).planeList

# class that makes a square-based pyramid with 4 triangles and a quadrilateral
class squareBasedPyramid(shape):
    def __init__(self, baseTopLeft, baseTopRight, baseBottomLeft, baseBottomRight, tip, colour = "black"):
        shape.__init__(self, baseBottomLeft, baseBottomRight, baseTopLeft, baseTopRight, tip)
        self.planeList = quadrilateral(baseTopLeft, baseTopRight, baseBottomLeft, baseBottomRight, colour).planeList + triangle(baseTopLeft, baseTopRight, tip, colour).planeList + triangle(baseTopLeft, baseBottomLeft, tip, colour).planeList + triangle(baseBottomLeft, baseBottomRight, tip, colour).planeList + triangle(baseBottomRight, baseTopRight, tip, colour).planeList

def canFloat(num): # a function which uses a try-except block to check if a string can be converted to a float
    try: # tries to convert to a float and returns true if it could
        float(num)
        return True
    except (ValueError, TypeError): # if it couldn't simply returns false
        return False

def promptPoint(positionLabel = None): # prompts user to enter coordinates for a point and returns the point
    coordinates = None # default value
    numeric = False # a boolean to track if every value given is numeric to avoid errors

    # splits, strips, and converts every value to a float within this loop
    while numeric is False:
        numeric = True
        if(coordinates is None): # base case
            if(positionLabel is None): #position label so you can dynamically enter the name of a point using this same function
                coordinates = input("Please input the coordinates of a vertice on your shape separated by commas:\n")
            else:
                coordinates = input("Please input the coordinates of the " + positionLabel + " vertice of your shape separated by commas:\n")
        else: # if they typed it in wrong
            if(positionLabel is None): #position label so you can dynamically enter the name of a point using this same function
                coordinates = input("Misunderstood, please input the coordinates of a vertice on your shape separated by commas:\n")
            else:
                coordinates = input("Misunderstood, please input the coordinates of the " + positionLabel + " vertice of your shape separated by commas:\n")
        coordinateList = coordinates.split(",") # a list containing each coordinate for x, y, and z for the current coordinate
        for i in range(0, min(len(coordinateList), 3)): # only need to check up until the list ends or the first three values, whichever comes first
            coordinateList[i] = coordinateList[i].strip() # I didn't know this at first but strip intelligently removes trailing values from both ends if you leave it empty
            if(canFloat(coordinateList[i]) is False): # checking if the value can be converted to a float using the canFloat function we created
                numeric = False
            else:
                coordinateList[i] = float(coordinateList[i]) # converting to a float for calculations, but only if the value is numeric
        while len(coordinateList) < 3: # if user enters too little, fill with 0s. if user enters too much, it's okay because it uses the first three, otherwise it must fill the rest with 0's
            coordinateList.append(0)
    print("Point created!")
    return point(coordinateList[0], coordinateList[1], coordinateList[2]) # returning the new point

colourSet = {"red","blue","green","yellow","magenta","cyan","black","white","gray","orange","purple","brown"} # a set containing the names of the colours so that I can quickly look through them in the following function
def promptColour(): # prompts the user to select a colour for the shape
    colour = None # default values
    numeric = False
    while(colour not in colourSet and numeric is False):
        if colour is None: # base case
            colour = input("Please enter a colour (either enter the name or the rgb value separated by commas):\n")
        else: # something actually went wrong
            colour = input("Misunderstood, please try entering another colour (either enter the name or the rgb value separated by commas):\n")
        colour = colour.lower()
        if(colour not in colourSet): # if it's not a graphics.py colour, split, strip, and check if it is numeric, setting the bool tracking if it's an rgb value to false if it isn't
            rgbList = colour.split(",")
            numeric = True # bool for checking if the string inputted can be used for rgb inputs in the event the colour isn't built-in
            for i in range(0, min(len(rgbList), 3)): # only needs to check every value in the list until the 3rd
                rgbList[i] = rgbList[i].strip() # I didn't know this at first but strip intelligently removes trailing values from both ends if you leave it empty
                if(rgbList[i].isnumeric() is False): # note that while I would try to avoid isnumeric because it doesn't work with floats, the function can only take integers anyways
                    numeric = False
                else:
                    rgbList[i] = int(rgbList[i]) # converts the value to an int for calculations if it is possible
            while len(rgbList) < 3: # if the user enter too little, fill with 0s. If the user enters too much, it's fine because only the first three values are used
                rgbList.append(0)
            if(numeric is True): # if numeric is still true then it returns the colour
                return graphics.color_rgb(rgbList[0], rgbList[1], rgbList[2])
        else:
            return colour        

def promptTransformation(type = None): # prompts the user to enter the transformation type passed in by the type parameter and returns a list the main code loop can pass to the correct transformation on every point on the shape in the main loop
    magnitudes = None # default value
    numeric = False # a boolean to track if every value given is numeric to avoid errors
    
    # splits, strips, and converts every value to a float within this loop
    while numeric is False:
        numeric = True
        if(magnitudes is None): # base case
            if(type is None): #position label so you can dynamically enter the name of a point using this same function
                magnitudes = input("Please input the magnitude of the transformation along each axis (separated by commas):\n")
            else:
                magnitudes = input("Please input the magnitude of the " + type + " along each axis (separated by commas):\n")
        else: # if they typed it in wrong
            if(type is None): #position label so you can dynamically enter the name of a point using this same function
                magnitudes = input("Misunderstood, please input the magnitude of the transformation along each axis (separated by commas):\n")
            else:
                magnitudes = input("Misunderstood, please input the magnitude of the " + type + " along each axis (separated by commas):\n")
        magnitudeList = magnitudes.split(",") # a list containing each coordinate for x, y, and z for the current coordinate
        for i in range(0, min(len(magnitudeList), 3)): # only need to check up until the list ends or the first three values, whichever comes first
            magnitudeList[i] = magnitudeList[i].strip() # I didn't know this at first but strip intelligently removes trailing values from both ends if you leave it empty
            if(canFloat(magnitudeList[i]) is False): # checking if the value can be converted to a float using the canFloat function we created
                numeric = False
            else:
                magnitudeList[i] = float(magnitudeList[i]) # converting to a float for calculations, but only if the value is numeric
        while len(magnitudeList) < 3: # if user enters too little, fill with 0s. if user enters too much, it's okay because it uses the first three, otherwise it must fill the rest with 0's
            magnitudeList.append(0)
    return magnitudeList[0:3] # returning a new list containing the first three values of magnitudeList

def redrawWindow():
    pointDict = {} # a special use of dictionaries which stores a colour and z value for every x and y position for the purpose of comparing z values (z-buffering)

    global win
    win.close() # closing the window to clear everything that was done before
    win = graphics.GraphWin("3D Engine", 500, 500, autoflush=False) # opening the window again
    
    print("Beginning new render...")
        
    for i in triangle.triangleList:
        maxX = round(max(i.p1.transformedX, i.p2.transformedX, i.p3.transformedX)) # have to round our boundaries because the range function only takes ints
        minX = round(min(i.p1.transformedX, i.p2.transformedX, i.p3.transformedX))
        maxY = round(max(i.p1.transformedY, i.p2.transformedY, i.p3.transformedY))
        minY = round(min(i.p1.transformedY, i.p2.transformedY, i.p3.transformedY))
        for j in range(max(0, minY), min(501, maxY + 1)): # using min and max to frame it at either the triangle boundary or the screen (This way we only have to add constraints to the z value)
            for k in range(max(0, minX), min(501, maxX + 1)): # iterates through j (y) and k (x) checking if the pixel is inside the triangle, and calculating the z
                if(i.pointWithin(point(k, j, 1))): # make sure to set the z value to 1 for no distortion (although I don't think it matters)
                    z = i.calculateZ(k, j)
                    if(0 <= z and z <= 250):
                        if(k in pointDict.keys()): 
                            if(j in pointDict[k].keys()):
                                if(pointDict[k][j] > z):
                                    win.plotPixel(k, win.height - j, i.colour) # NOTE: here it draws the point read at the window's height - y to make the window look as if it's in the 1st quadrant
                                    pointDict[k][j] = z
                            else:
                                win.plotPixel(k, win.height - j, i.colour) # NOTE: here it draws the point read at the window's height - y to make the window look as if it's in the 1st quadrant
                                pointDict[k][j] = z
                        else:
                            win.plotPixel(k, win.height - j, i.colour)
                            pointDict[k] = dict() # This tells it that there is a new dictionary item in the dictionary, which allows me to add without it removing old data
                            pointDict[k][j] = z # setting the dict values

    for i in triangle.triangleList: # parsing through each triangle and drawing a wireframe after it's displayed
        l1 = graphics.Line(graphics.Point(i.p1.transformedX, win.height - i.p1.transformedY), graphics.Point(i.p2.transformedX, win.height - i.p2.transformedY))
        l2 = graphics.Line(graphics.Point(i.p1.transformedX, win.height - i.p1.transformedY), graphics.Point(i.p3.transformedX, win.height - i.p3.transformedY))
        l3 = graphics.Line(graphics.Point(i.p2.transformedX, win.height - i.p2.transformedY), graphics.Point(i.p3.transformedX, win.height - i.p3.transformedY))
        l1.draw(win)
        l2.draw(win)
        l3.draw(win)

    win.flush() # tells the window to update (reminder: autoflush is off) only after every draw order is made
    print("window updated")

# graphics.py window and global variables
win = graphics.GraphWin("3D Engine", 500, 500, autoflush=False) # the graphics window. NOTE autoflush is disabled because otherwise it repeatedly stops recieving draw commands in order to re-draw the window. While this has it's uses, it is better for my purposes if the window only updates at the end
frustumWidth = 500 # the height and width of the near plane of the frustum (https://www.youtube.com/watch?v=U0_ONQQ5ZNM)
frustumHeight = 500
fov = 60 * math.pi / 180 # the fov of the window has to be converted to radians otherwise it's wrong

pointDict = {} # a special use of dictionaries I came up with. acts like a matrix where you search the x, then the y, and can access both the z value from previous writes and it's colour. Looks like this: {x:{y1: [z1, colour1], y2: [z2, colour2]}}

# this is the cycle of prompting the user can go through
shapeDict = {} # a dictionary of every shape so they can be accessed later
prompt = 1
while True:
    if(prompt > 5 or prompt <= 0): # informing the user they entered something wrong if the prompt is not 1-5
        print("Error, nonexistent command selected")
    prompt = input("Please enter the number of the command you want to run:\n1. create an object\n2. rotate an object\n3. reposition object\n4. scale object\n5. delete shape\n\nselected command: ")
    while(prompt.isnumeric() is False): # ensuring that prompt is a valid integer
        prompt = input("Error, command must be a valid integer:\n1. create an object\n2. rotate an object\n3. reposition object\n4. scale object\n5. delete shape\n\nselected command: ")
    prompt = int(prompt) # converting prompt to an integer
    if(prompt == 1): # create shape
        shapeType = int(input("Please input the number of the shape you wish to create:\n1. triangle\n2. quadrilateral\n3. rectangular prism\n4. square-based pyramid\nselected shape: "))
        while shapeType <= 0 or shapeType > 5:
            print("Error, nonexistent shape selected")
            shapeType = int(input("Please input the number of the shape you wish to create:\n1. triangle\n2. quadrilateral\n3. rectangular prism\n4. square-based pyramid\nselected shape: "))
        if(shapeType == 1): # triangle
            p1 = promptPoint() # using the prompPoint function to save space
            p2 = promptPoint()
            p3 = promptPoint()
            colour = promptColour()
            name = input("Please enter a name for the triangle you created so you can access it later:\n")
            while name in shapeDict:
                name = input("Another shape shares that name. Please select another:\n")
            shapeDict[name] = triangle(p1, p2, p3, colour)
        elif(shapeType == 2): # quadrilateral
            p1 = promptPoint("bottom left")
            p2 = promptPoint("bottom right")
            p3 = promptPoint("top left")
            p4 = promptPoint("top right")
            colour = promptColour()
            name = input("Please enter a name for the quadrilateral you created so you can access it later:\n")
            while name in shapeDict:
                name = input("Another shape shares that name. Please select another:\n")
            shapeDict[name] = quadrilateral(p3, p4, p1, p2, colour)
        elif(shapeType == 3): # rectangular prism
            p1 = promptPoint("corner")
            p2 = promptPoint("opposite corner")
            colour = promptColour()
            name = input("Please enter a name for the rectangular prism you created so you can access it later:\n")
            while name in shapeDict:
                name = input("Another shape shares that name. Please select another:\n")
            shapeDict[name] = rectangularPrism(p1, p2, colour)
        elif(shapeType == 4): # square-based pyramid
            p1 = promptPoint("tip") # gathering every point along the pyramid
            p2 = promptPoint("bottom left")
            p3 = promptPoint("bottom right")
            p4 = promptPoint("top left")
            p5 = promptPoint("top right")
            colour = promptColour()
            name = input("Please enter a name for the pyramid you created so you can access it later:\n")
            while name in shapeDict:
                name = input("Another shape shares that name. Please select another:\n")
            shapeDict[name] = squareBasedPyramid(p4, p5, p2, p3, p1, colour)
        for i in shapeDict[name].pointList: # iterating through the pointlist and transforming them
            i.transformToPerspective()
        for i in shapeDict[name].planeList: # iterating through the planelist and calculating the planar equation coefficients
            i.calculatePlanarCoefficients()
        redrawWindow() # redrawing window
    elif(prompt == 2): # set rotation
        if(len(shapeDict) == 0):
            print("Error: no shapes available to rotate")
            continue
        name = input("Please enter the name of the shape you would like to rotate:\n")
        while name not in shapeDict:
            name = input("Shape not found, please try again:\n")
        rotationList = promptTransformation("rotation") # goes through the prompting loop with a label of "rotation"
        for i in shapeDict[name].pointList: # assigning the rotationList to the rotation value of each point in the shape. Doesn't matter if the values are greater than 3 because only the first three are used ever
            i.rotation = rotationList
            i.transformToPerspective()
        for i in shapeDict[name].planeList: # iterating through the planelist and calculating the planar equation coefficients
            i.calculatePlanarCoefficients()
        redrawWindow() # redrawing window
    elif(prompt == 3): # set translation
        if(len(shapeDict) == 0):
            print("Error: no shapes available to translate")
            continue
        name = input("Please enter the name of the shape you would like to set the position of:\n")
        while name not in shapeDict:
            name = input("Shape not found, please try again:\n")
        positionList = promptTransformation("translation") # goes through the prompting loop with a label of "translation"
        for i in shapeDict[name].pointList: # assigning the positionList to the rotation value of each point in the shape. Doesn't matter if the values are greater than 3 because only the first three are used ever
            i.translation = positionList
            i.transformToPerspective()
        for i in shapeDict[name].planeList: # iterating through the planelist and calculating the planar equation coefficients
            i.calculatePlanarCoefficients()
        redrawWindow() # redrawing window
    elif(prompt == 4): # set scale
        if(len(shapeDict) == 0):
            print("Error: no shapes available to scale")
            continue
        name = input("Please enter the name of the shape you would like to set the scale of:\n")
        while name not in shapeDict:
            name = input("Shape not found, please try again:\n")
        scaleList = promptTransformation("scale") # goes through the prompting loop with a lael of "scale"
        for i in shapeDict[name].pointList: # assigning the scaleList to the rotation value of each point in the shape. Doesn't matter if the values are greater than 3 because only the first three are used ever
            i.scale = scaleList
            i.transformToPerspective()
        for i in shapeDict[name].planeList: # iterating through the planelist and calculating the planar equation coefficients
            i.calculatePlanarCoefficients()
        redrawWindow() # redrawing window
    else: # delete object
        if(len(shapeDict) == 0):
            print("Error: no shapes available to delete")
            continue
        name = input("Please enter the name of the shape you would like to delete:\n")
        while name not in shapeDict:
            name = input("Shape not found, please try again:\n")
        for i in shapeDict[name].planeList: # iterates through all of the planes of the shape and removes them from the triangle list so they aren't drawn anymore
            triangle.triangleList.remove(i)
        del shapeDict[name] # after that is done, removes the object reference from the dictionary so the name is free and the shape is no longer accessed anymore
        redrawWindow()