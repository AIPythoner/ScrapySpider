from zheye import zheye

z = zheye()
positions = z.Recognize('test.gif')
print(positions[0][1]/2,positions[0][0]/2)
print(positions[1][1]/2,positions[1][0]/2)

print('\n\n\n')

print(positions[0][0]/2,positions[0][1]/2)
print(positions[1][0]/2,positions[1][1]/2)