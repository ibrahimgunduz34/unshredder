from PIL import Image
from sys import argv
import math

class Unshredder(object):
    def __init__(self, inputfilename, outputFilename):
        self.__inputFilename  = inputfilename
        self.__outputFilename = outputFilename
        self.__loadImage()

    def __loadImage(self):
        self.__image     = Image.open(self.__inputFilename)
        self.__imageSize = self.__image.size
        self.__imageData =     self.__image.getdata()
        self.__shredSize = 32
        self.__shredCount = self.__imageSize[0] / self.__shredSize

    def __getPixelValue(self, x, y):
        return self.__imageData[y * self.__imageSize[0] + x]

    def __calculatePixelDifference(self, pixel1, pixel2):
        return sum( [ (math.log(color1 / 255.0 + 1.0 / 255) - 
                       math.log(color2 / 255.0 + 1.0 / 255)) ** 2 
                       for color1, color2 in zip(pixel1, pixel2) ])
        # This algorithm is not working as properly.
        # return sum( [ abs(color1 - color2) for color1, color2 in zip(pixel1, pixel2) ] ) 

    def __compareColumns(self, col1, col2, diff = 0, y = 0):
        pixel1 = self.__getPixelValue(col1 * self.__shredSize, y)
        pixel2 = self.__getPixelValue(col2 * self.__shredSize + self.__shredSize - 1, y)
        diff += self.__calculatePixelDifference(pixel1, pixel2)
        if y < self.__imageSize[1] - 1:
            y += 1
            return self.__compareColumns(col1, col2, diff,  y)
        else:
            return diff / self.__imageSize[1]

    def __compare(self):
        edges = sorted([ (self.__compareColumns(col1, col2), col1, col2) 
                        for col1 in xrange(0, self.__shredCount) 
                            for col2 in xrange(0, self.__shredCount)
                                if col1 != col2 ])
        
        sortedShreds      = [[-1, -1] for i in xrange(0, self.__shredCount)]
        joinedShredCount = 0

        for diff, col1, col2 in edges:
            if sortedShreds[col1][1] < 0 and sortedShreds[col2][0] < 0:
                sortedShreds[col1][1] = col2
                sortedShreds[col2][0] = col1
                joinedShredCount += 1
                if joinedShredCount == self.__shredCount -1:
                    break

        return sortedShreds

    def __getFirstShredIndex(self, sortedShreds, index = 0):
        if sortedShreds[index][1] >= 0:
            index += 1
            return self.__getFirstShredIndex(sortedShreds, index)
        else:
            return index

    def __createNewImageFromSortedShreds(self, sortedShreds, start):
        newImage     = Image.new('RGB', self.__imageSize)
        sortedShreds = self.__compare()
        col1         = start
        
        for col2 in xrange(0, self.__shredCount):
            col1x1 = col1 * self.__shredSize
            col1x2 = col1x1 + self.__shredSize
            shred  = self.__image.crop((col1x1, 0, col1x2, self.__imageSize[1] -1))
            col2x1 = self.__shredSize * col2
            newImage.paste(shred, (col2x1, 0))
            col1 = sortedShreds[col1][0]
        
        newImage.save(self.__outputFilename, 'JPEG')

    def make(self):
        sortedShreds = self.__compare()
        start        = self.__getFirstShredIndex(sortedShreds)
        self.__createNewImageFromSortedShreds(sortedShreds, start)


if __name__ == '__main__':
    scriptName, inFile, outFile = argv
    unshredder = Unshredder(inFile, outFile)
    unshredder.make()

