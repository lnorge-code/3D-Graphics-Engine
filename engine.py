"""
step 1: making a class for both points and triangles
Step 2: making a canonical viewing volume (-1 to 1, -1 to 1, 0 to 1)
step 3: rasterize and output to graphics.py
step 4: add transformations to every point for the orthographic view volume, square frustum, and rotations
"""
import graphics
import math

# class to store all the values of the vertices of each triangle, both original and transformed
class point:
    # a classwide list for all of the points created
    pointList = []
    def __init__(self, realX, realY, realZ):
        # both real and transformed values (defaulted to the real ones but changed later)
        self.realX = realX
        self.realY = realY
        self.realZ = realZ
        self.transformedX = realX # transformed X and Y values will by default be the same as the real values because there are many times I need to use this class after these values are calculated and python won't like nonetypes in this location
        self.transformedY = realY
        self.transformedZ = realZ
        self.rotation = [0, 0, 0]
        self.translation = [0, 0, 0]
        self.scale = [1, 1, 1]
        self.pointList.append(self) # adds the point created to the list
    
    # a repr which outputs all attributes of the point
    def __repr__(self):
        return str(self.transformedX) + ", " + str(self.transformedY) + ", " + str(self.transformedZ)
    
    def transformToPerspective(self):
        # factoring in the scale. NOTE: if we were scaling the view volume/frustum, it should be /=. But, because I am letting the user mess with the scale themselves, it's more intuitive if the opposite occurs, scaling every shape instead
        self.realX *= self.scale[0]
        self.realY *= self.scale[1]
        self.realZ *= self.scale[2]

        # rotations. Note that for the calculations I had to store variables so when one was set it wouldn't affect future calculations until after the rotation calculations are fully complete. I also made the calculations use negative values because otherwise my rotations would be counterclockwise
        yPrime = self.realZ * math.sin(0 - self.rotation[0]) + self.realY * math.cos(0 - self.rotation[0]) # x rotation
        zPrime = self.realZ * math.cos(0 - self.rotation[0]) - self.realY * math.sin(0 - self.rotation[0])
        self.realY = yPrime
        self.realZ = zPrime

        xPrime = self.realX * math.cos(0 - self.rotation[1]) - self.realZ * math.sin(0 - self.rotation[1]) # y rotation
        zPrime = self.realX * math.sin(0 - self.rotation[1]) + self.realZ * math.cos(0 - self.rotation[1])
        self.realX = xPrime
        self.realZ = zPrime

        xPrime = self.realX * math.cos(0 - self.rotation[2]) - self.realY * math.sin(0 - self.rotation[2]) # z rotation
        yPrime = self.realX * math.sin(0 - self.rotation[2]) + self.realY * math.cos(0 - self.rotation[2])
        self.realX = xPrime
        self.realY = yPrime

        # translations
        self.realX += self.translation[0]
        self.realY += self.translation[1]
        self.realZ += self.translation[2]

        # finally the frustum can be applied and saved to new variables
        self.transformedX = self.realX * (0.5 * frustrumWidth / math.tan(0.5 * fov)) / (self.realZ + 0.5 * frustrumWidth / math.tan(0.5 * fov))
        self.transformedY = self.realY * (0.5 * frustrumHeight / math.tan(0.5 * fov)) / (self.realZ + 0.5 * frustrumHeight / math.tan(0.5 * fov))

        # now translate the transformedX and Y by 250 to center it in the drawing window
        self.transformedX += 250
        self.transformedY += 250
        self.transformedZ = self.realZ

# shape parent class to make creating other shape classes easier
class shape:
    # only attribute of the shape class is a pointslist so that you can set the rotation and position of a whole object
    def __init__(self, *points):
        self.pointList = list(points)

    def setRotation(self, newRotation):
        for i in self.pointList:
            i.rotation = newRotation
    
    def setPosition(self, newPosition):
        for i in self.pointList:
            i.translation = newPosition

# a triangle class to store multiple points, with methods to help with calculating later
class triangle(shape):
    triangleList = [] # list of every triangle made for later
    def __init__(self, p1, p2, p3, colour = "black"):
        shape.__init__(self, p1, p2, p3)
        self.p1 = p1 # point 1, 2, and 3
        self.p2 = p2
        self.p3 = p3
        self.colour = colour
        self.triangleList.append(self)
        self.xCP = None # these last four need to be calculated later (used to find the z value given an x and y coordinate later)
        self.yCP = None
        self.zCP = None
        self.k = None

    # a function to calculate the area given 3 points (used to make the pointWithin function below more readable)
    def area(self, p1, p2, p3):
        return abs((p1.transformedX * (p2.transformedY - p3.transformedY) + p2.transformedX * (p3.transformedY - p1.transformedY) + p3.transformedX * (p1.transformedY - p2.transformedY)) / 2)
    
    # a function to calculate whether a point is within the triangle
    def pointWithin(self, point):
        # checks if on triangle ABC point P is inside by seeing if the area of ABP, ACP, and BCP all add up to the area of the overall triangle
        # NOTE: when comparing them it uses the math.isclose method to add a small tolerance, because on really skinny triangles the pixel just barely doesn't exist inside which can cause the edges to look like dashed lines, so there needs to be some flexibility in the values it will accept
        if(math.isclose(self.area(self.p1, self.p2, point) + self.area(self.p1, self.p3, point) + self.area(self.p2, self.p3, point), self.area(self.p1, self.p2, self.p3), abs_tol=100)):
            return True
        return False
    
    # a function which uses the x and y values and some math to calculate where a point on the triangle is on the z axis
    def calculateZ(self, x, y): # NOTE: we add tolerance in the pointWithin function but not this one DOESN'T MATTER FOR PLANES, BUT ADD AN ADDITIONAL CHECK IF THE CALCULATED X EXISTS ON THE LINE AND IF IT DOESN"T USE THE Y
        if(self.xCP is None): # only really need to check if one is missing because it will assign them all
            # This is some vector and matrix math which I recommend looking at the math help sources to understand
            # Basically, with 3 points on the triangle, it creates a vector for AB and AC and calculates the cross product (I simplified it all in one step). With the cross product's equation (k = ax + by + cz) it plugs in one of the vertices to solve for k. Now it has all the variables stored that it needs to solve for z
            # I highly recommend looking at the cross product math help video to understand this math
            self.xCP = (self.p2.transformedY - self.p1.transformedY) * (self.p3.transformedZ - self.p1.transformedZ) - (self.p2.transformedZ - self.p1.transformedZ) * (self.p3.transformedY - self.p1.transformedY)
            self.yCP = -1 * ((self.p2.transformedX - self.p1.transformedX) * (self.p3.transformedZ - self.p1.transformedZ) - (self.p2.transformedZ - self.p1.transformedZ) * (self.p3.transformedX - self.p1.transformedX))
            self.zCP = (self.p2.transformedX - self.p1.transformedX) * (self.p3.transformedY - self.p1.transformedY) - (self.p2.transformedY - self.p1.transformedY) * (self.p3.transformedX - self.p1.transformedX)
            self.k = self.p1.transformedX * self.xCP + self.p1.transformedY * self.yCP + self.p1.transformedZ * self.zCP
        # two exceptions occur: 1. if xCP, yCP, and zCP are all 0 that means the points don't form a plane (two vectors are parralell) 2. If just zCP is 0 that means there isn't a unique value of z that goes with the x and y values inputted (either no working value or multiple)
        if(self.zCP == 0):
            if(self.xCP == 0 and self.yCP == 0): # if all are 0 then it is a line so we need to calculate z assuming it is a 3D line
                if(self.p2.transformedX - self.p1.transformedX == 0 and self.p2.transformedY - self.p1.transformedY == 0 and self.p2.transformedZ - self.p1.transformedZ == 0): # one error can occur if two points of the triangle lie on top of each other, and would as such create a line of 0, 0, 0. We just have to use another line
                    return self.zWithLine(x, y, self.p1, self.p3)    
                return self.zWithLine(x, y, self.p1, self.p2)
            else: # If just the z of the cross product is 0 and there is either no valid z values or there is multiple
                # NOTE: the web forum claimed there could be no value of z that works, but I'm fairly certain this won't occur with the planes that we're working with, so on to the next case:
                # for there to be multiple z values that work the plane must be perfectly in line with the camera. This means we can just use the closest z value for each line comprising our triangle at x, y
                return min(self.zWithLine(x, y, self.p1, self.p2), self.zWithLine(x, y, self.p1, self.p3), self.zWithLine(x, y, self.p2, self.p3))
        return (self.k - x * self.xCP - y * self.yCP) / self.zCP

    def zWithLine(self, x, y, p1, p2):
        # note that the equations I found work with only one variable plugged in. This means that if a line is vertical we can plug in the y instead to get a working value
        if(math.isclose(p2.transformedX - p1.transformedX, 0, abs_tol=1)): # If lineX is 0 that means it's vertical and can't be found using the x coordinate, so we can use y instead
            if(p2.transformedY - p1.transformedY == 0): # both of them are on top of each other. This shouldn't be a problem, yet here we are
                return p2.transformedZ
            z = p1.transformedZ + ((p2.transformedZ - p1.transformedZ) * (y - p1.transformedY) / (p2.transformedY - p1.transformedY)) # a formula I worked out following the equations of 3D lines video
        else: # otherwise use the x coordinate
            z = p1.transformedZ + ((p2.transformedZ - p1.transformedZ) * (x - p1.transformedX) / (p2.transformedX - p1.transformedX)) # a formula I worked out following the equations of 3D lines video
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
        quadrilateral(fTL, fTR, fBL, fBR, colour) # front face
        quadrilateral(fTR, bTR, fBR, bBR, colour) # right face
        quadrilateral(bTL, fTL, bBL, fBL, colour) # left face
        quadrilateral(bTL, bTR, fTL, fTR, colour) # top face
        quadrilateral(bBL, bBR, fBL, fBR, colour) # bottom face
        quadrilateral(bTL, bTR, bBL, bBR, colour) # back
    
    def __repr__(self):
        return "rectangular prism with corners " + self.bottomLeftFront.__repr__() + " and " + self.topRightBack.__repr__()

# quadrilateral class that makes a simple quadrilateral given 4 points for bottom left, right, and top left and right values
class quadrilateral(shape):
    def __init__(self, topLeft, topRight, bottomLeft, bottomRight, colour = "black"):
        shape.__init__(self, topLeft, topRight, bottomLeft, bottomRight)
        triangle(topLeft, bottomLeft, topRight, colour)
        triangle(bottomRight, bottomLeft, topRight, colour)

# class that makes a square-based pyramid with 4 triangles and a quadrilateral
class squareBasedPyramid(shape):
    def __init__(self, baseTopLeft, baseTopRight, baseBottomLeft, baseBottomRight, tip, colour = "black"):
        shape.__init__(self, baseBottomLeft, baseBottomRight, baseTopLeft, baseTopRight, tip)
        quadrilateral(baseTopLeft, baseTopRight, baseBottomLeft, baseBottomRight, colour)
        triangle(baseTopLeft, baseTopRight, tip, colour)
        triangle(baseTopLeft, baseBottomLeft, tip, colour)
        triangle(baseBottomLeft, baseBottomRight, tip, colour)
        triangle(baseBottomRight, baseTopRight, tip, colour)

def promptPoint(positionLabel = None): # prompts user to enter coordinates for a point and returns the point
    if(positionLabel is None): #position label so you can dynamically enter the name of a point using this same function
        coordinates = input("Please input the coordinates of a vertice on your shape separated by commas:\n")
    else:
        coordinates = input("Please input the coordinates of the " + positionLabel + " vertice of your shape separated by commas:\n")

    # splits, strips, and converts every value to a float
    coordinateList = coordinates.split(",") # a list containing each coordinate for x, y, and z for the current coordinate
    for i in range(0, len(coordinateList)):
        coordinateList[i] = coordinateList[i].strip() # I didn't know this at first but strip intelligently removes trailing values from both ends if you leave it empty
        coordinateList[i] = float(coordinateList[i]) # converting to a float for calculations
    while len(coordinateList) < 3: # if user enters too much, it's okay because it uses the first three, otherwise it must fill the rest with 0's
        coordinateList.append(0)
    print("Point created!")
    return point(coordinateList[0], coordinateList[1], coordinateList[2])

colourSet = {"red","blue","green","yellow","magenta","cyan","black","white","gray","orange","purple","brown"} # a set containing the names of the colours so that I can quickly look through them in the following function
def promptColour(): # prompts the user to select a colour for the shape
    colour = None # default values
    numeric = False
    while(colour not in colourSet and numeric is False):
        if colour is None: # base case
            colour = input("Please enter a colour (either enter the name or the rgb value separated by commas:\n")
        else: # something actually went wrong
            colour = input("Misunderstood, please try entering another colour (either enter the name or the rgb value separated by commas]):\n")
        colour = colour.lower()
        if(colour not in colourSet): # if it's not a graphics.py colour, split, strip, and check if it is numeric, setting the bool tracking if it's an rgb value to false if it isn't
            rgbList = colour.split(",")
            numeric = True # bool for checking if the string inputted can be used for rgb inputs in the event the colour isn't built-in
            for i in range(0, 2):
                rgbList[i] = rgbList[i].strip() # I didn't know this at first but strip intelligently removes trailing values from both ends if you leave it empty
                if(rgbList[i].isnumeric() is False): # note that while I would try to avoid isnumeric because it doesn't work with floats, the function can only take integers anyways
                    numeric = False
            if(numeric is True): # if numeric is still true then it returns the colour
                return graphics.color_rgb(int(rgbList[0]), int(rgbList[1]), int(rgbList[2]))
        else:
            return colour        

# graphics.py window
win = graphics.GraphWin("3D Engine", 500, 500)
frustrumWidth = 500
frustrumHeight = 500
fov = 60 * math.pi / 180 # has to be converted to radians otherwise it's wrong

pointDict = {} # a special use of dictionaries I came up with. acts like a matrix where you search the x, then the y, and can access both the z value from previous writes and it's colour. Looks like this: {x:{y1: [z1, colour1], y2: [z2, colour2]}}

# this is the cycle of prompting the user can go through
shapeDict = {} # a dictionary of every shape so they can be accessed later
prompt = 1
while prompt != 5:
    if(prompt > 5 or prompt <= 0):
        print("Error, nonexistent command selected")
    prompt = int(input("Please enter the number of the command you want to run:\n1. create an object\n2. rotate an object\n3. reposition object\n4. scale object\n5. run graphics generator\n\nselected command: "))
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
            p1 = promptPoint("tip")
            p2 = promptPoint("bottom left")
            p3 = promptPoint("bottom right")
            p4 = promptPoint("top left")
            p5 = promptPoint("top right")
            colour = promptColour()
            name = input("Please enter a name for the pyramid you created so you can access it later:\n")
            while name in shapeDict:
                name = input("Another shape shares that name. Please select another:\n")
            shapeDict[name] = squareBasedPyramid(p4, p5, p2, p3, p1, colour)
    elif(prompt == 2): # set rotation
        name = input("Please enter the name of the shape you would like to rotate:\n")
        while name not in shapeDict:
            name = input("Shape not found, please try again:\n")
        rotation = input("Please enter the new rotation of the shape separated by commas:\n")
        rotationList = rotation.split(",") # a list containing each coordinate for x, y, and z for the current coordinate
        for i in range(0, len(rotationList)):
            rotationList[i] = rotationList[i].strip() # I didn't know this at first but strip intelligently removes trailing values from both ends if you leave it empty
            rotationList[i] = float(rotationList[i]) # converting to a float for calculations
        while len(rotationList) < 3: # ensures that the rotationList is always 3 items at least
            rotationList.append(0)
        for i in shapeDict[name].pointList: # assigning the rotationList to the rotation value of each point in the shape. Doesn't matter if the values are greater than 3 because only the first three are used ever
            i.rotation = rotationList
    elif(prompt == 3): # set translation
        name = input("Please enter the name of the shape you would like to set the position of:\n")
        while name not in shapeDict:
            name = input("Shape not found, please try again:\n")
        position = input("Please enter the new position of the shape separated by commas:\n")
        positionList = position.split(",") # a list containing each coordinate for x, y, and z for the current coordinate
        for i in range(0, len(positionList)):
            positionList[i] = positionList[i].strip() # I didn't know this at first but strip intelligently removes trailing values from both ends if you leave it empty
            positionList[i] = float(positionList[i]) # converting to a float for calculations
        while len(positionList) < 3: # ensures that the positionList is always 3 items at least
            positionList.append(0)
        for i in shapeDict[name].pointList: # assigning the positionList to the rotation value of each point in the shape. Doesn't matter if the values are greater than 3 because only the first three are used ever
            i.translation = positionList
    elif(prompt == 4): # set scale
        name = input("Please enter the name of the shape you would like to set the scale of:\n")
        while name not in shapeDict:
            name = input("Shape not found, please try again:\n")
        scale = input("Please enter the new scale of the shape separated by commas:\n")
        scaleList = scale.split(",") # a list containing each coordinate for x, y, and z for the current coordinate
        for i in range(0, len(scaleList)):
            scaleList[i] = scaleList[i].strip() # I didn't know this at first but strip intelligently removes trailing values from both ends if you leave it empty
            scaleList[i] = float(scaleList[i]) # converting to a float for calculations
        while len(scaleList) < 3: # ensures that the scaleList is always 3 items at least
            scaleList.append(1) # NOTE: 1 in that case because that keeps it the same
        for i in shapeDict[name].pointList: # assigning the scaleList to the rotation value of each point in the shape. Doesn't matter if the values are greater than 3 because only the first three are used ever
            i.scale = scaleList
    else: # run
        break
for i in point.pointList:
    i.transformToPerspective()

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

print("render complete")
# stops the graphics window from closing automatically when the file completes
input()
