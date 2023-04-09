"""
the Critic
the Critic compares how close two curves are to eachother.
the use of this is to take a desired tension curve, and compare it to the tension curve of a dynamically generated story/plan.
as of now it get's normalized on both x and y coordinates
"""

#linear algebra
def line(p1, p2, x):
    f = (p2[1] - p1[1]) / (p2[0] - p1[0])
    y = f* (p2[0] - x) - p2[1]
    return - y

#takes a set of points and linearly fills in points, between the points.
def curve_chopper(curve, N = 50):
    xline = []
    yline = []
    n = 1
    x1 = curve[0][0]
    x2 = curve[0][1]
    y1 = curve[1][0]
    y2 = curve[1][1]
    
    bigx = curve[0][len(curve[0]) -1]

    for x in range(N + 1):
        xstep = (x / N) * bigx
        
        if(xstep > x2):
            n +=1
            """
            if (n > len(curve[0]) -1):
                break
            """
            x1 = x2
            y1 = y2
            x2 = curve[0][n]
            y2 = curve[1][n]

        xline.append(xstep)
        yline.append(line((x1,y1), (x2,y2), xstep))

    return (xline,yline)

#takes a list of points and changes it's size to be between 0-1
def normalize_curve(ycurve, xcurve = []):
    maxy = max(ycurve)

    if(maxy == 0 and abs(min(ycurve)) == 0):
        maxy = 1
    elif (maxy < abs(min(ycurve))):
        maxy = abs(min(ycurve))

    if (len(ycurve) != len(xcurve)):
        maxx = len(ycurve) -1
        xcurve = [*range(maxx)]
        print("error in critic: uneven number of curve points")
    else:
        maxx = max(xcurve)
    if (maxx == 0):
        maxx = 1
    x = []
    y = []
    n = 0
    for point in ycurve:
        y.append(point/maxy)
        x.append(xcurve[n]/maxx)
        n+=1
    return x,y

#takes a list of ints and returns a relative list of floats valued between 0. and 1.
def normalize_int_list(l):
    maxi = max(l)

    if(maxi == 0 and abs(min(l)) == 0):
        maxi = 1

    result = []
    for i in l:
        result.append(i/maxi)

    return result


#uses previous functions to standerdize a list of points, by setting values to be between 0-1 and setting the no. of points to N
def standardize_curve(xcurve, ycurve, N = 50):
        return curve_chopper((normalize_curve(ycurve, xcurve)), N)

#compares two lists of points aka. tension curves, by standardizing them, and then seing how they compare. Lower is more alike
def curve_comparer(curve1, curve2, N = 50, normalize = 'both'):
    if normalize == 'both':
        sc1 = standardize_curve(curve1[0],curve1[1], N)
        sc2 = standardize_curve(curve2[0],curve2[1], N)
    else:
        sc1 = curve_chopper(curve1, N)
        sc2 = curve_chopper(curve2, N)

    result = 0
    for y in range(N + 1):
        result += abs(sc1[1][y] - sc2[1][y])

    return result/N

#test

"""
c1 = ([0,1,2,3],[0,1,2,3])
c2 = ([0,1],[0,1])
res = curve_comparer(c1,c2,10,True)
print(res)

"""