import math
from sys import argv
from PIL import Image

class Unshredder(object):
    def __init__(self, inputfilename, outputFilename):
        """
        class constructor.

        :param inputfilename: input filename to be read.
        :type filename: string
        :param outputFilename: Output filename to save the unshredded image.
        :type outputFilename: string
        """
        self.__inputFilename = inputfilename
        self.__outputFilename = outputFilename
        self.__load_image()

    def __load_image(self):
        """
        loads the image from the specified input file at 
        construction.
        """
        self.__image     = Image.open(self.__inputFilename)
        self.__imageSize = self.__image.size
        self.__imageData =     self.__image.getdata()
        self.__shredSize = 32
        self.__shredCount = self.__imageSize[0] / self.__shredSize

    def __get_pixel_value(self, x, y):
        """
        returns color value of the specified coordinate.

        :param x: horizontal coordinate of the pixel.
        :type x: integer
        :param y: vertical coordinate of the pixel.
        :type y: integer
        :return tuple
        """
        return self.__imageData[y * self.__imageSize[0] + x]

    def __calculate_pixel_difference(self, pixel1, pixel2):
        """
        calculates color difference between two pixels.

        :param pixel1: First pixel.
        :type pixel1: tuple
        :param :pixel2: Second pixel.
        :type pixel2: tuple
        :return float
        """
        return sum( [ (math.log(color1 / 255.0 + 1.0 / 255) - 
                       math.log(color2 / 255.0 + 1.0 / 255)) ** 2 
                       for color1, color2 in zip(pixel1, pixel2) ])
        # This algorithm is not working as properly.
        # return sum( [ abs(color1 - color2) for color1, color2 in zip(pixel1, pixel2) ] ) 

    def __compare_columns(self, col1, col2, diff = 0, y = 0):
        """
        compare the specified columns for color difference.

        :param col1: First shred. 
        :type col1: integer
        :param col2: Second shred.
        :type col2: integer
        """
        pixel1 = self.__get_pixel_value(col1 * self.__shredSize, y)
        pixel2 = self.__get_pixel_value(col2 * self.__shredSize + self.__shredSize - 1, y)
        diff += self.__calculate_pixel_difference(pixel1, pixel2)
        if y < self.__imageSize[1] - 1:
            y += 1
            return self.__compare_columns(col1, col2, diff,  y)
        else:
            return diff / self.__imageSize[1]

    def __compare(self):
        """
        compares all the columns with each other.
        
        :return list
        """
        edges = sorted([ (self.__compare_columns(col1, col2), col1, col2) 
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

    def __get_first_shred_index(self, sortedShreds, index = 0):
        """
        returns index of first shred.

        :param sortedShreds: Sorted shred list.
        :type sortedShreds: list
        :param index: last scanned index number. Used on recursive call. 
                       (default=0)
        :type index: integer
        :return integer
        """
        if sortedShreds[index][1] >= 0:
            index += 1
            return self.__get_first_shred_index(sortedShreds, index)
        else:
            return index

    def __create_image(self, sortedShreds, start):
        """
        creates unshredded image from the specified sorted shred list.

        :param sortedShreds: Sorted shred list.
        :type sortedShreds: list.
        :param start: First shred index.
        :type start: integer
        """
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
        """
        performs unshredding process.
        """
        sortedShreds = self.__compare()
        start        = self.__get_first_shred_index(sortedShreds)
        self.__create_image(sortedShreds, start)


if __name__ == '__main__':
    scriptName, inFile, outFile = argv
    unshredder = Unshredder(inFile, outFile)
    unshredder.make()

