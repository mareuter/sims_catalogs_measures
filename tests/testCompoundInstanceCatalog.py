from __future__ import with_statement
import os
import numpy
import unittest
import lsst.utils.tests as utilsTests
from lsst.utils import getPackageDir
from lsst.sims.utils import ObservationMetaData
from lsst.sims.catalogs.generation.db import fileDBObject, CatalogDBObject
from lsst.sims.catalogs.measures.instance import InstanceCatalog, \
                                                 CompoundInstanceCatalog

class table1DB1(CatalogDBObject):
    tableid = 'table1'
    objid = 'table1DB1'
    idColKey = 'id'

    columns = [('raJ2000','ra'),
               ('decJ2000','dec')]


class table1DB2(CatalogDBObject):
    tableid = 'table1'
    objid = 'table1DB2'
    idColKey = 'id'

    columns = [('raJ2000', '2.0*ra'),
               ('decJ2000', '2.0*dec')]


class table2DB(CatalogDBObject):
    tableid = 'table2'
    objid = 'table2DB'
    idColKey = 'id'

    columns = [('raJ2000', 'ra'),
               ('decJ2000', 'dec')]


class Cat1(InstanceCatalog):
    column_outputs = ['raObs', 'decObs', 'final_mag']

    def get_raObs(self):
        return self.column_by_name('raJ2000')

    def get_decObs(self):
        return self.column_by_name('decJ2000')

    def get_final_mag(self):
        return self.column_by_name('mag') + self.column_by_name('dmag')


class Cat2(Cat1):

    def get_raObs(self):
        return self.column_by_name('raJ2000') + self.column_by_name('dra')

    def get_decObs(self):
        return self.column_by_name('decJ2000') + self.column_by_name('ddec')


class Cat3(Cat1):

    def get_final_mag(self):
        return self.column_by_name('mag')


class CompoundCatalogTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.baseDir = os.path.join(getPackageDir('sims_catalogs_measures'),
                               'tests', 'scratchSpace')

        cls.table1FileName = os.path.join(cls.baseDir, 'compound_table1.txt')
        cls.table2FileName = os.path.join(cls.baseDir, 'compound_table2.txt')

        if os.path.exists(cls.table1FileName):
            os.unlink(cls.table1FileName)
        if os.path.exists(cls.table2FileName):
            os.unlink(cls.table2FileName)

        dtype1 = numpy.dtype([
                           ('ra', numpy.float),
                           ('dec', numpy.float),
                           ('mag', numpy.float),
                           ('dmag', numpy.float),
                           ('dra', numpy.float),
                           ('ddec', numpy.float)
                           ])

        dbDtype1 = numpy.dtype([
                           ('id', numpy.int),
                           ('ra', numpy.float),
                           ('dec', numpy.float),
                           ('mag', numpy.float),
                           ('dmag', numpy.float),
                           ('dra', numpy.float),
                           ('ddec', numpy.float)
                           ])

        nPts = 100
        numpy.random.seed(42)
        raList = numpy.random.random_sample(nPts)*360.0
        decList = numpy.random.random_sample(nPts)*180.0-90.0
        magList = numpy.random.random_sample(nPts)*10.0+15.0
        dmagList = numpy.random.random_sample(nPts)*10.0 - 5.0
        draList = numpy.random.random_sample(nPts)*5.0 - 2.5
        ddecList = numpy.random.random_sample(nPts)*(-2.0) - 4.0

        cls.table1Control = numpy.rec.fromrecords([
                                                  (r, d, mm, dm, dr, dd) \
                                                  for r, d, mm, dm, dr, dd \
                                                  in zip(raList, decList,
                                                         magList, dmagList,
                                                         draList, ddecList)],
                                                  dtype=dtype1
                                                  )

        with open(cls.table1FileName, 'w') as output:
            output.write("# id ra dec mag dmag dra ddec\n")
            for ix, (r, d, mm, dm, dr, dd) in \
            enumerate(zip(raList, decList, magList, dmagList, draList, ddecList)):

                output.write('%d %e %e %e %e %e %e\n' \
                             % (ix, r, d, mm, dm, dr, dd))


        dtype2 = numpy.dtype([
                            ('ra', numpy.float),
                            ('dec', numpy.float),
                            ('mag', numpy.float)
                            ])

        dbDtype2 = numpy.dtype([
                            ('id', numpy.int),
                            ('ra', numpy.float),
                            ('dec', numpy.float),
                            ('mag', numpy.float)
                            ])

        ra2List = numpy.random.random_sample(nPts)*360.0+360.0
        dec2List = numpy.random.random_sample(nPts)*180.0+180.0
        mag2List = numpy.random.random_sample(nPts)*3.0+7.0

        cls.table2Control = numpy.rec.fromrecords([
                                                  (r, d, m) \
                                                  for r, d, m in \
                                                  zip(ra2List, dec2List, mag2List)
                                                  ], dtype=dtype2)

        with open(cls.table2FileName, 'w') as output:
            output.write('# id ra dec mag\n')
            for ix, (r, d, m) in enumerate(zip(ra2List, dec2List, mag2List)):
                output.write('%d %e %e %e\n' % (ix, r, d, m))

        cls.dbName = os.path.join(cls.baseDir, 'compound_db.db')
        if os.path.exists(cls.dbName):
            os.unlink(cls.dbName)

        fdbo = fileDBObject(cls.table1FileName, runtable='table1',
                            database=cls.dbName, dtype=dbDtype1,
                            idColKey='id')

        fdbo = fileDBObject(cls.table2FileName, runtable='table2',
                            database=cls.dbName, dtype=dbDtype2,
                            idColKey='id')


    def testCompoundCatalog(self):
        fileName = os.path.join(self.baseDir, 'simplest_compound_catalog.txt')
        db1 = table1DB1(database=self.dbName, driver='sqlite')
        db2 = table1DB2(database=self.dbName, driver='sqlite')
        db3 = table2DB(database=self.dbName, driver='sqlite')

        cat1 = Cat1(db1)
        cat2 = Cat2(db2)
        cat3 = Cat3(db3)

        compoundCat = CompoundInstanceCatalog([cat1, cat2, cat3])

        compoundCat.write_catalog(fileName)



def suite():
    """Returns a suite containing all the test cases in this module."""
    utilsTests.init()
    suites = []
    suites += unittest.makeSuite(CompoundCatalogTest)

    return unittest.TestSuite(suites)

def run(shouldExit=False):
    """Run the tests"""
    utilsTests.run(suite(), shouldExit)

if __name__ == "__main__":
    run(True)
