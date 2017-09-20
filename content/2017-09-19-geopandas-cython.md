Title: GeoPandas developments: improved performance
Date: 2017-09-19 20:00
Tags: python, geospatial, geopandas, shapely
Slug: geopandas-cython
Summary: Short version for index and feeds

*This work is a collaboration with [Matthew Rocklin](http://matthewrocklin.com/). This blogpost shows our recent work on the GeoPandas library and is partly based on the [EuroSciPy talk](https://www.youtube.com/watch?v=bWsA2R707BM) ([slides](https://jorisvandenbossche.github.io/talks/2017_EuroScipy_geopandas/#1)) I recently gave on the same topic.*


Background
----------

[intro]

Geospatial data analysis. Vector data. Open source libraries (GDAL/OGR, GEOS). Python stack.

The goal of GeoPandas is to make working with geospatial data in python easier. GeoPandas extends the pandas data analysis library to work with geographic objects and spatial operations.

<!-- PELICAN_END_SUMMARY -->

It combines the capabilities of pandas and shapely, providing geospatial operations in pandas and a high-level interface to multiple geometries to shapely. It further builds upon the capabilities of many other libraries including fiona (reading/writing data), pyproj (projections), rtree (spatial index), ... GeoPandas enables you to easily do operations in python that would otherwise require a spatial database such as PostGIS.

In this post we focus on GeoPandas, a geospatial extension of Pandas which
helps to manages tabular data that is annotated with geometry information like
points, paths, and polygons.

### Small GeoPandas demo

For example GeoPandas makes it easy to load and plot the [Police Districts of
Chicago](https://data.cityofchicago.org/Public-Safety/Boundaries-Police-Districts/4dt9-88ua).

```python
import geopandas as gpd
df = gpd.read_file("quartier_paris.geojson")
df.head()
```

<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>objectid</th>
      <th>c_qu</th>
      <th>l_qu</th>
      <th>c_ar</th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>29</td>
      <td>47</td>
      <td>Bercy</td>
      <td>12</td>
      <td>POLYGON ((2.391141037839471 48.82611264577471,...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>41</td>
      <td>1</td>
      <td>St-Germain-l'Auxerrois</td>
      <td>1</td>
      <td>POLYGON ((2.344593389828428 48.85404991486192,...</td>
    </tr>
    <tr>
      <th>2</th>
      <td>79</td>
      <td>76</td>
      <td>Combat</td>
      <td>19</td>
      <td>POLYGON ((2.388343313526396 48.88056667377272,...</td>
    </tr>
    <tr>
      <th>3</th>
      <td>68</td>
      <td>65</td>
      <td>Ternes</td>
      <td>17</td>
      <td>POLYGON ((2.295039618663717 48.87377869547587,...</td>
    </tr>
    <tr>
      <th>4</th>
      <td>50</td>
      <td>10</td>
      <td>Enfants-Rouges</td>
      <td>3</td>
      <td>POLYGON ((2.367101341254551 48.86162755885409,...</td>
    </tr>
  </tbody>
</table>
</div>

```python
# determine in which district each stations is located
stations = gpd.sjoin(stations, quartiers[['l_qu', 'geometry']], op='within')
# count the number of stations per district, and add this information to the
# districts dataframe
counts = stations.groupby('l_qu').size()
quartiers = quartiers.merge(counts.reset_index(name='n_stations'))
# calculate the relative number of bike stations divided by the area
quartiers['n_stations_relative'] = quartiers['n_stations'] / quartiers.geometry.area
#
ax = df.plot(column='n_stations_relative', figsize=(15, 6))
ax.set_axis_off()
```

<img src="{filename}figures/quartiers-paris-bike-stations.png">

Full demo notebook see ... from EuroScipy presentation.


Performance bottlenecks
-----------------------

Unfortunately GeoPandas can be slow, which limits interactive exploration on
larger datasets.  The first dataset mentioned above, crimes in Chicago, has
roughly seven million entries and is several gigabytes in memory.  Analyzing
this sort of dataset interactively with GeoPandas today is not feasible.

This slow performance is because of the current design of GeoPandas. Today
a GeoDataFrame basically is a pandas dataframe with a special `object`-dtype column that
stores Shapely geometries (the 'geometry' column). Shapely geometries are Python objects that provide
a Python interface and reference to GEOS Geometry objects in C:

<img src="{filename}images/geopandas-shapely-1.svg"
     width="50%">

The easy-to-use vectorized operations that GeoPandas provides, such as calculating the distance from every geometry in my dataframe to a certain point:

```python
df.geometry.distance(some_point)
```

is actually simply a small wrapper around Python for loops over shapely calls. So the above method call is roughly equivalent to the following:

```python
[geom.distance(some_point) for geom in df.geometry]
```

Where each `geom` object in this iteration is an individual Shapely object.
This simple design has made GeoPandas a very lightweight and easy-to-develop library, and is possible because GeoPandas can build upon the existing geospatial libraries. But, this simple design has also become a performance bottleneck.

The iteration over the individual Shapely geometries is inefficient for two reasons:

1. Iterating in Python can be quite slow relative to iterating through those same objects in C.
2. Calling the geospatial operation on the Shapely Python object gives some overhead compared to calling the underlying GEOS C operation directly (additionally, the Shapely python objects can take up a significant amount of RAM relative to the GEOS Geometry objects that they wrap).

#### Some timings

```python
import geopandas as gpd
from shapely.geometry import Point, Polygon
import random

s = gpd.GeoSeries([Point(random.random(), random.random()) for _ in range(100000)])
polygon = Polygon([(random.random(), random.random()) for _ in range(3)])
```

```python
s.distance(polygon)
s.within(polygon)
```

Both take roughly 1 second to compute.
This may not seem that much, but you have to be aware that geospatial datasets quickly become larger than 100,000 points, and that in more complex analyses those basic operations as distances and set operations often are done many times.

Below, I also compare the performance of GeoPandas to [PostGIS](http://postgis.net/), the standard
geospatial plugin for the popular PostgreSQL database ([original notebook](https://github.com/jorisvandenbossche/talks/blob/master/2017_EuroScipy_geopandas/geopandas_postgis_comparison.ipynb) with the comparison). While GeoPandas can often be as expressive as PostGIS, we can see that the current version is also much slower.

Cythonizing GeoPandas
---------------------

Currently the slowdown in GeoPandas is because we iterate over every Shapely
object in Python, rather than calling the underlying C library GEOS directly.

Fortunately, we can improve upon this both by accelerating GeoPandas with
Cython, and then by parallelizing it with Dask.

So instead of using a Pandas `object`-dtype column that *holds shapely objects*
like the following image:

<img src="{filename}images/geopandas-shapely-1.svg"
     width="49%">

We instead store a NumPy array of *direct pointers to the GEOS objects*.

<img src="{filename}images/geopandas-shapely-2.svg"
     width="49%">

This allows us to store data more efficiently, and also requires us to now
write our loops over these geometries in C or Cython.  When we perform bulk
vectorized operations on many GEOS pointers at once like in the
`df.geometry.distance(some_point)` example above we can now drop down to Cython
or C to write these loops directly, which provides a significant speedup.

As an example, we include Cython code to compute distance between a GeoSeries
and an individual shapely object below:

```python
cdef GEOSGeometry *left_geom
cdef GEOSGeometry *right_geom = some_point.__geom__  # a geometry pointer

with nogil:
    for idx in xrange(n):
        left_geom = <GEOSGeometry *> arr[idx]
        if left_geom != NULL:
            distance = GEOSDistance_r(handle, left_geom, some_point.__geom)
        else:
            distance = NaN
```

For a more complete example how to use Cython to interface directly with GEOS to speed-up shapely operations, see my [previous blogpost]({filename}/2017-03-18-vectorized-shapely-cython.md).


Some benchmarks
---------------

results simple timings above

![Alt Text]({filename}/figures/timings_distance_all.png)
![Alt Text]({filename}/figures/timings_within_all.png)

big improvement. Depending on the exact operation.

#### Comparison to PostGIS

**PostGIS Query**

```sql
-- What is the population and racial make-up of the neighborhoods of Manhattan?
SELECT
  neighborhoods.name AS neighborhood_name, Sum(census.popn_total) AS population,
  100.0 * Sum(census.popn_white) / NULLIF(Sum(census.popn_total),0) AS white_pct,
  100.0 * Sum(census.popn_black) / NULLIF(Sum(census.popn_total),0) AS black_pct
FROM nyc_neighborhoods AS neighborhoods
JOIN nyc_census_blocks AS census
ON ST_Intersects(neighborhoods.geom, census.geom)
GROUP BY neighborhoods.name
ORDER BY white_pct DESC;
```

**GeoPandas Code**

```python
res = geopandas.sjoin(nyc_neighborhoods, nyc_census_blocks, op='intersects')
res = res.groupby('NAME')[['POPN_TOTAL', 'POPN_WHITE', 'POPN_BLACK']].sum()
res['POPN_BLACK'] = res['POPN_BLACK'] / res['POPN_TOTAL'] * 100
res['POPN_WHITE'] = res['POPN_WHITE'] / res['POPN_TOTAL'] * 100
res.sort_values('POPN_WHITE', ascending=False)
```

Example from [Boundless tutorial](http://workshops.boundlessgeo.com/postgis-intro/) (CC BY SA)

These operations now run at full C speed, and so we get back to exactly the
performance of PostGIS.

<img src="{filename}/figures/timings_sjoin_all.png">

This is not surprising because PostGIS is using the same GEOS library
internally.  In fact, nearly *all* open source GIS libraries all depend on
GEOS.  These algorithms are not particularly complex, so it is not surprising
that everyone has implemented them more or less exactly the same.

This is great.  The Python GIS stack now has a full-speed library that operates
as fast as any other open GIS system is likely to manage.


Outlook
-------

Some promising results, but this is still a work in progress, and there is still plenty of work
to do.

Challenges / problems to tackle:

* Robust integration with pandas
* Slow data ingestion (currently based on Fiona, wrapper around GDAL/OGR)
* Re-implementing algorithms such as spatial overlays (spatial joins already done in C, directly interfacing GEOS and wrapped in cython to use in GeoPandas)
* Battle testing!

To elaborate on the first item:

First, we need for Pandas to track our arrays of GEOS pointers differently from
how it tracks a normal integer array.  This is both for usability reasons, like
we want to render them differently and don't want users to be able to perform
numeric operations like sum and mean on these arrays, and also for stability
reasons, because we need to track these pointers and release their allocated
GEOSGeometry objects from memory at the appropriate times. Currently, this
goal is pursued by creating a new block type, the GeometryBlock ('blocks' are
the internal building blocks of pandas that hold the data of the different columns).
This will require some changes to Pandas itself to enable custom block types
(see [this issue](https://github.com/pandas-dev/pandas/issues/17144) on the pandas
issue tracker).

But also promises: apart from improved speed-up, also memory improvement + opens up the ability to parallellize and distributed e.g. using dask (reference to Matthew's blogpost -> exploration of this)

`GeometryArray` concept might be more broadly useful that just for pandas. If you have such use cases, we would love to hear about that!

### Trying this out

You can track future progress on this effort at
[geopandas/geopandas #473](https://github.com/geopandas/geopandas/issues/473)
which includes installation instructions.

Feedback -> github

Conclusion
----------

With established technologies in the PyData space like Cython and Dask we've
been able to accelerate and scale GeoPandas operations above and beyond
industry standards.  However this work is still experimental and not ready for
production use.  This work is a bit of a side project for both Joris and
Matthew and they would welcome effort from other experienced open source
developers.  We believe that this project can have a large social impact and
are enthusiastic about pursuing it in the future.  We hope that you share our
enthusiasm.
