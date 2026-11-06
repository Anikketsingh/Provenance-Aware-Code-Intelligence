# Annotation Packet

Follow `RULES.md`, and record answers in `annotations.csv`.

## L001  django  `django/contrib/gis/gdal/prototypes/raster.py:134`

```
     130         c_int,
     131         POINTER(c_double),
     132         POINTER(c_double),
     133         POINTER(c_double),
>>   134         POINTER(c_double),
     135         c_void_p,
     136         c_void_p,
     137     ],
     138 )
```

**Candidate commits, oldest first:**

- `8f5904560a`  2015-11-25  Fixed #25734 -- Made GDALBand min and max properties use GDALComputeRasterStatistics.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/contrib/gis/gdal/prototypes/raster.py b/django/contrib/gis/gdal/prototypes/raster.py
--- a/django/contrib/gis/gdal/prototypes/raster.py
+++ b/django/contrib/gis/gdal/prototypes/raster.py
@@ -83,2 +142,1 @@
-    std_call('GDALComputeRasterStatistics'),
-    [c_void_p, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), c_void_p, c_void_p],
+        POINTER(c_double),
### df8d8d4292  2016-03-28  Fixed E128 flake8 warnings in django/.

diff --git a/django/contrib/gis/gdal/prototypes/raster.py b/django/contrib/gis/gdal/prototypes/raster.py
--- a/django/contrib/gis/gdal/prototypes/raster.py
+++ b/django/contrib/gis/gdal/prototypes/raster.py
@@ -77,2 +80,2 @@
-compute_band_statistics = void_output(std_call('GDALComputeRasterStatistics'),
+    std_call('GDALComputeRasterStatistics'),
     [c_void_p, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), c_void_p, c_void_p],
### 8f5904560a  2015-11-24  Fixed #25734 -- Made GDALBand min and max properties use GDALComputeRasterStatistics.

diff --git a/django/contrib/gis/gdal/prototypes/raster.py b/django/contrib/gis/gdal/prototypes/raster.py
--- a/django/contrib/gis/gdal/prototypes/raster.py
+++ b/django/contrib/gis/gdal/prototypes/raster.py
@@ -65,2 +72,2 @@
-get_band_minimum = double_output(std_call('GDALGetRasterMinimum'), [c_void_p, POINTER(c_int)])
-get_band_maximum = double_output(std_call('GDALGetRasterMaximum'), [c_void_p, POINTER(c_int)])
+compute_band_statistics = void_output(std_call('GDALComputeRasterStatistics'),
+    [c_void_p, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), c_void_p, c_void_p],
### 3c4fca271b  2015-04-29  Fixed #24724 -- Fixed GIS initialization crash on Windows.

diff --git a/django/contrib/gis/gdal/prototypes/raster.py b/django/contrib/gis/gdal/prototypes/raster.py
--- a/django/contrib/gis/gdal/prototypes/raster.py
+++ b/django/contrib/gis/gdal/prototypes/raster.py
@@ -50,12 +62,2 @@
-band_io = void_output(lgdal.GDALRasterIO, [c_void_p, c_int, c_int, c_int, c_int, c_int,
-                                           c_void_p, c_int, c_int, c_int, c_int, c_int])
-get_band_xsize = int_output(lgdal.GDALGetRasterBandXSize, [c_void_p])
-get_band_ysize = int_output(lgdal.GDALGetRasterBandYSize, [c_void_p])
-get_band_index = int_output(lgdal.GDALGetBandNumber, [c_void_p])
-get_band_description = const_string_output(lgdal.GDALGetDescription, [c_void_p])
-get_band_ds = voidptr_output(lgdal.GDALGetBandDataset, [c_void_p])
-get_band_datatype = int_output(lgdal.GDALGetRasterDataType, [c_void_p])
-get_band_nodata_value = double_output(lgdal.GDALGetRasterNoDataValue, [c_void_p, POINTER(c_int)])
-set_band_nodata_value = void_output(lgdal.GDALSetRasterNoDataValue, [c_void_p, c_double])
-get_band_minimum = double_output(lgdal.GDALGetRasterMinimum, [c_void_p, POINTER(c_int)])
-get_band_maximum = double_output(lgdal.GDALGetRasterMaximum, [c_void_p, POINTER(c_int)])
+get_band_minimum = double_output(std_call('GDALGetRasterMinimum'), [c_void_p, POINTER(c_int)])
+get_band_maximum = double_output(std_call('GDALGetRasterMaximum'), [c_void_p, POINTER(c_int)])
### 6e08bde8c4  2014-12-02  Added RasterSource/GDALBand GDAL objects

diff --git a/django/contrib/gis/gdal/prototypes/raster.py b/django/contrib/gis/gdal/prototypes/raster.py
--- a/django/contrib/gis/gdal/prototypes/raster.py
+++ b/django/contrib/gis
... (cut, so use `git log -L` for the rest)
````

</details>

## L002  redis  `src/cluster_legacy.h:329`

```
     325     sds hostname;               /* The known hostname for this node */
     326     sds human_nodename;         /* The known human readable nodename for this node */
     327     int tcp_port;               /* Latest known clients TCP port. */
     328     int tls_port;               /* Latest known clients TLS port */
>>   329     int cport;                  /* Latest known cluster port of this node. */
     330     clusterLink *link;          /* TCP/IP link established toward this node */
     331     clusterLink *inbound_link;  /* TCP/IP link accepted from this node */
     332     list *fail_reports;         /* List of nodes signaling this as failing */
     333 };
```

**Candidate commits, oldest first:**

- `ecc9109434`  2011-03-29  Cluster branch merged to unstable.
- `11436b1449`  2016-01-29  Cluster announce ip / port initial implementation.
- `d9a0478599`  2023-11-22  Cluster refactor: Make clusterNode private

<details><summary>Line history</summary>

````diff
### d9a047859  2023-10-30  Cluster refactor: Make clusterNode private

diff --git a/src/cluster_legacy.h b/src/cluster_legacy.h
--- a/src/cluster_legacy.h
+++ b/src/cluster_legacy.h
@@ -214,0 +244,1 @@
+    int cport;                  /* Latest known cluster port of this node. */

````

</details>

## L003  redis  `src/db.c:3381`

```
    3377 
    3378         first = 0;
    3379         if (spec->begin_search_type == KSPEC_BS_INDEX) {
    3380             first = spec->bs.index.pos;
>>  3381         } else if (spec->begin_search_type == KSPEC_BS_KEYWORD) {
    3382             int start_index = spec->bs.keyword.startfrom > 0 ? spec->bs.keyword.startfrom : argc+spec->bs.keyword.startfrom;
    3383             int end_index = spec->bs.keyword.startfrom > 0 ? argc-1: 1;
    3384             for (i = start_index; i != end_index; i = start_index <= end_index ? i + 1 : i - 1) {
    3385                 if (i >= argc || i < 1)
```

**Candidate commits, oldest first:**

- `55c81f2cd3`  2022-01-20  ACL V2 - Selectors and key based permissions (#9974)

<details><summary>Line history</summary>

````diff
### 55c81f2cd  2022-01-20  ACL V2 - Selectors and key based permissions (#9974)

diff --git a/src/db.c b/src/db.c
--- a/src/db.c
+++ b/src/db.c
@@ -1681,0 +1714,1 @@
+        } else if (spec->begin_search_type == KSPEC_BS_KEYWORD) {

````

</details>

## L004  redis  `src/object.c:612`

```
     608 void freeHashObject(robj *o) {
     609     hashTypeFree(o);
     610 }
     611 
>>   612 void freeModuleObject(robj *o) {
     613     moduleValue *mv = o->ptr;
     614     mv->type->free(mv->value);
     615     zfree(mv);
     616 }
```

**Candidate commits, oldest first:**

- `8ec28002be`  2016-06-03  Modules: support for modules native data types.

<details><summary>Line history</summary>

````diff
### 8ec28002b  2016-05-18  Modules: support for modules native data types.

diff --git a/src/object.c b/src/object.c
--- a/src/object.c
+++ b/src/object.c
@@ -284,0 +291,1 @@
+void freeModuleObject(robj *o) {

````

</details>

## L005  django  `django/db/models/lookups.py:536`

```
     532             try:
     533                 rhs = OrderedSet(self.rhs)
     534                 rhs.discard(None)
     535             except TypeError:  # Unhashable items in self.rhs
>>   536                 rhs = [r for r in self.rhs if r is not None]
     537 
     538             if not rhs:
     539                 raise EmptyResultSet
     540 
```

**Candidate commits, oldest first:**

- `5776a1660e`  2020-06-11  Fixed #31667 -- Made __in lookup ignore None values.

<details><summary>Line history</summary>

````diff
### 5776a1660e  2020-06-05  Fixed #31667 -- Made __in lookup ignore None values.

diff --git a/django/db/models/lookups.py b/django/db/models/lookups.py
--- a/django/db/models/lookups.py
+++ b/django/db/models/lookups.py
@@ -372,1 +374,1 @@
-                rhs = self.rhs
+                rhs = [r for r in self.rhs if r is not None]
### 86eccdc8b6  2015-11-07  Fixed #25544 -- Removed duplicate ids in prefetch_related() queries.

diff --git a/django/db/models/lookups.py b/django/db/models/lookups.py
--- a/django/db/models/lookups.py
+++ b/django/db/models/lookups.py
@@ -207,3 +210,1 @@
-            # rhs should be an iterable, we use batch_process_rhs
-            # to prepare/transform those values
-            rhs = list(self.rhs)
+                rhs = self.rhs
### 00aa562884  2014-09-14  Fixed #23493 -- Added bilateral attribute to Transform

diff --git a/django/db/models/lookups.py b/django/db/models/lookups.py
--- a/django/db/models/lookups.py
+++ b/django/db/models/lookups.py
@@ -206,9 +252,3 @@
-    def get_db_prep_lookup(self, value, connection):
-        params = self.lhs.output_field.get_db_prep_lookup(
-            self.lookup_name, value, connection, prepared=True)
-        if not params:
-            # TODO: check why this leads to circular import
-            from django.db.models.sql.datastructures import EmptyResultSet
-            raise EmptyResultSet
-        placeholder = '(' + ', '.join('%s' for p in params) + ')'
-        return (placeholder, params)
+            # rhs should be an iterable, we use batch_process_rhs
+            # to prepare/transform those values
+            rhs = list(self.rhs)
### 95cc0e15b4  2014-06-17  Fixed #22819 -- Renamed output_type -> output_field in query expression API.

diff --git a/django/db/models/lookups.py b/django/db/models/lookups.py
--- a/django/db/models/lookups.py
+++ b/django/db/models/lookups.py
@@ -205,9 +205,9 @@
     def get_db_prep_lookup(self, value, connection):
-        params = self.lhs.output_type.get_db_prep_lookup(
+        params = self.lhs.output_field.get_db_prep_lookup(
             self.lookup_name, value, connection, prepared=True)
         if not params:
             # TODO: check why this leads to circular import
             from django.db.models.sql.datastructures import EmptyResultSet
             raise EmptyResultSet
         placeholder = '(' + ', '.join('%s' for p in params) + ')'
         return (placeholder, params)
### 20bab2cf9d  2014-01-18  Fixed #16187 -- refactored ORM lookup system

diff --git a/django/db/models/lookups.py b/django/db/models/lookups.py
--- /dev/null
+++ b/django/db/models/lookups.py
@@ -0,0 +177,9 @@
+    def get_db_prep_lookup(self, value, connection):
+        params = self.lhs.output_type.get_db_prep_lookup(
+            self.lookup_name, value, connection, prepared=True)
+        if not params:
+            # TODO: check why this leads to circular import
+            from django.db.models.sql.datastructures import EmptyResultSet
+            raise EmptyResultSet
+        placeholder = '(' + ', '.join('%s' for p in params) + ')'
+        return (placeholder, params)

````

</details>

## L006  redis  `src/cluster_asm.c:1924`

```
    1920     {
    1921         const char *reason = disabled_by_module ? "trim is disabled by module" :
    1922                              impl_ret != C_OK ? "cluster is not ready" :
    1923                              trim_in_progress ? "trim in progress for some of the slots" :
>>  1924                                                 "server paused";
    1925         if (start_blocked_logged == 0) {
    1926             serverLog(LL_WARNING, "Can not start import task %s for slots: %s due to %s",
    1927                                   task->id, slots_str, reason);
    1928             start_blocked_logged = 1;
```

**Candidate commits, oldest first:**

- `2bc4e0299d`  2025-10-22  Add Atomic Slot Migration (ASM) support (#14414)

<details><summary>Line history</summary>

````diff
### 2bc4e0299  2025-10-22  Add Atomic Slot Migration (ASM) support (#14414)

diff --git a/src/cluster_asm.c b/src/cluster_asm.c
--- /dev/null
+++ b/src/cluster_asm.c
@@ -0,0 +1707,1 @@
+                                                "server paused";

````

</details>

## L007  django  `django/db/models/query.py:835`

```
     831             if unique_fields and not db_features.supports_update_conflicts_with_target:
     832                 raise NotSupportedError(
     833                     "This database backend does not support updating "
     834                     "conflicts with specifying unique fields that can trigger "
>>   835                     "the upsert."
     836                 )
     837             if not unique_fields and db_features.supports_update_conflicts_with_target:
     838                 raise ValueError(
     839                     "Unique fields that can trigger the upsert must be provided."
```

**Candidate commits, oldest first:**

- `0f6946495a`  2022-01-19  Fixed #31685 -- Added support for updating conflicts to QuerySet.bulk_create().
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/db/models/query.py b/django/db/models/query.py
--- a/django/db/models/query.py
+++ b/django/db/models/query.py
@@ -520,3 +579,1 @@
-                    'This database backend does not support updating '
-                    'conflicts with specifying unique fields that can trigger '
-                    'the upsert.'
+                    "the upsert."
### 0f6946495a  2020-06-15  Fixed #31685 -- Added support for updating conflicts to QuerySet.bulk_create().

diff --git a/django/db/models/query.py b/django/db/models/query.py
--- a/django/db/models/query.py
+++ b/django/db/models/query.py
@@ -469,1 +493,3 @@
-    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
+                    'This database backend does not support updating '
+                    'conflicts with specifying unique fields that can trigger '
+                    'the upsert.'
### f1fbef6cd1  2017-10-03  Fixed #28668 -- Allowed QuerySet.bulk_create() to ignore insert conflicts.

diff --git a/django/db/models/query.py b/django/db/models/query.py
--- a/django/db/models/query.py
+++ b/django/db/models/query.py
@@ -421,1 +422,1 @@
-    def bulk_create(self, objs, batch_size=None):
+    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
### 29132ebdef  2012-04-29  Fixed #17788 -- Added batch_size argument to qs.bulk_create()

diff --git a/django/db/models/query.py b/django/db/models/query.py
--- a/django/db/models/query.py
+++ b/django/db/models/query.py
@@ -391,1 +391,1 @@
-    def bulk_create(self, objs):
+    def bulk_create(self, objs, batch_size=None):
### 7deb25b8dd  2011-09-09  Fixed #7596.  Added Model.objects.bulk_create, and make use of it in several places.  This provides a performance benefit when inserting multiple objects.  THanks to Russ for the review, and Simon Meers for the MySQl implementation.

diff --git a/django/db/models/query.py b/django/db/models/query.py
--- a/django/db/models/query.py
+++ b/django/db/models/query.py
@@ -355,0 +357,1 @@
+    def bulk_create(self, objs):

````

</details>

## L008  django  `django/db/models/fields/related.py:1180`

```
    1176                         "ForeignKey(unique=True) is usually better served by a "
    1177                         "OneToOneField."
    1178                     ),
    1179                     obj=self,
>>  1180                     id="fields.W342",
    1181                 )
    1182             ]
    1183             if self.unique
    1184             else []
```

**Candidate commits, oldest first:**

- `f39b0421b4`  2014-11-28  Fixed #23338 -- Added warning when unique=True on ForeigKey
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -905,8 +1014,1 @@
-        return [
-            checks.Warning(
-                'Setting unique=True on a ForeignKey has the same effect as using a OneToOneField.',
-                hint='ForeignKey(unique=True) is usually better served by a OneToOneField.',
-                obj=self,
-                id='fields.W342',
-            )
-        ] if self.unique else []
+                    id="fields.W342",
### f39b0421b4  2014-09-08  Fixed #23338 -- Added warning when unique=True on ForeigKey

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -1738,0 +1740,8 @@
+        return [
+            checks.Warning(
+                'Setting unique=True on a ForeignKey has the same effect as using a OneToOneField.',
+                hint='ForeignKey(unique=True) is usually better served by a OneToOneField.',
+                obj=self,
+                id='fields.W342',
+            )
+        ] if self.unique else []

````

</details>

## L009  django  `django/db/backends/oracle/base.py:41`

```
      37                 "Error loading ctypes: %s; "
      38                 "the Oracle backend requires ctypes to "
      39                 "operate correctly under Cygwin." % e
      40             )
>>    41         kernel32 = ctypes.CDLL("kernel32")
      42         for name, value in environ:
      43             kernel32.SetEnvironmentVariableA(name, value)
      44     else:
      45         os.environ.update(environ)
```

**Candidate commits, oldest first:**

- `cbf9d6e0bb`  2010-12-03  Fixed the Oracle environment variables not getting set correctly under Cygwin.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/db/backends/oracle/base.py b/django/db/backends/oracle/base.py
--- a/django/db/backends/oracle/base.py
+++ b/django/db/backends/oracle/base.py
@@ -28,4 +33,1 @@
-            raise ImproperlyConfigured("Error loading ctypes: %s; "
-                                       "the Oracle backend requires ctypes to "
-                                       "operate correctly under Cygwin." % e)
-        kernel32 = ctypes.CDLL('kernel32')
+        kernel32 = ctypes.CDLL("kernel32")
### b8c368feb2  2010-12-08  Replaced an ImportError with ImproperlyConfigured in the Oracle backend.

diff --git a/django/db/backends/oracle/base.py b/django/db/backends/oracle/base.py
--- a/django/db/backends/oracle/base.py
+++ b/django/db/backends/oracle/base.py
@@ -21,3 +23,4 @@
-        except ImportError:
-            raise ImportError("ctypes not found. The Oracle backend requires ctypes to operate correctly under Cygwin.")
+            raise ImproperlyConfigured("Error loading ctypes: %s; "
+                                       "the Oracle backend requires ctypes to "
+                                       "operate correctly under Cygwin." % e)
         kernel32 = ctypes.CDLL('kernel32')
### cbf9d6e0bb  2010-12-03  Fixed the Oracle environment variables not getting set correctly under Cygwin.

diff --git a/django/db/backends/oracle/base.py b/django/db/backends/oracle/base.py
--- a/django/db/backends/oracle/base.py
+++ b/django/db/backends/oracle/base.py
@@ -14,5 +21,3 @@
-# Oracle takes client-side character set encoding from the environment.
-os.environ['NLS_LANG'] = '.UTF8'
-# This prevents unicode from getting mangled by getting encoded into the
-# potentially non-unicode database character set.
-os.environ['ORA_NCHAR_LITERAL_REPLACE'] = 'TRUE'
+        except ImportError:
+            raise ImportError("ctypes not found. The Oracle backend requires ctypes to operate correctly under Cygwin.")
+        kernel32 = ctypes.CDLL('kernel32')
### faf1609851  2009-03-27  Fixed an issue with unicode being mangled in Oracle when the database character set is non-unicode.

diff --git a/django/db/backends/oracle/base.py b/django/db/backends/oracle/base.py
--- a/django/db/backends/oracle/base.py
+++ b/django/db/backends/oracle/base.py
@@ -15,2 +15,5 @@
 # Oracle takes client-side character set encoding from the environment.
 os.environ['NLS_LANG'] = '.UTF8'
+# This prevents unicode from getting mangled by getting encoded into the
+# potentially non-unicode database character set.
+os.environ['ORA_NCHAR_LITERAL_REPLACE'] = 'TRUE'
### 953badbea5  2007-07-04  Merged Unicode branch into trunk (r4952:5608). This should be fully backwards compatible for all practical purposes.

diff --git a/django/db/backends/oracle/base.py b/django/db/backends/oracle/base.py
--- a/django/db/backends/oracle/base.py
+++ b/django/db/backends/oracle/base.py
@@ -9,0 +14,2 @@
+# Oracle takes client-side character set encoding from the environment.
+os.environ['NLS_LANG'] = '.UTF8'

````

</details>

## L010  django  `django/contrib/gis/gdal/prototypes/raster.py:109`

```
     105 )
     106 set_band_nodata_value = void_output(
     107     std_call("GDALSetRasterNoDataValue"), [c_void_p, c_double]
     108 )
>>   109 delete_band_nodata_value = void_output(
     110     std_call("GDALDeleteRasterNoDataValue"), [c_void_p]
     111 )
     112 get_band_statistics = void_output(
     113     std_call("GDALGetRasterStatistics"),
```

**Candidate commits, oldest first:**

- `f1db8c36e9`  2016-03-29  Fixed #26415 -- Allowed deleting nodata value on GDALBands.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/contrib/gis/gdal/prototypes/raster.py b/django/contrib/gis/gdal/prototypes/raster.py
--- a/django/contrib/gis/gdal/prototypes/raster.py
+++ b/django/contrib/gis/gdal/prototypes/raster.py
@@ -62,13 +117,1 @@
-    std_call('GDALRasterIO'),
-    [c_void_p, c_int, c_int, c_int, c_int, c_int, c_void_p, c_int, c_int, c_int, c_int, c_int]
-)
-get_band_xsize = int_output(std_call('GDALGetRasterBandXSize'), [c_void_p])
-get_band_ysize = int_output(std_call('GDALGetRasterBandYSize'), [c_void_p])
-get_band_index = int_output(std_call('GDALGetBandNumber'), [c_void_p])
-get_band_description = const_string_output(std_call('GDALGetDescription'), [c_void_p])
-get_band_ds = voidptr_output(std_call('GDALGetBandDataset'), [c_void_p])
-get_band_datatype = int_output(std_call('GDALGetRasterDataType'), [c_void_p])
-get_band_color_interp = int_output(std_call('GDALGetRasterColorInterpretation'), [c_void_p])
-get_band_nodata_value = double_output(std_call('GDALGetRasterNoDataValue'), [c_void_p, POINTER(c_int)])
-set_band_nodata_value = void_output(std_call('GDALSetRasterNoDataValue'), [c_void_p, c_double])
-delete_band_nodata_value = void_output(std_call('GDALDeleteRasterNoDataValue'), [c_void_p])
+delete_band_nodata_value = void_output(
### 3ae4344bbd  2021-04-07  Dropped support for GEOS 3.5 and GDAL 2.0.

diff --git a/django/contrib/gis/gdal/prototypes/raster.py b/django/contrib/gis/gdal/prototypes/raster.py
--- a/django/contrib/gis/gdal/prototypes/raster.py
+++ b/django/contrib/gis/gdal/prototypes/raster.py
@@ -66,16 +62,13 @@
     std_call('GDALRasterIO'),
     [c_void_p, c_int, c_int, c_int, c_int, c_int, c_void_p, c_int, c_int, c_int, c_int, c_int]
 )
 get_band_xsize = int_output(std_call('GDALGetRasterBandXSize'), [c_void_p])
 get_band_ysize = int_output(std_call('GDALGetRasterBandYSize'), [c_void_p])
 get_band_index = int_output(std_call('GDALGetBandNumber'), [c_void_p])
 get_band_description = const_string_output(std_call('GDALGetDescription'), [c_void_p])
 get_band_ds = voidptr_output(std_call('GDALGetBandDataset'), [c_void_p])
 get_band_datatype = int_output(std_call('GDALGetRasterDataType'), [c_void_p])
 get_band_color_interp = int_output(std_call('GDALGetRasterColorInterpretation'), [c_void_p])
 get_band_nodata_value = double_output(std_call('GDALGetRasterNoDataValue'), [c_void_p, POINTER(c_int)])
 set_band_nodata_value = void_output(std_call('GDALSetRasterNoDataValue'), [c_void_p, c_double])
-if GDAL_VERSION >= (2, 1):
-    delete_band_nodata_value = void_output(std_call('GDALDeleteRasterNoDataValue'), [c_void_p])
-else:
-    delete_band_nodata_value = None
+delete_band_nodata_value = void_output(std_call('GDALDeleteRasterNoDataValue'), [c_void_p])
### 4fe6588da3  2017-09-18  Fixed #28576 -- Added color interpretation method to GDALBand.

diff --git a/django/contrib/gis/gdal/prototypes/raster.py b/django/contrib/gis/gdal/prototypes/raster.py
--- a/django/contrib/gis/gdal/prototypes/raster.py
+++ b/django/contrib/gis/gdal/prototypes/raster.py
@@ -69,15 +69,16 @@
     std_call('GDALRasterIO'),
     [c_void_p, c_int, c_int, c_int, c_int, c_int, c_void_p, c_int, c_int, c_int, c_int, c_int]
 )
 get_band_xsize = int_output(std_call('GDALGetRasterBandXSize'), [c_void_p])
 get_band_ysize = int_output(std_call('GDALGetRasterBandYSize'), [c_void_p])
 get_band_index = int_output(std_call('GDALGetBandNumber'), [c_void_p])
 get_band_description = const_string_output(
... (cut, so use `git log -L` for the rest)
````

</details>

## L011  django  `django/db/backends/postgresql/base.py:335`

```
     331             try:
     332                 self.isolation_level = IsolationLevel(isolation_level_value)
     333                 set_isolation_level = True
     334             except ValueError:
>>   335                 raise ImproperlyConfigured(
     336                     f"Invalid transaction isolation level {isolation_level_value} "
     337                     f"specified. Use one of the psycopg.IsolationLevel values."
     338                 )
     339         if self.pool:
```

**Candidate commits, oldest first:**

- `1e0fb3b7a3`  2005-07-16  Added helpful error message if DATABASE_NAME or DATABASE_USER is blank for postgresql
- `e7982bb5b0`  2005-09-19  Fixed #491 -- Non-user connections are now supported for PostgreSQL. Thanks, jafo@tummy.co
- `b367ec2244`  2007-08-20  Made various negligible formatting cleanups to the database backends
- `ff60c5f9de`  2009-12-22  Fixed #1142 -- Added multiple database support.
- `828f7b62e8`  2012-07-10  Fixed #18602 -- Improved error message when database NAME is missing
- `1d90c9b113`  2022-12-12  Refs #33308 -- Added psycopg_any.IsolationLevel.

<details><summary>Line history</summary>

````diff
### 1d90c9b113  2022-12-12  Refs #33308 -- Added psycopg_any.IsolationLevel.

diff --git a/django/db/backends/postgresql/base.py b/django/db/backends/postgresql/base.py
--- a/django/db/backends/postgresql/base.py
+++ b/django/db/backends/postgresql/base.py
@@ -229,2 +233,1 @@
-            if self.isolation_level != connection.isolation_level:
-                connection.set_session(isolation_level=self.isolation_level)
+                raise ImproperlyConfigured(
### 3adc5f1ee6  2015-02-16  Fixed #24335 -- Bumped required psycopg2 version to 2.4.5 (2.5 for contrib.postgres).

diff --git a/django/db/backends/postgresql_psycopg2/base.py b/django/db/backends/postgresql_psycopg2/base.py
--- a/django/db/backends/postgresql_psycopg2/base.py
+++ b/django/db/backends/postgresql_psycopg2/base.py
@@ -176,6 +186,2 @@
-            # Set the isolation level to the value from OPTIONS. This isn't
-            # needed on psycopg2 < 2.4.2 because it happens as a side-effect
-            # of _set_autocommit(False).
-            if (self.isolation_level != connection.isolation_level and
-                    self.psycopg2_version >= (2, 4, 2)):
+            if self.isolation_level != connection.isolation_level:
                 connection.set_session(isolation_level=self.isolation_level)
### 76356d963c  2015-02-14  Fixed #24318 -- Set the transaction isolation level with psycopg >= 2.4.2.

diff --git a/django/db/backends/postgresql_psycopg2/base.py b/django/db/backends/postgresql_psycopg2/base.py
--- a/django/db/backends/postgresql_psycopg2/base.py
+++ b/django/db/backends/postgresql_psycopg2/base.py
@@ -168,1 +179,6 @@
-        return Database.connect(**conn_params)
+            # Set the isolation level to the value from OPTIONS. This isn't
+            # needed on psycopg2 < 2.4.2 because it happens as a side-effect
+            # of _set_autocommit(False).
+            if (self.isolation_level != connection.isolation_level and
+                    self.psycopg2_version >= (2, 4, 2)):
+                connection.set_session(isolation_level=self.isolation_level)
### 1893467784  2012-11-26  Fixed #19274 -- Made db connection creation overridable in subclasses

diff --git a/django/db/backends/postgresql_psycopg2/base.py b/django/db/backends/postgresql_psycopg2/base.py
--- a/django/db/backends/postgresql_psycopg2/base.py
+++ b/django/db/backends/postgresql_psycopg2/base.py
@@ -159,1 +183,1 @@
-    def _cursor(self):
+        return Database.connect(**conn_params)
### 315145f7ca  2009-03-11  Fixed #10459 -- Refactored the internals of database connection objects so that connections know their own settings and pass around settings as dictionaries instead of passing around the Django settings module itself. This will make it easier for multiple database support. Thanks to Alex Gaynor for the initial patch.

diff --git a/django/db/backends/postgresql_psycopg2/base.py b/django/db/backends/postgresql_psycopg2/base.py
--- a/django/db/backends/postgresql_psycopg2/base.py
+++ b/django/db/backends/postgresql_psycopg2/base.py
@@ -68,1 +68,1 @@
-    def _cursor(self, settings):
+    def _cursor(self):
### 7c41b19c8a  2007-08-19  Refactored all database backends to inherit from a common base class to remove quite a bit of duplicated code. Thanks for the patch, Brian Harring. Refs #5106

diff --git a/django/db/backends/postgresql_psycopg2/base.py b/django/db/backends/postgresql_psycopg2/base.py
--- a/django/db/backends/postgresql_psycopg2/base.py
+++ b/django/db/backen
... (cut, so use `git log -L` for the rest)
````

</details>

## L012  django  `django/contrib/admin/options.py:247`

```
     243             # OneToOneField with parent_link=True or a M2M intermediary.
     244             if formfield and db_field.name not in self.raw_id_fields:
     245                 try:
     246                     related_modeladmin = self.admin_site.get_model_admin(
>>   247                         db_field.remote_field.model
     248                     )
     249                 except NotRegistered:
     250                     wrapper_kwargs = {}
     251                 else:
```

**Candidate commits, oldest first:**

- `30610719d5`  2010-09-10  Adding related objects in the admin (via popup) respects user permissions. Patch from Smil
- `8f30556329`  2015-03-25  Renamed Field.rel attribute to remote_field
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.
- `f64fd47a76`  2023-07-07  Fixed #9602 -- Added AdminSite.get_model_admin().

<details><summary>Line history</summary>

````diff
### f64fd47a76  2023-07-07  Fixed #9602 -- Added AdminSite.get_model_admin().

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -188,8 +192,1 @@
-                related_modeladmin = self.admin_site._registry.get(
-                    db_field.remote_field.model
-                )
-                wrapper_kwargs = {}
-                if related_modeladmin:
-                    wrapper_kwargs.update(
-                        can_add_related=related_modeladmin.has_add_permission(request),
-                        can_change_related=related_modeladmin.has_change_permission(
+                        db_field.remote_field.model
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -163,8 +181,8 @@
-                related_modeladmin = self.admin_site._registry.get(db_field.remote_field.model)
+                related_modeladmin = self.admin_site._registry.get(
+                    db_field.remote_field.model
+                )
                 wrapper_kwargs = {}
                 if related_modeladmin:
                     wrapper_kwargs.update(
                         can_add_related=related_modeladmin.has_add_permission(request),
-                        can_change_related=related_modeladmin.has_change_permission(request),
-                        can_delete_related=related_modeladmin.has_delete_permission(request),
-                        can_view_related=related_modeladmin.has_view_permission(request),
+                        can_change_related=related_modeladmin.has_change_permission(
### 825f0beda8  2018-05-02  Fixed #8936 -- Added a view permission and a read-only admin.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -163,7 +163,8 @@
                 related_modeladmin = self.admin_site._registry.get(db_field.remote_field.model)
                 wrapper_kwargs = {}
                 if related_modeladmin:
                     wrapper_kwargs.update(
                         can_add_related=related_modeladmin.has_add_permission(request),
                         can_change_related=related_modeladmin.has_change_permission(request),
                         can_delete_related=related_modeladmin.has_delete_permission(request),
+                        can_view_related=related_modeladmin.has_view_permission(request),
### 8f30556329  2015-02-26  Renamed Field.rel attribute to remote_field

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -157,7 +155,7 @@
-                related_modeladmin = self.admin_site._registry.get(db_field.rel.to)
+                related_modeladmin = self.admin_site._registry.get(db_field.remote_field.model)
                 wrapper_kwargs = {}
                 if related_modeladmin:
                     wrapper_kwargs.update(
                         can_add_related=related_modeladmin.has_add_permission(request),
                         can_change_related=related_modeladmin.has_change_permission(request),
                         can_delete_related=related_modeladmin.has_delete_permission(request),
### 07988744b3  2
... (cut, so use `git log -L` for the rest)
````

</details>

## L013  django  `django/utils/regex_helper.py:153`

```
     149                             ch, escaped = next(pattern_iter)
     150                         param = "".join(name)
     151                         # Named backreferences have already consumed the
     152                         # parenthesis.
>>   153                         if terminal_char != ")":
     154                             result.append(Group((("%%(%s)s" % param), param)))
     155                             walk_to_end(ch, pattern_iter)
     156                         else:
     157                             result.append(Group((("%%(%s)s" % param), None)))
```

**Candidate commits, oldest first:**

- `e52c52ea13`  2012-01-03  Fixed #17492 -- Allow reversal of named backreferences. Thanks nate_b
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/utils/regex_helper.py b/django/utils/regex_helper.py
--- a/django/utils/regex_helper.py
+++ b/django/utils/regex_helper.py
@@ -150,1 +152,1 @@
-                        if terminal_char != ')':
+                        if terminal_char != ")":
### e52c52ea13  2012-01-03  Fixed #17492 -- Allow reversal of named backreferences. Thanks nate_b

diff --git a/django/utils/regex_helper.py b/django/utils/regex_helper.py
--- a/django/utils/regex_helper.py
+++ b/django/utils/regex_helper.py
@@ -147,2 +154,1 @@
-                        result.append(Group(((u"%%(%s)s" % param), param)))
-                        walk_to_end(ch, pattern_iter)
+                        if terminal_char != ')':
### 7838493b9e  2008-08-31  Fixed #8726 -- When doing reverse URL resolving, make sure we're consistently dealing with unicode strings throughout by promoting up from UTF-8 as necessary.

diff --git a/django/utils/regex_helper.py b/django/utils/regex_helper.py
--- a/django/utils/regex_helper.py
+++ b/django/utils/regex_helper.py
@@ -147,2 +147,2 @@
-                        result.append(Group((("%%(%s)s" % param), param)))
+                        result.append(Group(((u"%%(%s)s" % param), param)))
                         walk_to_end(ch, pattern_iter)
### a63a83e5d8  2008-08-31  A rewrite of the reverse URL parsing: the reverse() call and the "url" template tag.

diff --git a/django/utils/regex_helper.py b/django/utils/regex_helper.py
--- /dev/null
+++ b/django/utils/regex_helper.py
@@ -0,0 +143,2 @@
+                        result.append(Group((("%%(%s)s" % param), param)))
+                        walk_to_end(ch, pattern_iter)

````

</details>

## L014  redis  `src/server.c:4162`

```
    4158  *
    4159  * The function returns true if stats was updated and false if not. */
    4160 int incrCommandStatsOnError(struct redisCommand *cmd, int flags) {
    4161     /* hold the prev error count captured on the last command execution */
>>  4162     static long long prev_err_count = 0;
    4163     int res = 0;
    4164     if (cmd) {
    4165         if ((server.stat_total_error_replies - prev_err_count) > 0) {
    4166             if (flags & ERROR_COMMAND_REJECTED) {
```

**Candidate commits, oldest first:**

- `aa856b39f2`  2022-02-27  Sort out the mess around Lua error messages and error stats (#10329)

<details><summary>Line history</summary>

````diff
### aa856b39f  2022-02-27  Sort out the mess around Lua error messages and error stats (#10329)

diff --git a/src/server.c b/src/server.c
--- a/src/server.c
+++ b/src/server.c
@@ -3138,0 +3149,1 @@
+    static long long prev_err_count = 0;

````

</details>

## L015  django  `django/utils/lorem_ipsum.py:117`

```
     113     "enim",
     114     "totam",
     115     "delectus",
     116     "ducimus",
>>   117     "quis",
     118     "voluptates",
     119     "dolores",
     120     "molestiae",
     121     "harum",
```

**Candidate commits, oldest first:**

- `d22e39c10d`  2007-03-30  Fixed #3799 -- Added django.contrib.webdesign and moved 'lorem' template tag into there
- `953badbea5`  2007-07-04  Merged Unicode branch into trunk (r4952:5608). This should be fully backwards compatible f
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/utils/lorem_ipsum.py b/django/utils/lorem_ipsum.py
--- a/django/utils/lorem_ipsum.py
+++ b/django/utils/lorem_ipsum.py
@@ -18,29 +117,1 @@
-    'exercitationem', 'perferendis', 'perspiciatis', 'laborum', 'eveniet',
-    'sunt', 'iure', 'nam', 'nobis', 'eum', 'cum', 'officiis', 'excepturi',
-    'odio', 'consectetur', 'quasi', 'aut', 'quisquam', 'vel', 'eligendi',
-    'itaque', 'non', 'odit', 'tempore', 'quaerat', 'dignissimos',
-    'facilis', 'neque', 'nihil', 'expedita', 'vitae', 'vero', 'ipsum',
-    'nisi', 'animi', 'cumque', 'pariatur', 'velit', 'modi', 'natus',
-    'iusto', 'eaque', 'sequi', 'illo', 'sed', 'ex', 'et', 'voluptatibus',
-    'tempora', 'veritatis', 'ratione', 'assumenda', 'incidunt', 'nostrum',
-    'placeat', 'aliquid', 'fuga', 'provident', 'praesentium', 'rem',
-    'necessitatibus', 'suscipit', 'adipisci', 'quidem', 'possimus',
-    'voluptas', 'debitis', 'sint', 'accusantium', 'unde', 'sapiente',
-    'voluptate', 'qui', 'aspernatur', 'laudantium', 'soluta', 'amet',
-    'quo', 'aliquam', 'saepe', 'culpa', 'libero', 'ipsa', 'dicta',
-    'reiciendis', 'nesciunt', 'doloribus', 'autem', 'impedit', 'minima',
-    'maiores', 'repudiandae', 'ipsam', 'obcaecati', 'ullam', 'enim',
-    'totam', 'delectus', 'ducimus', 'quis', 'voluptates', 'dolores',
-    'molestiae', 'harum', 'dolorem', 'quia', 'voluptatem', 'molestias',
-    'magni', 'distinctio', 'omnis', 'illum', 'dolorum', 'voluptatum', 'ea',
-    'quas', 'quam', 'corporis', 'quae', 'blanditiis', 'atque', 'deserunt',
-    'laboriosam', 'earum', 'consequuntur', 'hic', 'cupiditate',
-    'quibusdam', 'accusamus', 'ut', 'rerum', 'error', 'minus', 'eius',
-    'ab', 'ad', 'nemo', 'fugit', 'officia', 'at', 'in', 'id', 'quos',
-    'reprehenderit', 'numquam', 'iste', 'fugiat', 'sit', 'inventore',
-    'beatae', 'repellendus', 'magnam', 'recusandae', 'quod', 'explicabo',
-    'doloremque', 'aperiam', 'consequatur', 'asperiores', 'commodi',
-    'optio', 'dolor', 'labore', 'temporibus', 'repellat', 'veniam',
-    'architecto', 'est', 'esse', 'mollitia', 'nulla', 'a', 'similique',
-    'eos', 'alias', 'dolore', 'tenetur', 'deleniti', 'porro', 'facere',
-    'maxime', 'corrupti',
+    "quis",
### df8d8d4292  2016-03-28  Fixed E128 flake8 warnings in django/.

diff --git a/django/utils/lorem_ipsum.py b/django/utils/lorem_ipsum.py
--- a/django/utils/lorem_ipsum.py
+++ b/django/utils/lorem_ipsum.py
@@ -19,29 +20,29 @@
-WORDS = ('exercitationem', 'perferendis', 'perspiciatis', 'laborum', 'eveniet',
-        'sunt', 'iure', 'nam', 'nobis', 'eum', 'cum', 'officiis', 'excepturi',
-        'odio', 'consectetur', 'quasi', 'aut', 'quisquam', 'vel', 'eligendi',
-        'itaque', 'non', 'odit', 'tempore', 'quaerat', 'dignissimos',
-        'facilis', 'neque', 'nihil', 'expedita', 'vitae', 'vero', 'ipsum',
-        'nisi', 'animi', 'cumque', 'pariatur', 'velit', 'modi', 'natus',
-        'iusto', 'eaque', 'sequi', 'illo', 'sed', 'ex', 'et', 'voluptatibus',
-        'tempora', 'veritatis', 'ratione', 'assumenda', 'incidunt', 'nostrum',
-        'placeat', 'aliquid', 'fuga', 'provident', 'praesentium', 'rem',
-        'necessitatibus', 'suscipit', 'adipisci', 'quidem', 'possimus',
-        'voluptas', 'debitis', 'sint', 'accusantium', 'unde', 'sapiente',
-        'voluptate', 'qui', 'aspernatur', 'laudantium', 'soluta', 'amet',
-        'quo', 'aliquam', 'saepe', 'culpa', 'libero', 'ipsa', 'dicta
... (cut, so use `git log -L` for the rest)
````

</details>

## L016  redis  `src/sparsearray.c:258`

```
     254 
     255 /* Create a new sparse slice */
     256 arSlice *arSliceSparseNew(redisArray *ar) {
     257     uint32_t cap = (ArraySparseKMax < 4) ? ArraySparseKMax : 4;
>>   258     arSlice *s = arAllocAndTrack(ar, arSparseAllocSize(cap));
     259     s->encoding = AR_SLICE_SPARSE;
     260     s->count = 0;
     261     s->layout.sparse.cap = cap;
     262     arSparseSetupPointers(s);
```

**Candidate commits, oldest first:**

- `0d9576435f`  2026-05-13  Implement the new Redis Array type (#15162)

<details><summary>Line history</summary>

````diff
### 0d9576435  2026-05-13  Implement the new Redis Array type (#15162)

diff --git a/src/sparsearray.c b/src/sparsearray.c
--- /dev/null
+++ b/src/sparsearray.c
@@ -0,0 +258,1 @@
+    arSlice *s = arAllocAndTrack(ar, arSparseAllocSize(cap));

````

</details>

## L017  django  `django/contrib/gis/utils/layermapping.py:489`

```
     485                 "No ForeignKey %s model found with keyword arguments: %s"
     486                 % (rel_model.__name__, fk_kwargs)
     487             )
     488 
>>   489     def verify_geom(self, geom, model_field):
     490         """
     491         Verify the geometry -- construct and return a GeometryCollection
     492         if necessary (for example if the model field is MultiPolygonField while
     493         the mapped shapefile only contains Polygons).
```

**Candidate commits, oldest first:**

- `79e68c225b`  2008-08-05  Merged the gis branch into trunk.

<details><summary>Line history</summary>

````diff
### 79e68c225b  2008-08-05  Merged the gis branch into trunk.

diff --git a/django/contrib/gis/utils/layermapping.py b/django/contrib/gis/utils/layermapping.py
--- /dev/null
+++ b/django/contrib/gis/utils/layermapping.py
@@ -0,0 +475,1 @@
+    def verify_geom(self, geom, model_field):

````

</details>

## L018  django  `django/core/management/sql.py:32`

```
      28             stdout = kwargs.get("stdout", sys.stdout)
      29             stdout.write(
      30                 "Running pre-migrate handlers for application %s" % app_config.label
      31             )
>>    32         models.signals.pre_migrate.send(
      33             sender=app_config,
      34             app_config=app_config,
      35             verbosity=verbosity,
      36             interactive=interactive,
```

**Candidate commits, oldest first:**

- `3de1288042`  2013-05-23  Fixed #11398 - Added a pre_syncdb signal
- `68e0a169c4`  2013-07-30  Rename pre_ and post_syncdb to *_migrate, with aliases from old names
- `2732edc5f2`  2013-12-17  Deprecated get_apps().

<details><summary>Line history</summary>

````diff
### 2732edc5f2  2013-12-14  Deprecated get_apps().

diff --git a/django/core/management/sql.py b/django/core/management/sql.py
--- a/django/core/management/sql.py
+++ b/django/core/management/sql.py
@@ -213,6 +213,1 @@
-            print("Running pre-migrate handlers for application %s" % app_name)
-        models.signals.pre_migrate.send(sender=app, app=app,
-                                       create_models=create_models,
-                                       verbosity=verbosity,
-                                       interactive=interactive,
-                                       db=db)
+        models.signals.pre_migrate.send(
### 68e0a169c4  2013-07-30  Rename pre_ and post_syncdb to *_migrate, with aliases from old names

diff --git a/django/core/management/sql.py b/django/core/management/sql.py
--- a/django/core/management/sql.py
+++ b/django/core/management/sql.py
@@ -200,6 +200,6 @@
-            print("Running pre-sync handlers for application %s" % app_name)
-        models.signals.pre_syncdb.send(sender=app, app=app,
+            print("Running pre-migrate handlers for application %s" % app_name)
+        models.signals.pre_migrate.send(sender=app, app=app,
                                        create_models=create_models,
                                        verbosity=verbosity,
                                        interactive=interactive,
                                        db=db)
### 3de1288042  2013-05-17  Fixed #11398 - Added a pre_syncdb signal

diff --git a/django/core/management/sql.py b/django/core/management/sql.py
--- a/django/core/management/sql.py
+++ b/django/core/management/sql.py
@@ -194,0 +200,6 @@
+            print("Running pre-sync handlers for application %s" % app_name)
+        models.signals.pre_syncdb.send(sender=app, app=app,
+                                       create_models=create_models,
+                                       verbosity=verbosity,
+                                       interactive=interactive,
+                                       db=db)

````

</details>

## L019  django  `django/http/response.py:297`

```
     293     def set_signed_cookie(self, key, value, salt="", **kwargs):
     294         value = signing.get_cookie_signer(
     295             salt=signing._cookie_signer_salt(key, salt)
     296         ).sign(value)
>>   297         return self.set_cookie(key, value, **kwargs)
     298 
     299     def delete_cookie(self, key, path="/", domain=None, samesite=None):
     300         # Browsers can ignore the Set-Cookie header if the cookie doesn't use
     301         # the secure flag and either:
```

**Candidate commits, oldest first:**

- `f60d428463`  2011-05-21  Fixed #12417 -- Added signing functionality, including signing cookies. Many thanks to Sim
- `b4066d7d21`  2012-10-21  Cleaned up the the http module. Moved all of the code from __init__.py to request.py, resp

<details><summary>Line history</summary>

````diff
### b4066d7d21  2012-10-21  Cleaned up the the http module. Moved all of the code from __init__.py to request.py, response.py and utils.py

diff --git a/django/http/response.py b/django/http/response.py
--- /dev/null
+++ b/django/http/response.py
@@ -0,0 +184,1 @@
+        return self.set_cookie(key, value, **kwargs)

````

</details>

## L020  redis  `src/server.h:1079`

```
    1075     list *module_configs; /* List of configurations the module has registered */
    1076     ModuleConfigsApplied configs_initialized; /* Have the module configurations been initialized? */
    1077     int in_call;    /* RM_Call() nesting level */
    1078     int in_hook;    /* Hooks callback nesting level for this module (0 or 1). */
>>  1079     int options;    /* Module options and capabilities. */
    1080     int blocked_clients;         /* Count of RedisModuleBlockedClient in this module. */
    1081     size_t reply_buffers;        /* Owned reply buffers keep the module loaded. */
    1082     RedisModuleInfoFunc info_cb; /* Callback for module to add INFO fields. */
    1083     RedisModuleDefragFunc defrag_cb;    /* Callback for global data defrag. */
```

**Candidate commits, oldest first:**

- `4339706e07`  2019-07-30  Avoid diskelss-load if modules did not declare they handle read errors
- `b7b23bdfb8`  2019-09-26  INFO: more info about loaded modules.
- `babe3c7b29`  2021-06-01  Modules: rewrite config loadmodule option

<details><summary>Line history</summary>

````diff
### babe3c7b2  2018-04-20  Modules: rewrite config loadmodule option

diff --git a/src/server.h b/src/server.h
--- a/src/server.h
+++ b/src/server.h
@@ -609,0 +625,1 @@
+    int options;    /* Module options and capabilities. */

````

</details>

## L021  django  `django/db/backends/base/client.py:30`

```
      26     def runshell(self, parameters):
      27         args, env = self.settings_to_cmd_args_env(
      28             self.connection.settings_dict, parameters
      29         )
>>    30         env = {**os.environ, **env} if env else None
      31         subprocess.run(args, env=env, check=True)
```

**Candidate commits, oldest first:**

- `bbe6fbb876`  2020-10-29  Refs #32061 -- Unified DatabaseClient.runshell() in db backends.
- `6e742dabc9`  2021-04-27  Fixed #32687 -- Restored passing process’ environment to underlying tool in dbshell on Pos

<details><summary>Line history</summary>

````diff
### 6e742dabc9  2021-04-26  Fixed #32687 -- Restored passing process’ environment to underlying tool in dbshell on PostgreSQL.

diff --git a/django/db/backends/base/client.py b/django/db/backends/base/client.py
--- a/django/db/backends/base/client.py
+++ b/django/db/backends/base/client.py
@@ -24,2 +24,1 @@
-        if env:
-            env = {**os.environ, **env}
+        env = {**os.environ, **env} if env else None
### bbe6fbb876  2020-10-04  Refs #32061 -- Unified DatabaseClient.runshell() in db backends.

diff --git a/django/db/backends/base/client.py b/django/db/backends/base/client.py
--- a/django/db/backends/base/client.py
+++ b/django/db/backends/base/client.py
@@ -12,1 +24,2 @@
-        raise NotImplementedError('subclasses of BaseDatabaseClient must provide a runshell() method')
+        if env:
+            env = {**os.environ, **env}
### 28308078f3  2015-01-12  Fixed #22603 -- Reorganized classes in django.db.backends.

diff --git a/django/db/backends/base/client.py b/django/db/backends/base/client.py
--- /dev/null
+++ b/django/db/backends/base/client.py
@@ -0,0 +15,1 @@
+        raise NotImplementedError('subclasses of BaseDatabaseClient must provide a runshell() method')

````

</details>

## L022  django  `django/contrib/gis/gdal/raster/base.py:53`

```
      49             counter = 0
      50             item = data[counter]
      51             while item:
      52                 key, val = item.decode().split("=")
>>    53                 domain_meta[key] = val
      54                 counter += 1
      55                 item = data[counter]
      56             # The default domain values are returned if domain is None.
      57             result[domain or "DEFAULT"] = domain_meta
```

**Candidate commits, oldest first:**

- `e0b456bee7`  2017-06-07  Fixed #28232 -- Made raster metadata readable and writable on GDALRaster/Band.

<details><summary>Line history</summary>

````diff
### e0b456bee7  2017-05-23  Fixed #28232 -- Made raster metadata readable and writable on GDALRaster/Band.

diff --git a/django/contrib/gis/gdal/raster/base.py b/django/contrib/gis/gdal/raster/base.py
--- /dev/null
+++ b/django/contrib/gis/gdal/raster/base.py
@@ -0,0 +55,1 @@
+                domain_meta[key] = val

````

</details>

## L023  redis  `src/chk.c:615`

```
     611     for (int i = 0; i < k; i++) {
     612         if (list[i].item != NULL &&
     613             sdslen(list[i].item) == (size_t)itemlen &&
     614             memcmp(list[i].item, item, itemlen) == 0) {
>>   615             return i;
     616         }
     617     }
     618     return -1;
     619 }
```

**Candidate commits, oldest first:**

- `c93e4a62c6`  2026-01-16  Add hotkeys detection (#14680)

<details><summary>Line history</summary>

````diff
### c93e4a62c  2026-01-16  Add hotkeys detection (#14680)

diff --git a/src/chk.c b/src/chk.c
--- /dev/null
+++ b/src/chk.c
@@ -0,0 +615,1 @@
+            return i;

````

</details>

## L024  django  `django/db/models/fields/related.py:1058`

```
    1054 
    1055     def check(self, **kwargs):
    1056         databases = kwargs.get("databases") or []
    1057         return [
>>  1058             *super().check(**kwargs),
    1059             *self._check_on_delete(databases),
    1060             *self._check_unique(),
    1061         ]
    1062 
```

**Candidate commits, oldest first:**

- `d818e0c9b2`  2014-01-20  Fixed #16905 -- Added extensible checks (nee validation) framework
- `d6eaf7c018`  2017-01-25  Refs #23919 -- Replaced super(ClassName, self) with super().
- `d13a9e44de`  2017-12-11  Fixed #28909 -- Simplified code using tuple/list/set/dict unpacking.

<details><summary>Line history</summary>

````diff
### d13a9e44de  2017-12-11  Fixed #28909 -- Simplified code using tuple/list/set/dict unpacking.

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -818,4 +821,1 @@
-        errors = super().check(**kwargs)
-        errors.extend(self._check_on_delete())
-        errors.extend(self._check_unique())
-        return errors
+            *super().check(**kwargs),
### d6eaf7c018  2017-01-21  Refs #23919 -- Replaced super(ClassName, self) with super().

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -804,4 +803,4 @@
-        errors = super(ForeignKey, self).check(**kwargs)
+        errors = super().check(**kwargs)
         errors.extend(self._check_on_delete())
         errors.extend(self._check_unique())
         return errors
### f39b0421b4  2014-09-08  Fixed #23338 -- Added warning when unique=True on ForeigKey

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -1711,3 +1711,4 @@
         errors = super(ForeignKey, self).check(**kwargs)
         errors.extend(self._check_on_delete())
+        errors.extend(self._check_unique())
         return errors
### d818e0c9b2  2014-01-20  Fixed #16905 -- Added extensible checks (nee validation) framework

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -1355,0 +1559,3 @@
+        errors = super(ForeignKey, self).check(**kwargs)
+        errors.extend(self._check_on_delete())
+        return errors

````

</details>

## L025  redis  `src/module.c:13966`

```
   13962     zfree(cmd->key_specs);
   13963     for (int j = 0; cmd->tips && cmd->tips[j]; j++)
   13964         zfree((char *)cmd->tips[j]);
   13965     zfree(cmd->tips);
>> 13966     for (int j = 0; cmd->history && cmd->history[j].since; j++) {
   13967         zfree((char *)cmd->history[j].since);
   13968         zfree((char *)cmd->history[j].changes);
   13969     }
   13970     zfree(cmd->history);
```

**Candidate commits, oldest first:**

- `867816003e`  2021-12-15  Auto-generate the command table from JSON files (#9656)
- `23325c135f`  2022-01-23  sub-command support for ACL CAT and COMMAND LIST. redisCommand always stores fullname (#10

<details><summary>Line history</summary>

````diff
### 23325c135  2022-01-23  sub-command support for ACL CAT and COMMAND LIST. redisCommand always stores fullname (#10127)

diff --git a/src/module.c b/src/module.c
--- a/src/module.c
+++ b/src/module.c
@@ -9968,0 +9999,1 @@
+    for (int j = 0; cmd->history && cmd->history[j].since; j++) {

````

</details>

## L026  redis  `src/redis-cli.c:8316`

```
    8312      * slots are always matched by nodes receiving slots. */
    8313     while (total_balance > 0) {
    8314         listRewind(involved, &li);
    8315         while ((ln = listNext(&li)) != NULL) {
>>  8316             clusterManagerNode *n = ln->value;
    8317             if (n->balance <= 0 && total_balance > 0) {
    8318                 n->balance--;
    8319                 total_balance--;
    8320             }
```

**Candidate commits, oldest first:**

- `486c7af7b8`  2018-04-23  Cluster Manager: 'create', 'info' and 'check' commands
- `6d1a7cec23`  2018-04-23  Cluster Manager: rebalance command

<details><summary>Line history</summary>

````diff
### 6d1a7cec2  2018-03-23  Cluster Manager: rebalance command

diff --git a/src/redis-cli.c b/src/redis-cli.c
--- a/src/redis-cli.c
+++ b/src/redis-cli.c
@@ -3781,2 +3973,1 @@
-            clusterManagerReshardTableItem *item = ln->value;
-            zfree(item);
+            clusterManagerNode *n = ln->value;
### 99da9c950  2018-02-28  Cluster Manager: reshard command, fixed slots parsing bug and other minor bugs.

diff --git a/src/redis-cli.c b/src/redis-cli.c
--- a/src/redis-cli.c
+++ b/src/redis-cli.c
@@ -3272,3 +3774,2 @@
-    fprintf(stderr, "Invalid arguments: you need to pass either a valid "
-                    "address (ie. 120.0.0.1:7000) or space separated IP "
-                    "and port (ie. 120.0.0.1 7000)\n");
+            clusterManagerReshardTableItem *item = ln->value;
+            zfree(item);
### 486c7af7b  2018-01-31  Cluster Manager: 'create', 'info' and 'check' commands

diff --git a/src/redis-cli.c b/src/redis-cli.c
--- a/src/redis-cli.c
+++ b/src/redis-cli.c
@@ -1662,0 +2885,3 @@
+    fprintf(stderr, "Invalid arguments: you need to pass either a valid "
+                    "address (ie. 120.0.0.1:7000) or space separated IP "
+                    "and port (ie. 120.0.0.1 7000)\n");

````

</details>

## L027  django  `django/db/backends/postgresql/base.py:252`

```
     248 
     249     def get_connection_params(self):
     250         settings_dict = self.settings_dict
     251         # None may be used to connect to the default 'postgres' db
>>   252         if settings_dict["NAME"] == "" and not settings_dict["OPTIONS"].get("service"):
     253             raise ImproperlyConfigured(
     254                 "settings.DATABASES is improperly configured. "
     255                 "Please supply the NAME or OPTIONS['service'] value."
     256             )
```

**Candidate commits, oldest first:**

- `dcb3ad3319`  2021-01-20  Fixed #32292 -- Added support for connection by service name to PostgreSQL.
- `50e95ad536`  2024-02-23  Simplified using DATABASES["OPTIONS"].

<details><summary>Line history</summary>

````diff
### 50e95ad536  2024-02-23  Simplified using DATABASES["OPTIONS"].

diff --git a/django/db/backends/postgresql/base.py b/django/db/backends/postgresql/base.py
--- a/django/db/backends/postgresql/base.py
+++ b/django/db/backends/postgresql/base.py
@@ -193,3 +193,1 @@
-        if settings_dict["NAME"] == "" and not settings_dict.get("OPTIONS", {}).get(
-            "service"
-        ):
+        if settings_dict["NAME"] == "" and not settings_dict["OPTIONS"].get("service"):
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/db/backends/postgresql/base.py b/django/db/backends/postgresql/base.py
--- a/django/db/backends/postgresql/base.py
+++ b/django/db/backends/postgresql/base.py
@@ -155,4 +159,3 @@
-        if (
-            settings_dict['NAME'] == '' and
-            not settings_dict.get('OPTIONS', {}).get('service')
+        if settings_dict["NAME"] == "" and not settings_dict.get("OPTIONS", {}).get(
+            "service"
         ):
### dcb3ad3319  2020-12-23  Fixed #32292 -- Added support for connection by service name to PostgreSQL.

diff --git a/django/db/backends/postgresql/base.py b/django/db/backends/postgresql/base.py
--- a/django/db/backends/postgresql/base.py
+++ b/django/db/backends/postgresql/base.py
@@ -155,1 +155,4 @@
-        if settings_dict['NAME'] == '':
+        if (
+            settings_dict['NAME'] == '' and
+            not settings_dict.get('OPTIONS', {}).get('service')
+        ):
### e953c78eeb  2013-11-09  Fixed #16969 -- Don't connect to named database when possible

diff --git a/django/db/backends/postgresql_psycopg2/base.py b/django/db/backends/postgresql_psycopg2/base.py
--- a/django/db/backends/postgresql_psycopg2/base.py
+++ b/django/db/backends/postgresql_psycopg2/base.py
@@ -104,1 +105,1 @@
-        if not settings_dict['NAME']:
+        if settings_dict['NAME'] == '':
### 1893467784  2012-11-26  Fixed #19274 -- Made db connection creation overridable in subclasses

diff --git a/django/db/backends/postgresql_psycopg2/base.py b/django/db/backends/postgresql_psycopg2/base.py
--- a/django/db/backends/postgresql_psycopg2/base.py
+++ b/django/db/backends/postgresql_psycopg2/base.py
@@ -159,1 +161,1 @@
-    def _cursor(self):
+        if not settings_dict['NAME']:
### 315145f7ca  2009-03-11  Fixed #10459 -- Refactored the internals of database connection objects so that connections know their own settings and pass around settings as dictionaries instead of passing around the Django settings module itself. This will make it easier for multiple database support. Thanks to Alex Gaynor for the initial patch.

diff --git a/django/db/backends/postgresql_psycopg2/base.py b/django/db/backends/postgresql_psycopg2/base.py
--- a/django/db/backends/postgresql_psycopg2/base.py
+++ b/django/db/backends/postgresql_psycopg2/base.py
@@ -68,1 +68,1 @@
-    def _cursor(self, settings):
+    def _cursor(self):
### 7c41b19c8a  2007-08-19  Refactored all database backends to inherit from a common base class to remove quite a bit of duplicated code. Thanks for the patch, Brian Harring. Refs #5106

diff --git a/django/db/backends/postgresql_psycopg2/base.py b/django/db/backends/postgresql_psycopg2/base.py
--- a/django/db/backends/postgresql_psycopg2/base.py
+++ b/django/db/backends/postgresql_psycopg2/base.py
@@ -29,8 +23,1 @@
-class DatabaseWrapper(local):
-    def __init__(self, **kwargs):
-        self.connection = None
-        self.queries = []
-        self.options = kwargs
-
-   
... (cut, so use `git log -L` for the rest)
````

</details>

## L028  django  `django/contrib/sites/shortcuts.py:13`

```
       9     ``Site`` object or a ``RequestSite`` object based on the request.
      10     """
      11     # Import is inside the function because its point is to avoid importing the
      12     # Site models when django.contrib.sites isn't installed.
>>    13     if apps.is_installed("django.contrib.sites"):
      14         from .models import Site
      15 
      16         return Site.objects.get_current(request)
      17     else:
```

**Candidate commits, oldest first:**

- `9ffab9cee1`  2014-01-26  Moved RequestSite and get_current_site.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/contrib/sites/shortcuts.py b/django/contrib/sites/shortcuts.py
--- a/django/contrib/sites/shortcuts.py
+++ b/django/contrib/sites/shortcuts.py
@@ -13,1 +13,1 @@
-    if apps.is_installed('django.contrib.sites'):
+    if apps.is_installed("django.contrib.sites"):
### 9ffab9cee1  2014-01-25  Moved RequestSite and get_current_site.

diff --git a/django/contrib/sites/shortcuts.py b/django/contrib/sites/shortcuts.py
--- /dev/null
+++ b/django/contrib/sites/shortcuts.py
@@ -0,0 +13,1 @@
+    if apps.is_installed('django.contrib.sites'):

````

</details>

## L029  django  `django/contrib/contenttypes/forms.py:86`

```
      82     fk_field="object_id",
      83     fields=None,
      84     exclude=None,
      85     extra=3,
>>    86     can_order=False,
      87     can_delete=True,
      88     max_num=None,
      89     formfield_callback=None,
      90     validate_max=False,
```

**Candidate commits, oldest first:**

- `02cc59187b`  2008-08-10  Fixed #4667 -- Added support for inline generic relations in the admin. Thanks to Honza Kr
- `10e3faf191`  2014-01-26  Fixed #19774 -- Deprecated the contenttypes.generic module.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/contrib/contenttypes/forms.py b/django/contrib/contenttypes/forms.py
--- a/django/contrib/contenttypes/forms.py
+++ b/django/contrib/contenttypes/forms.py
@@ -52,9 +86,1 @@
-def generic_inlineformset_factory(model, form=ModelForm,
-                                  formset=BaseGenericInlineFormSet,
-                                  ct_field="content_type", fk_field="object_id",
-                                  fields=None, exclude=None,
-                                  extra=3, can_order=False, can_delete=True,
-                                  max_num=None, formfield_callback=None,
-                                  validate_max=False, for_concrete_model=True,
-                                  min_num=None, validate_min=False,
-                                  absolute_max=None, can_delete_extra=True):
+    can_order=False,
### 35b03788b0  2020-08-17  Refs #9061 -- Allowed GenericInlineFormSet to disable deleting extra forms.

diff --git a/django/contrib/contenttypes/forms.py b/django/contrib/contenttypes/forms.py
--- a/django/contrib/contenttypes/forms.py
+++ b/django/contrib/contenttypes/forms.py
@@ -52,9 +52,9 @@
 def generic_inlineformset_factory(model, form=ModelForm,
                                   formset=BaseGenericInlineFormSet,
                                   ct_field="content_type", fk_field="object_id",
                                   fields=None, exclude=None,
                                   extra=3, can_order=False, can_delete=True,
                                   max_num=None, formfield_callback=None,
                                   validate_max=False, for_concrete_model=True,
                                   min_num=None, validate_min=False,
-                                  absolute_max=None):
+                                  absolute_max=None, can_delete_extra=True):
### 3254991762  2020-08-17  Refs #20347 -- Allowed customizing the maximum number of instantiated forms in generic_inlineformset_factory().

diff --git a/django/contrib/contenttypes/forms.py b/django/contrib/contenttypes/forms.py
--- a/django/contrib/contenttypes/forms.py
+++ b/django/contrib/contenttypes/forms.py
@@ -52,8 +52,9 @@
 def generic_inlineformset_factory(model, form=ModelForm,
                                   formset=BaseGenericInlineFormSet,
                                   ct_field="content_type", fk_field="object_id",
                                   fields=None, exclude=None,
                                   extra=3, can_order=False, can_delete=True,
                                   max_num=None, formfield_callback=None,
                                   validate_max=False, for_concrete_model=True,
-                                  min_num=None, validate_min=False):
+                                  min_num=None, validate_min=False,
+                                  absolute_max=None):
### 4ef10f245a  2014-03-05  Fixed #17642 -- Added min_num support to modelformsets, inlines, and the admin.

diff --git a/django/contrib/contenttypes/forms.py b/django/contrib/contenttypes/forms.py
--- a/django/contrib/contenttypes/forms.py
+++ b/django/contrib/contenttypes/forms.py
@@ -54,8 +54,8 @@
 def generic_inlineformset_factory(model, form=ModelForm,
                                   formset=BaseGenericInlineFormSet,
                                   ct_field="content_type", fk_field="object_id",
                 
... (cut, so use `git log -L` for the rest)
````

</details>

## L030  django  `django/db/models/query.py:308`

```
     304         query = queryset.query
     305         compiler = query.get_compiler(queryset.db)
     306         return compiler.results_iter(
     307             tuple_expected=True,
>>   308             chunked_fetch=self.chunked_fetch,
     309             chunk_size=self.chunk_size,
     310         )
     311 
     312 
```

**Candidate commits, oldest first:**

- `d97f026a7a`  2017-11-21  Fixed #28817 -- Made QuerySet.iterator() use server-side cursors after values() and values
- `3187c89d6f`  2018-01-26  Fixed #29067 -- Fixed regression in QuerySet.values_list(..., flat=True) followed by annot
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/db/models/query.py b/django/db/models/query.py
--- a/django/db/models/query.py
+++ b/django/db/models/query.py
@@ -141,1 +171,1 @@
-        return compiler.results_iter(tuple_expected=True, chunked_fetch=self.chunked_fetch, chunk_size=self.chunk_size)
+            chunked_fetch=self.chunked_fetch,
### d97f026a7a  2017-11-19  Fixed #28817 -- Made QuerySet.iterator() use server-side cursors after values() and values_list().

diff --git a/django/db/models/query.py b/django/db/models/query.py
--- a/django/db/models/query.py
+++ b/django/db/models/query.py
@@ -136,2 +140,1 @@
-                return map(rowfactory, compiler.results_iter())
-        return compiler.results_iter(tuple_expected=True)
+        return compiler.results_iter(tuple_expected=True, chunked_fetch=self.chunked_fetch, chunk_size=self.chunk_size)
### dca67bb2c2  2017-08-24  Refs #28459 -- Improved performance of SQLCompiler.apply_converters().

diff --git a/django/db/models/query.py b/django/db/models/query.py
--- a/django/db/models/query.py
+++ b/django/db/models/query.py
@@ -136,2 +135,2 @@
-                results = map(rowfactory, results)
-        return results
+                return map(rowfactory, compiler.results_iter())
+        return compiler.results_iter(tuple_expected=True)
### 2d136ede8a  2017-08-01  Fixed #28459 -- Improved performance of ValuesListIterable.

diff --git a/django/db/models/query.py b/django/db/models/query.py
--- a/django/db/models/query.py
+++ b/django/db/models/query.py
@@ -132,7 +134,2 @@
-                fields = list(queryset._fields) + [f for f in annotation_names if f not in queryset._fields]
-            else:
-                fields = names
-
-            for row in compiler.results_iter():
-                data = dict(zip(names, row))
-                yield tuple(data[f] for f in fields)
+                results = map(rowfactory, results)
+        return results
### 4c3bfe9053  2015-01-30  Fixed #24211 -- Removed ValuesQuerySet() and ValuesListQuerySet().

diff --git a/django/db/models/query.py b/django/db/models/query.py
--- a/django/db/models/query.py
+++ b/django/db/models/query.py
@@ -42,1 +141,7 @@
-    See `__reduce__` for more details.
+                fields = list(queryset._fields) + [f for f in annotation_names if f not in queryset._fields]
+            else:
+                fields = names
+
+            for row in compiler.results_iter():
+                data = dict(zip(names, row))
+                yield tuple(data[f] for f in fields)
### 31fadc1202  2013-07-26  Fixed #20625 -- Chainable Manager/QuerySet methods.

diff --git a/django/db/models/query.py b/django/db/models/query.py
--- a/django/db/models/query.py
+++ b/django/db/models/query.py
@@ -33,0 +38,1 @@
+    See `__reduce__` for more details.

````

</details>

## L031  django  `django/core/files/images.py:61`

```
      57         # parse the whole file.
      58         chunk_size = 1024
      59         while 1:
      60             data = file.read(chunk_size)
>>    61             if not data:
      62                 break
      63             try:
      64                 p.feed(data)
      65             except zlib.error as e:
```

**Candidate commits, oldest first:**

- `7899568e01`  2008-08-08  File storage refactoring, adding far more flexibility to Django's file handling. The new f
- `a7faf6424a`  2009-05-08  Fixed #8817: get_image_dimensions correctly closes the files it opens, and leaves open the

<details><summary>Line history</summary>

````diff
### a7faf6424a  2009-05-08  Fixed #8817: get_image_dimensions correctly closes the files it opens, and leaves open the ones it doesn't. Thanks, mitsuhiko.

diff --git a/django/core/files/images.py b/django/core/files/images.py
--- a/django/core/files/images.py
+++ b/django/core/files/images.py
@@ -35,8 +40,1 @@
-    while 1:
-        data = file.read(1024)
-        if not data:
-            break
-        p.feed(data)
-        if p.image:
-            return p.image.size
-    return None
+            if not data:
### 7899568e01  2008-08-08  File storage refactoring, adding far more flexibility to Django's file handling. The new files.txt document has details of the new features.

diff --git a/django/core/files/images.py b/django/core/files/images.py
--- /dev/null
+++ b/django/core/files/images.py
@@ -0,0 +35,8 @@
+    while 1:
+        data = file.read(1024)
+        if not data:
+            break
+        p.feed(data)
+        if p.image:
+            return p.image.size
+    return None

````

</details>

## L032  redis  `src/script_lua.c:1233`

```
    1229     luaLoadLib(lua, LUA_DBLIBNAME, luaopen_debug);
    1230     luaLoadLib(lua, LUA_OSLIBNAME, luaopen_os);
    1231     luaLoadLib(lua, "cjson", luaopen_cjson);
    1232     luaLoadLib(lua, "struct", luaopen_struct);
>>  1233     luaLoadLib(lua, "cmsgpack", luaopen_cmsgpack);
    1234     luaLoadLib(lua, "bit", luaopen_bit);
    1235 
    1236 #if 0 /* Stuff that we don't load currently, for sandboxing concerns. */
    1237     luaLoadLib(lua, LUA_LOADLIBNAME, luaopen_package);
```

**Candidate commits, oldest first:**

- `63505e0b59`  2012-02-24  Lua_cmsgpack added to Redis scripting.
- `22aab1ce94`  2021-12-01  Redis Functions - Move code to make review process easier.

<details><summary>Line history</summary>

````diff
### 22aab1ce9  2021-10-05  Redis Functions - Move code to make review process easier.

diff --git a/src/script_lua.c b/src/script_lua.c
--- /dev/null
+++ b/src/script_lua.c
@@ -0,0 +1175,1 @@
+    luaLoadLib(lua, "cmsgpack", luaopen_cmsgpack);

````

</details>

## L033  django  `django/db/models/fields/related.py:1674`

```
    1670                             "through_fields keyword argument."
    1671                             % (self, from_model_name),
    1672                             hint=(
    1673                                 "Use through_fields to specify which two foreign keys "
>>  1674                                 "Django should use."
    1675                             ),
    1676                             obj=self.remote_field.through,
    1677                             id="fields.E333",
    1678                         )
```

**Candidate commits, oldest first:**

- `c627da0ccc`  2014-03-05  Fixed #14549 - Removed restriction of single FKs on intermediary tables
- `004ba0f99e`  2016-02-12  Removed unneeded hint=None/obj=None in system check messages.
- `7119f40c98`  2022-02-07  Refs #33476 -- Refactored code to strictly match 88 characters line length.

<details><summary>Line history</summary>

````diff
### 7119f40c98  2022-02-04  Refs #33476 -- Refactored code to strictly match 88 characters line length.

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -1485,1 +1498,1 @@
-                            hint="Use through_fields to specify which two foreign keys Django should use.",
+                                "Django should use."
### 004ba0f99e  2016-02-12  Removed unneeded hint=None/obj=None in system check messages.

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -1256,7 +1251,1 @@
-                            ("The model is used as an intermediate model by "
-                             "'%s', but it has more than two foreign keys "
-                             "to '%s', which is ambiguous. You must specify "
-                             "which two foreign keys Django should use via the "
-                             "through_fields keyword argument.") % (self, from_model_name),
-                            hint=("Use through_fields to specify which two "
-                                  "foreign keys Django should use."),
+                            hint="Use through_fields to specify which two foreign keys Django should use.",
### c627da0ccc  2014-02-19  Fixed #14549 - Removed restriction of single FKs on intermediary tables

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -1932,4 +1958,7 @@
                             ("The model is used as an intermediate model by "
                              "'%s', but it has more than two foreign keys "
-                             "to '%s', which is ambiguous.") % (self, from_model_name),
-                            hint=None,
+                             "to '%s', which is ambiguous. You must specify "
+                             "which two foreign keys Django should use via the "
+                             "through_fields keyword argument.") % (self, from_model_name),
+                            hint=("Use through_fields to specify which two "
+                                  "foreign keys Django should use."),
### 82ac389486  2014-03-03  Edited model and field checks for grammar and consistency.

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -1929,4 +1923,4 @@
-                            ('The model is used as an intermediary model by '
-                             '%s, but it has more than two foreign keys '
-                             'to %s, which is ambiguous and is not permitted.') % (self, from_model_name),
+                            ("The model is used as an intermediate model by "
+                             "'%s', but it has more than two foreign keys "
+                             "to '%s', which is ambiguous.") % (self, from_model_name),
                             hint=None,
### d818e0c9b2  2014-01-20  Fixed #16905 -- Added extensible checks (nee validation) framework

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -1585,0 +1888,4 @@
+       
... (cut, so use `git log -L` for the rest)
````

</details>

## L034  django  `django/conf/global_settings.py:55`

```
      51 
      52 # Languages we provide translations for, out of the box.
      53 LANGUAGES = [
      54     ("af", gettext_noop("Afrikaans")),
>>    55     ("ar", gettext_noop("Arabic")),
      56     ("ar-dz", gettext_noop("Algerian Arabic")),
      57     ("ast", gettext_noop("Asturian")),
      58     ("az", gettext_noop("Azerbaijani")),
      59     ("bg", gettext_noop("Bulgarian")),
```

**Candidate commits, oldest first:**

- `8c399ba5b6`  2006-07-10  fixed #2302: added arabic translation. thx Ahmad Alhashemi.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/conf/global_settings.py b/django/conf/global_settings.py
--- a/django/conf/global_settings.py
+++ b/django/conf/global_settings.py
@@ -57,97 +58,1 @@
-    ('af', gettext_noop('Afrikaans')),
-    ('ar', gettext_noop('Arabic')),
-    ('ar-dz', gettext_noop('Algerian Arabic')),
-    ('ast', gettext_noop('Asturian')),
-    ('az', gettext_noop('Azerbaijani')),
-    ('bg', gettext_noop('Bulgarian')),
-    ('be', gettext_noop('Belarusian')),
-    ('bn', gettext_noop('Bengali')),
-    ('br', gettext_noop('Breton')),
-    ('bs', gettext_noop('Bosnian')),
-    ('ca', gettext_noop('Catalan')),
-    ('cs', gettext_noop('Czech')),
-    ('cy', gettext_noop('Welsh')),
-    ('da', gettext_noop('Danish')),
-    ('de', gettext_noop('German')),
-    ('dsb', gettext_noop('Lower Sorbian')),
-    ('el', gettext_noop('Greek')),
-    ('en', gettext_noop('English')),
-    ('en-au', gettext_noop('Australian English')),
-    ('en-gb', gettext_noop('British English')),
-    ('eo', gettext_noop('Esperanto')),
-    ('es', gettext_noop('Spanish')),
-    ('es-ar', gettext_noop('Argentinian Spanish')),
-    ('es-co', gettext_noop('Colombian Spanish')),
-    ('es-mx', gettext_noop('Mexican Spanish')),
-    ('es-ni', gettext_noop('Nicaraguan Spanish')),
-    ('es-ve', gettext_noop('Venezuelan Spanish')),
-    ('et', gettext_noop('Estonian')),
-    ('eu', gettext_noop('Basque')),
-    ('fa', gettext_noop('Persian')),
-    ('fi', gettext_noop('Finnish')),
-    ('fr', gettext_noop('French')),
-    ('fy', gettext_noop('Frisian')),
-    ('ga', gettext_noop('Irish')),
-    ('gd', gettext_noop('Scottish Gaelic')),
-    ('gl', gettext_noop('Galician')),
-    ('he', gettext_noop('Hebrew')),
-    ('hi', gettext_noop('Hindi')),
-    ('hr', gettext_noop('Croatian')),
-    ('hsb', gettext_noop('Upper Sorbian')),
-    ('hu', gettext_noop('Hungarian')),
-    ('hy', gettext_noop('Armenian')),
-    ('ia', gettext_noop('Interlingua')),
-    ('id', gettext_noop('Indonesian')),
-    ('ig', gettext_noop('Igbo')),
-    ('io', gettext_noop('Ido')),
-    ('is', gettext_noop('Icelandic')),
-    ('it', gettext_noop('Italian')),
-    ('ja', gettext_noop('Japanese')),
-    ('ka', gettext_noop('Georgian')),
-    ('kab', gettext_noop('Kabyle')),
-    ('kk', gettext_noop('Kazakh')),
-    ('km', gettext_noop('Khmer')),
-    ('kn', gettext_noop('Kannada')),
-    ('ko', gettext_noop('Korean')),
-    ('ky', gettext_noop('Kyrgyz')),
-    ('lb', gettext_noop('Luxembourgish')),
-    ('lt', gettext_noop('Lithuanian')),
-    ('lv', gettext_noop('Latvian')),
-    ('mk', gettext_noop('Macedonian')),
-    ('ml', gettext_noop('Malayalam')),
-    ('mn', gettext_noop('Mongolian')),
-    ('mr', gettext_noop('Marathi')),
-    ('ms', gettext_noop('Malay')),
-    ('my', gettext_noop('Burmese')),
-    ('nb', gettext_noop('Norwegian Bokmål')),
-    ('ne', gettext_noop('Nepali')),
-    ('nl', gettext_noop('Dutch')),
-    ('nn', gettext_noop('Norwegian Nynorsk')),
-    ('os', gettext_noop('Ossetic')),
-    ('pa', gettext_noop('Punjabi')),
-    ('pl', gettext_noop('Polish')),
-    ('pt', gettext_noop('Portuguese')),
-    ('pt-br', gettext_noop('Brazilian Portuguese')),
-    ('ro', gettext_noop('Romanian')),
-    ('ru', gettext_noop('Russian')),
-    ('sk', gettext_noop('Slovak')),
-    ('sl', gettext_noop('Slovenian')),
-    ('sq', gettext_noop('Albanian')),
-    ('sr', gettext_noop('Serbian')),
-    ('sr-latn', gettext_noop('Serbian
... (cut, so use `git log -L` for the rest)
````

</details>

## L035  redis  `src/redis-cli.c:7205`

```
    7201         for (; slot < CLUSTER_MANAGER_SLOTS; slot++) {
    7202             listIter li;
    7203             listNode *ln;
    7204             listRewind(cluster_manager.nodes, &li);
>>  7205             list *owners = listCreate();
    7206             while ((ln = listNext(&li)) != NULL) {
    7207                 clusterManagerNode *n = ln->value;
    7208                 if (n->flags & CLUSTER_MANAGER_FLAG_SLAVE) continue;
    7209                 if (n->slots[slot]) listAddNodeTail(owners, n);
```

**Candidate commits, oldest first:**

- `3f8a4adb49`  2018-04-23  Cluster Manager: fix command.
- `5bf13eaaf8`  2018-12-10  Cluster Manager: check/fix commands now handle multiple owners even if all slots are cover

<details><summary>Line history</summary>

````diff
### 5bf13eaaf  2018-11-22  Cluster Manager: check/fix commands now handle multiple owners even if all slots are covered and not open.

diff --git a/src/redis-cli.c b/src/redis-cli.c
--- a/src/redis-cli.c
+++ b/src/redis-cli.c
@@ -4168,0 +4257,1 @@
+            list *owners = listCreate();

````

</details>

## L036  redis  `src/script_lua.c:210`

```
     206     .set_callback = redisProtocolToLuaType_Set,
     207     .map_callback = redisProtocolToLuaType_Map,
     208     .bool_callback = redisProtocolToLuaType_Bool,
     209     .double_callback = redisProtocolToLuaType_Double,
>>   210     .null_callback = redisProtocolToLuaType_Null,
     211     .big_number_callback = redisProtocolToLuaType_BigNumber,
     212     .verbatim_string_callback = redisProtocolToLuaType_VerbatimString,
     213     .attribute_callback = redisProtocolToLuaType_Attribute,
     214     .error = NULL,
```

**Candidate commits, oldest first:**

- `2237131e15`  2021-08-04  Unified Lua and modules reply parsing and added RESP3 support to RM_Call (#9202)
- `22aab1ce94`  2021-12-01  Redis Functions - Move code to make review process easier.

<details><summary>Line history</summary>

````diff
### 22aab1ce9  2021-10-05  Redis Functions - Move code to make review process easier.

diff --git a/src/script_lua.c b/src/script_lua.c
--- /dev/null
+++ b/src/script_lua.c
@@ -0,0 +95,1 @@
+    .null_callback = redisProtocolToLuaType_Null,

````

</details>

## L037  django  `django/db/backends/mysql/schema.py:41`

```
      37             # The name of the column check constraint is the same as the field
      38             # name on MariaDB. Adding IF EXISTS clause prevents migrations
      39             # crash. Constraint is removed during a "MODIFY" column statement.
      40             return "ALTER TABLE %(table)s DROP CONSTRAINT IF EXISTS %(name)s"
>>    41         return "ALTER TABLE %(table)s DROP CHECK %(name)s"
      42 
      43     def quote_value(self, value):
      44         self.connection.ensure_connection()
      45         # MySQLdb escapes to string, PyMySQL to bytes.
```

**Candidate commits, oldest first:**

- `1fc2c70f76`  2019-07-19  Fixed #30593 -- Added support for check constraints on MariaDB 10.2+.
- `e2c6a0858d`  2019-09-05  Fixed #30750 -- Added support for check constraints on MySQL 8.0.16+.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/db/backends/mysql/schema.py b/django/db/backends/mysql/schema.py
--- a/django/db/backends/mysql/schema.py
+++ b/django/db/backends/mysql/schema.py
@@ -38,2 +41,1 @@
-            return 'ALTER TABLE %(table)s DROP CONSTRAINT IF EXISTS %(name)s'
-        return 'ALTER TABLE %(table)s DROP CHECK %(name)s'
+        return "ALTER TABLE %(table)s DROP CHECK %(name)s"
### e2c6a0858d  2019-09-04  Fixed #30750 -- Added support for check constraints on MySQL 8.0.16+.

diff --git a/django/db/backends/mysql/schema.py b/django/db/backends/mysql/schema.py
--- a/django/db/backends/mysql/schema.py
+++ b/django/db/backends/mysql/schema.py
@@ -31,4 +38,2 @@
-    # The name of the column check constraint is the same as the field name on
-    # MariaDB. Adding IF EXISTS clause prevents migrations crash. Constraint is
-    # removed during a "MODIFY" column statement.
-    sql_delete_check = 'ALTER TABLE %(table)s DROP CONSTRAINT IF EXISTS %(name)s'
+            return 'ALTER TABLE %(table)s DROP CONSTRAINT IF EXISTS %(name)s'
+        return 'ALTER TABLE %(table)s DROP CHECK %(name)s'
### 1fc2c70f76  2019-07-14  Fixed #30593 -- Added support for check constraints on MariaDB 10.2+.

diff --git a/django/db/backends/mysql/schema.py b/django/db/backends/mysql/schema.py
--- a/django/db/backends/mysql/schema.py
+++ b/django/db/backends/mysql/schema.py
@@ -31,0 +31,4 @@
+    # The name of the column check constraint is the same as the field name on
+    # MariaDB. Adding IF EXISTS clause prevents migrations crash. Constraint is
+    # removed during a "MODIFY" column statement.
+    sql_delete_check = 'ALTER TABLE %(table)s DROP CONSTRAINT IF EXISTS %(name)s'

````

</details>

## L038  django  `django/http/response.py:488`

```
     484 
     485     @property
     486     def text(self):
     487         raise AttributeError(
>>   488             "This %s instance has no `text` attribute." % self.__class__.__name__
     489         )
     490 
     491     @property
     492     def streaming_content(self):
```

**Candidate commits, oldest first:**

- `4a685bc0dc`  2024-10-16  Fixed #35727 -- Added HttpResponse.text property.

<details><summary>Line history</summary>

````diff
### 4a685bc0dc  2024-09-11  Fixed #35727 -- Added HttpResponse.text property.

diff --git a/django/http/response.py b/django/http/response.py
--- a/django/http/response.py
+++ b/django/http/response.py
@@ -464,0 +472,1 @@
+            "This %s instance has no `text` attribute." % self.__class__.__name__

````

</details>

## L039  django  `django/contrib/gis/utils/layermapping.py:173`

```
     169         # Setting the transaction decorator with the function in the
     170         # transaction modes dictionary.
     171         self.transaction_mode = transaction_mode
     172         if transaction_mode == "autocommit":
>>   173             self.transaction_decorator = None
     174         elif transaction_mode == "commit_on_success":
     175             self.transaction_decorator = transaction.atomic
     176         else:
     177             raise LayerMapError("Unrecognized transaction mode: %s" % transaction_mode)
```

**Candidate commits, oldest first:**

- `79e68c225b`  2008-08-05  Merged the gis branch into trunk.
- `1adb7b3c38`  2013-03-11  Ported layermapping for autocommit.

<details><summary>Line history</summary>

````diff
### 1adb7b3c38  2013-03-11  Ported layermapping for autocommit.

diff --git a/django/contrib/gis/utils/layermapping.py b/django/contrib/gis/utils/layermapping.py
--- a/django/contrib/gis/utils/layermapping.py
+++ b/django/contrib/gis/utils/layermapping.py
@@ -130,3 +127,1 @@
-        if transaction_mode in self.TRANSACTION_MODES:
-            self.transaction_decorator = self.TRANSACTION_MODES[transaction_mode]
-            self.transaction_mode = transaction_mode
+            self.transaction_decorator = None
### 79e68c225b  2008-08-05  Merged the gis branch into trunk.

diff --git a/django/contrib/gis/utils/layermapping.py b/django/contrib/gis/utils/layermapping.py
--- /dev/null
+++ b/django/contrib/gis/utils/layermapping.py
@@ -0,0 +222,3 @@
+        if transaction_mode in self.TRANSACTION_MODES:
+            self.transaction_decorator = self.TRANSACTION_MODES[transaction_mode]
+            self.transaction_mode = transaction_mode

````

</details>

## L040  django  `django/conf/global_settings.py:17`

```
      13 ####################
      14 # CORE             #
      15 ####################
      16 
>>    17 DEBUG = False
      18 
      19 # Whether the framework should propagate raw exceptions rather than catching
      20 # them. This is useful under some testing situations and should never be used
      21 # on a live site.
```

**Candidate commits, oldest first:**

- `ed114e1510`  2005-07-13  Imported Django from private SVN repository (created from r. 8825)

<details><summary>Line history</summary>

````diff
### ed114e1510  2005-07-13  Imported Django from private SVN repository (created from r. 8825)

diff --git a/django/conf/global_settings.py b/django/conf/global_settings.py
--- /dev/null
+++ b/django/conf/global_settings.py
@@ -0,0 +10,1 @@
+DEBUG = False

````

</details>

## L041  django  `django/contrib/admin/options.py:622`

```
     618         opts = self.opts
     619         codename = get_permission_codename("add", opts)
     620         return request.user.has_perm("%s.%s" % (opts.app_label, codename))
     621 
>>   622     def has_change_permission(self, request, obj=None):
     623         """
     624         Return True if the given request has permission to change the given
     625         Django model instance, the default implementation doesn't examine the
     626         `obj` parameter.
```

**Candidate commits, oldest first:**

- `a19ed8aea3`  2008-07-18  Merged the newforms-admin branch into trunk.
- `b1b1da1eac`  2011-10-07  Fixed #8060 - Added permissions-checking for admin inlines. Thanks p.patruno for report an

<details><summary>Line history</summary>

````diff
### b1b1da1eac  2011-10-07  Fixed #8060 - Added permissions-checking for admin inlines. Thanks p.patruno for report and Stephan Jaensch for work on the patch.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -273,0 +281,1 @@
+    def has_change_permission(self, request, obj=None):

````

</details>

## L042  django  `django/db/models/fields/related.py:831`

```
     827         return self.get_instance_value_for_fields(instance, self.foreign_related_fields)
     828 
     829     @staticmethod
     830     def get_instance_value_for_fields(instance, fields):
>>   831         ret = []
     832         opts = instance._meta
     833         for field in fields:
     834             # Gotcha: in some cases (like fixture loading) a model can have
     835             # different values in parent_ptr_id and parent's id. So, use
```

**Candidate commits, oldest first:**

- `f5552571dc`  2013-08-21  Fixed #20820 -- Model inheritance + m2m fixture loading regression

<details><summary>Line history</summary>

````diff
### 1ed77e7782  2013-08-20  Fixed #20820 -- Model inheritance + m2m fixture loading regression

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -992,1 +992,1 @@
-        return tuple([getattr(instance, field.attname) for field in fields])
+        ret = []
### 97774429ae  2013-03-24  Fixed #19385 again, now with real code changes

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -992,1 +982,1 @@
-class ForeignKey(RelatedField, Field):
+        return tuple([getattr(instance, field.attname) for field in fields])
### f69cf70ed8  2006-05-02  MERGED MAGIC-REMOVAL BRANCH TO TRUNK. This change is highly backwards-incompatible. Please read http://code.djangoproject.com/wiki/RemovingTheMagic for upgrade instructions.

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- /dev/null
+++ b/django/db/models/fields/related.py
@@ -0,0 +418,1 @@
+class ForeignKey(RelatedField, Field):

````

</details>

## L043  redis  `src/connection.h:58`

```
      54     int (*configure)(void *priv, int reconfigure);
      55 
      56     /* ae & accept & listen & error & address handler */
      57     void (*ae_handler)(struct aeEventLoop *el, int fd, void *clientData, int mask);
>>    58     aeFileProc *accept_handler;
      59     int (*addr)(connection *conn, char *ip, size_t ip_len, int *port, int remote);
      60     int (*is_local)(connection *conn);
      61     int (*listen)(connListener *listener);
      62 
```

**Candidate commits, oldest first:**

- `0ae02ce95b`  2022-08-22  Abstract accept handler

<details><summary>Line history</summary>

````diff
### 0ae02ce95  2022-07-27  Abstract accept handler

diff --git a/src/connection.h b/src/connection.h
--- a/src/connection.h
+++ b/src/connection.h
@@ -74,0 +77,1 @@
+    aeFileProc *accept_handler;

````

</details>

## L044  django  `django/http/response.py:190`

```
     186         """HTTP headers as a bytestring."""
     187         return b"\r\n".join(
     188             [
     189                 key.encode("ascii") + b": " + value.encode("latin-1")
>>   190                 for key, value in self.headers.items()
     191             ]
     192         )
     193 
     194     __bytes__ = serialize_headers
```

**Candidate commits, oldest first:**

- `ed114e1510`  2005-07-13  Imported Django from private SVN repository (created from r. 8825)
- `dd799591fc`  2007-09-14  Backwards-incompatible change: renamed HttpResponse.headers to HttpResponse._headers to de
- `706659d2bb`  2007-10-20  Changed the way we handle HTTP headers internally so that they appear case-insensitive, bu
- `e04230e2e4`  2012-08-14  [py3] Ported django.http according to PEP 3333.
- `bcc2befd0e`  2020-09-14  Fixed #31789 -- Added a new headers interface to HttpResponse.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/http/response.py b/django/http/response.py
--- a/django/http/response.py
+++ b/django/http/response.py
@@ -152,4 +160,1 @@
-        return b'\r\n'.join([
-            key.encode('ascii') + b': ' + value.encode('latin-1')
-            for key, value in self.headers.items()
-        ])
+                for key, value in self.headers.items()
### f03ba0ad52  2021-08-02  Simplified serializing HTTP response headers.

diff --git a/django/http/response.py b/django/http/response.py
--- a/django/http/response.py
+++ b/django/http/response.py
@@ -156,8 +156,4 @@
-        def to_bytes(val, encoding):
-            return val if isinstance(val, bytes) else val.encode(encoding)
-
-        headers = [
-            (to_bytes(key, 'ascii') + b': ' + to_bytes(value, 'latin-1'))
+        return b'\r\n'.join([
+            key.encode('ascii') + b': ' + value.encode('latin-1')
             for key, value in self.headers.items()
-        ]
-        return b'\r\n'.join(headers)
+        ])
### bcc2befd0e  2020-07-14  Fixed #31789 -- Added a new headers interface to HttpResponse.

diff --git a/django/http/response.py b/django/http/response.py
--- a/django/http/response.py
+++ b/django/http/response.py
@@ -93,8 +151,8 @@
         def to_bytes(val, encoding):
             return val if isinstance(val, bytes) else val.encode(encoding)
 
         headers = [
             (to_bytes(key, 'ascii') + b': ' + to_bytes(value, 'latin-1'))
-            for key, value in self._headers.values()
+            for key, value in self.headers.items()
         ]
         return b'\r\n'.join(headers)
### 7afb476469  2017-05-20  Fixed #28226 -- Replaced use of str.join() with concatenation.

diff --git a/django/http/response.py b/django/http/response.py
--- a/django/http/response.py
+++ b/django/http/response.py
@@ -91,8 +91,8 @@
         def to_bytes(val, encoding):
             return val if isinstance(val, bytes) else val.encode(encoding)
 
         headers = [
-            (b': '.join([to_bytes(key, 'ascii'), to_bytes(value, 'latin-1')]))
+            (to_bytes(key, 'ascii') + b': ' + to_bytes(value, 'latin-1'))
             for key, value in self._headers.values()
         ]
         return b'\r\n'.join(headers)
### a14f087233  2013-10-17  Fixed #21282 -- Made HttpResponse.serialize_headers accept latin-1

diff --git a/django/http/response.py b/django/http/response.py
--- a/django/http/response.py
+++ b/django/http/response.py
@@ -126,5 +126,8 @@
+        def to_bytes(val, encoding):
+            return val if isinstance(val, bytes) else val.encode(encoding)
+
         headers = [
-            ('%s: %s' % (key, value)).encode('us-ascii')
+            (b': '.join([to_bytes(key, 'ascii'), to_bytes(value, 'latin-1')]))
             for key, value in self._headers.values()
         ]
         return b'\r\n'.join(headers)
### b4066d7d21  2012-10-21  Cleaned up the the http module. Moved all of the code from __init__.py to request.py, response.py and utils.py

diff --git a/django/http/response.py b/django/http/response.py
--- /dev/null
+++ b/django/http/response.py
@@ -0,0 +57,5 @@
+        headers = [
+            ('%s: %s' % (key, value)).encode('us-ascii')
+            for key, value in self._headers.values()
+        ]
+        return b'\r\n'.join(headers)

````

</details>

## L045  redis  `src/hyperloglog.c:726`

```
     722     sparse = p = ((uint8_t*)o->ptr) + HLL_HDR_SIZE;
     723     end = p + sdslen(o->ptr) - HLL_HDR_SIZE;
     724 
     725     first = 0;
>>   726     prev = NULL; /* Points to previous opcode at the end of the loop. */
     727     next = NULL; /* Points to the next opcode at the end of the loop. */
     728     span = 0;
     729     while(p < end) {
     730         long oplen;
```

**Candidate commits, oldest first:**

- `c756936b1d`  2014-04-11  HyperLogLog sparse representation initial implementation.
- `93238575f7`  2018-07-03  Fix typo

<details><summary>Line history</summary>

````diff
### 93238575f  2018-07-01  Fix typo

diff --git a/src/hyperloglog.c b/src/hyperloglog.c
--- a/src/hyperloglog.c
+++ b/src/hyperloglog.c
@@ -676,1 +676,1 @@
-    prev = NULL; /* Points to previos opcode at the end of the loop. */
+    prev = NULL; /* Points to previous opcode at the end of the loop. */
### c756936b1  2014-04-11  HyperLogLog sparse representation initial implementation.

diff --git a/src/hyperloglog.c b/src/hyperloglog.c
--- a/src/hyperloglog.c
+++ b/src/hyperloglog.c
@@ -541,0 +603,1 @@
+    prev = NULL; /* Points to previos opcode at the end of the loop. */

````

</details>

## L046  redis  `src/quicklist.c:2170`

```
    2166     size_t option_count = sizeof(options) / sizeof(*options);
    2167     int fill_count = (int)(sizeof(fills) / sizeof(*fills));
    2168     long long runtime[option_count];
    2169 
>>  2170     for (int _i = 0; _i < (int)option_count; _i++) {
    2171         printf("Testing Compression option %d\n", options[_i]);
    2172         long long start = mstime();
    2173         quicklistIter iter;
    2174 
```

**Candidate commits, oldest first:**

- `abdd1414a8`  2015-01-02  Allow compression of interior quicklist nodes

<details><summary>Line history</summary>

````diff
### abdd1414a  2014-12-10  Allow compression of interior quicklist nodes

diff --git a/src/quicklist.c b/src/quicklist.c
--- a/src/quicklist.c
+++ b/src/quicklist.c
@@ -1284,5 +1605,1 @@
-    TEST("create list") {
-        quicklist *ql = quicklistCreate();
-        ql_verify(ql, 0, 0, 0, 0);
-        quicklistRelease(ql);
-    }
+    for (int _i = 0; _i < (int)option_count; _i++) {
### 5e362b84a  2014-11-13  Add quicklist implementation

diff --git a/src/quicklist.c b/src/quicklist.c
--- /dev/null
+++ b/src/quicklist.c
@@ -0,0 +1246,5 @@
+    TEST("create list") {
+        quicklist *ql = quicklistCreate();
+        ql_verify(ql, 0, 0, 0, 0);
+        quicklistRelease(ql);
+    }

````

</details>

## L047  redis  `src/db.c:3264`

```
    3260  *         If not found, set to the bucket where the key should be added.
    3261  *         If set to NULL, then HT of dict not allocated yet.
    3262  */
    3263 kvobj *dbFindByLink(redisDb *db, sds key, dictEntryLink *plink) {
>>  3264     int slot = getKeySlot(key);
    3265     dictEntryLink link, bucket;
    3266 
    3267     link = kvstoreDictFindLink(db->keys, slot, key, &bucket);
    3268     if (link == NULL) {
```

**Candidate commits, oldest first:**

- `0270abda82`  2023-10-15  Replace cluster metadata with slot specific dictionaries (#11695)
- `e1789e4368`  2025-05-12  keyspace - Unify key and value & use dict no_value=1 (#13806)

<details><summary>Line history</summary>

````diff
### e1789e436  2025-05-12  keyspace - Unify key and value & use dict no_value=1 (#13806)

diff --git a/src/db.c b/src/db.c
--- a/src/db.c
+++ b/src/db.c
@@ -2401,3 +2502,1 @@
-static inline dictEntry *dbFindWithKeySlot(redisDb *db, void *key, int keySlot) {
-    return dbFindGenericWithKeySlot(db->keys, key, keySlot);
-}
+    int slot = getKeySlot(key);
### 985bf68f3  2025-02-25  Reduce redundant key slot calculations on expiration checks (#13796)

diff --git a/src/db.c b/src/db.c
--- a/src/db.c
+++ b/src/db.c
@@ -2315,0 +2342,3 @@
+static inline dictEntry *dbFindWithKeySlot(redisDb *db, void *key, int keySlot) {
+    return dbFindGenericWithKeySlot(db->keys, key, keySlot);
+}

````

</details>

## L048  django  `django/db/models/fields/tuple_lookups.py:188`

```
     184         # WHERE a IS NOT NULL AND b IS NOT NULL AND c IS NOT NULL
     185         rhs = self.rhs
     186         lookups = [IsNull(col, rhs) for col in self.lhs]
     187         root = WhereNode(lookups, connector=OR if rhs else AND)
>>   188         return root.as_sql(compiler, connection)
     189 
     190 
     191 class TupleGreaterThan(TupleLookupMixin, GreaterThan):
     192     def get_fallback_sql(self, compiler, connection):
```

**Candidate commits, oldest first:**

- `1eac690d25`  2024-08-01  Refs #373 -- Added tuple lookups.

<details><summary>Line history</summary>

````diff
### 1eac690d25  2024-07-23  Refs #373 -- Added tuple lookups.

diff --git a/django/db/models/fields/tuple_lookups.py b/django/db/models/fields/tuple_lookups.py
--- /dev/null
+++ b/django/db/models/fields/tuple_lookups.py
@@ -0,0 +94,1 @@
+        return root.as_sql(compiler, connection)

````

</details>

## L049  django  `django/contrib/admin/options.py:350`

```
     346 
     347         if "queryset" not in kwargs:
     348             queryset = self.get_field_queryset(db, db_field, request)
     349             if queryset is not None:
>>   350                 kwargs["queryset"] = queryset
     351 
     352         return db_field.formfield(**kwargs)
     353 
     354     def formfield_for_manytomany(self, db_field, request, **kwargs):
```

**Candidate commits, oldest first:**

- `d9330d5be2`  2013-03-04  Fixed #6585 -- Admin relationship widgets: Respect ordering defined by target model's Mode
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -239,1 +277,1 @@
-                kwargs['queryset'] = queryset
+                kwargs["queryset"] = queryset
### 1718b5256c  2013-11-21  Fixed #21405 -- Prevented queryset overwrite in BaseModelAdmin

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -218,3 +221,1 @@
-        queryset = self.get_field_queryset(db, db_field, request)
-        if queryset is not None:
-            kwargs['queryset'] = queryset
+                kwargs['queryset'] = queryset
### d9330d5be2  2013-02-23  Fixed #6585 -- Admin relationship widgets: Respect ordering defined by target model's ModelAdmin.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -174,0 +187,3 @@
+        queryset = self.get_field_queryset(db, db_field, request)
+        if queryset is not None:
+            kwargs['queryset'] = queryset

````

</details>

## L050  django  `django/db/models/fields/related.py:1778`

```
    1774             else:
    1775                 assert from_model is not None, (
    1776                     "ManyToManyField with intermediate "
    1777                     "tables cannot be checked if you don't pass the model "
>>  1778                     "where the field is attached to."
    1779                 )
    1780 
    1781                 source, through, target = (
    1782                     from_model,
```

**Candidate commits, oldest first:**

- `d818e0c9b2`  2014-01-20  Fixed #16905 -- Added extensible checks (nee validation) framework
- `aaad3e27ac`  2014-03-11  Fixed #22217 - ManyToManyField.through_fields fixes.

<details><summary>Line history</summary>

````diff
### aaad3e27ac  2014-03-07  Fixed #22217 - ManyToManyField.through_fields fixes.

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -2021,0 +2034,1 @@
+                    "where the field is attached to."

````

</details>

## L051  django  `django/db/models/fields/related.py:2111`

```
    2107         # specify *what* on my non-reversible relation?!"), so we set it up
    2108         # automatically. The funky name reduces the chance of an accidental
    2109         # clash.
    2110         if self.remote_field.symmetrical and (
>>  2111             self.remote_field.model == RECURSIVE_RELATIONSHIP_CONSTANT
    2112             or self.remote_field.model == cls._meta.object_name
    2113         ):
    2114             self.remote_field.related_name = "%s_rel_+" % name
    2115         elif self.remote_field.hidden:
```

**Candidate commits, oldest first:**

- `1e0dcd6c8b`  2020-01-16  Used constant instead of hard-coded value for recursive relationship.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -1667,2 +1859,1 @@
-            self.remote_field.model == RECURSIVE_RELATIONSHIP_CONSTANT or
-            self.remote_field.model == cls._meta.object_name
+            self.remote_field.model == RECURSIVE_RELATIONSHIP_CONSTANT
### 1e0dcd6c8b  2020-01-16  Used constant instead of hard-coded value for recursive relationship.

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -1564,1 +1578,2 @@
-                self.remote_field.model == "self" or self.remote_field.model == cls._meta.object_name):
+            self.remote_field.model == RECURSIVE_RELATIONSHIP_CONSTANT or
+            self.remote_field.model == cls._meta.object_name
### 8f30556329  2015-02-26  Renamed Field.rel attribute to remote_field

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -2620,2 +2651,1 @@
-        if self.rel.symmetrical and (self.rel.to == "self" or self.rel.to == cls._meta.object_name):
-            self.rel.related_name = "%s_rel_+" % name
+                self.remote_field.model == "self" or self.remote_field.model == cls._meta.object_name):
### 585b7acaa3  2009-11-03  Fixed #10109 -- Removed the use of raw SQL in many-to-many fields by introducing an autogenerated through model.

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -922,2 +945,2 @@
-        if self.rel.symmetrical and self.rel.to == "self" and self.rel.related_name is None:
+        if self.rel.symmetrical and (self.rel.to == "self" or self.rel.to == cls._meta.object_name):
             self.rel.related_name = "%s_rel_+" % name
### 38362a1276  2008-08-29  Fixed a missing piece of [8721].

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -853,2 +853,2 @@
-        if self.rel.symmetrical and self.rel.related_name is None:
+        if self.rel.symmetrical and self.rel.to == "self" and self.rel.related_name is None:
             self.rel.related_name = "%s_rel_+" % name
### f04123f4df  2008-08-29  Fixed #8279 -- Multiple many-to-many relations to "self" are now possible.

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -847,0 +853,2 @@
+        if self.rel.symmetrical and self.rel.related_name is None:
+            self.rel.related_name = "%s_rel_+" % name

````

</details>

## L052  redis  `src/lolwut5.c:72`

```
      68                 float r2 = (float)rand() / (float) RAND_MAX / squares_per_col * y;
      69                 float r3 = (float)rand() / (float) RAND_MAX / squares_per_col * y;
      70                 if (rand() % 2) r1 = -r1;
      71                 if (rand() % 2) r2 = -r2;
>>    72                 if (rand() % 2) r3 = -r3;
      73                 angle = r1;
      74                 sx += r2*square_side/3;
      75                 sy += r3*square_side/3;
      76             }
```

**Candidate commits, oldest first:**

- `eac2a79cf5`  2018-09-12  LOLWUT: draw Schotter by Georg Nees.
- `c560ade831`  2018-09-14  LOLWUT: split the command from version-specific implementations.

<details><summary>Line history</summary>

````diff
### c560ade83  2018-09-14  LOLWUT: split the command from version-specific implementations.

diff --git a/src/lolwut5.c b/src/lolwut5.c
--- /dev/null
+++ b/src/lolwut5.c
@@ -0,0 +198,1 @@
+                if (rand() % 2) r3 = -r3;

````

</details>

## L053  redis  `src/redis-cli.c:6523`

```
    6519             list *slot_nodes = listCreate();
    6520             sds slot_nodes_str = sdsempty();
    6521             listIter li;
    6522             listNode *ln;
>>  6523             listRewind(cluster_manager.nodes, &li);
    6524             while ((ln = listNext(&li)) != NULL) {
    6525                 clusterManagerNode *n = ln->value;
    6526                 if (n->flags & CLUSTER_MANAGER_FLAG_SLAVE || n->replicate)
    6527                     continue;
```

**Candidate commits, oldest first:**

- `486c7af7b8`  2018-04-23  Cluster Manager: 'create', 'info' and 'check' commands
- `3f8a4adb49`  2018-04-23  Cluster Manager: fix command.

<details><summary>Line history</summary>

````diff
### 3f8a4adb4  2018-04-06  Cluster Manager: fix command.

diff --git a/src/redis-cli.c b/src/redis-cli.c
--- a/src/redis-cli.c
+++ b/src/redis-cli.c
@@ -3117,1 +3289,1 @@
-static void clusterManagerCheckCluster(int quiet) {
+            listRewind(cluster_manager.nodes, &li);
### 486c7af7b  2018-01-31  Cluster Manager: 'create', 'info' and 'check' commands

diff --git a/src/redis-cli.c b/src/redis-cli.c
--- a/src/redis-cli.c
+++ b/src/redis-cli.c
@@ -1653,0 +2525,1 @@
+static void clusterManagerCheckCluster(int quiet) {

````

</details>

## L054  django  `django/contrib/gis/utils/layermapping.py:324`

```
     320             # Otherwise just pulling the SpatialReference from the layer
     321             sr = self.layer.srs
     322 
     323         if not sr:
>>   324             raise LayerMapError("No source reference system defined.")
     325         else:
     326             return sr
     327 
     328     def check_unique(self, unique):
```

**Candidate commits, oldest first:**

- `79e68c225b`  2008-08-05  Merged the gis branch into trunk.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/contrib/gis/utils/layermapping.py b/django/contrib/gis/utils/layermapping.py
--- a/django/contrib/gis/utils/layermapping.py
+++ b/django/contrib/gis/utils/layermapping.py
@@ -282,1 +321,1 @@
-            raise LayerMapError('No source reference system defined.')
+            raise LayerMapError("No source reference system defined.")
### 79e68c225b  2008-08-05  Merged the gis branch into trunk.

diff --git a/django/contrib/gis/utils/layermapping.py b/django/contrib/gis/utils/layermapping.py
--- /dev/null
+++ b/django/contrib/gis/utils/layermapping.py
@@ -0,0 +340,1 @@
+            raise LayerMapError('No source reference system defined.')

````

</details>

## L055  django  `django/contrib/admin/templatetags/admin_urls.py:18`

```
      14 
      15 
      16 @register.filter
      17 def admin_urlquote(value):
>>    18     return quote(value)
      19 
      20 
      21 @register.simple_tag(takes_context=True)
      22 def add_preserved_filters(context, url, popup=False, to_field=None):
```

**Candidate commits, oldest first:**

- `a222d6e800`  2012-07-03  Fixed incorrect URL to object on delete confirmation and history page

<details><summary>Line history</summary>

````diff
### a222d6e800  2012-07-03  Fixed incorrect URL to object on delete confirmation and history page

diff --git a/django/contrib/admin/templatetags/admin_urls.py b/django/contrib/admin/templatetags/admin_urls.py
--- a/django/contrib/admin/templatetags/admin_urls.py
+++ b/django/contrib/admin/templatetags/admin_urls.py
@@ -9,0 +14,1 @@
+    return quote(value)

````

</details>

## L056  django  `django/contrib/admin/options.py:2310`

```
    2306                     self.save_related(request, form, formsets=[], change=True)
    2307                     change_msg = self.construct_change_message(request, form, None)
    2308                     self.log_change(request, obj, change_msg)
    2309                     changecount += 1
>>  2310         if changecount:
    2311             msg = ngettext(
    2312                 "%(count)s %(name)s was changed successfully.",
    2313                 "%(count)s %(name)s were changed successfully.",
    2314                 changecount,
```

**Candidate commits, oldest first:**

- `7bc0878922`  2009-03-17  Fixed #8939: added a `list_editable` option to `ModelAdmin`; fields declared `list_editabl
- `512e348bb2`  2026-04-22  Refs #15759 -- Factored out _save_formset() in ModelAdmin.

<details><summary>Line history</summary>

````diff
### 512e348bb2  2026-04-10  Refs #15759 -- Factored out _save_formset() in ModelAdmin.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -2025,0 +2038,1 @@
+        if changecount:

````

</details>

## L057  django  `django/contrib/gis/utils/layermapping.py:385`

```
     381         and return the uniqueness keyword arguments -- a subset of the feature
     382         kwargs.
     383         """
     384         if isinstance(self.unique, str):
>>   385             return {self.unique: kwargs[self.unique]}
     386         else:
     387             return {fld: kwargs[fld] for fld in self.unique}
     388 
     389     # Verification routines used in constructing model keyword arguments.
```

**Candidate commits, oldest first:**

- `79e68c225b`  2008-08-05  Merged the gis branch into trunk.
- `b35ff0d920`  2013-10-27  Fixed all the E203 violations

<details><summary>Line history</summary>

````diff
### b35ff0d920  2013-10-26  Fixed all the E203 violations

diff --git a/django/contrib/gis/utils/layermapping.py b/django/contrib/gis/utils/layermapping.py
--- a/django/contrib/gis/utils/layermapping.py
+++ b/django/contrib/gis/utils/layermapping.py
@@ -325,1 +325,1 @@
-            return {self.unique : kwargs[self.unique]}
+            return {self.unique: kwargs[self.unique]}
### 79e68c225b  2008-08-05  Merged the gis branch into trunk.

diff --git a/django/contrib/gis/utils/layermapping.py b/django/contrib/gis/utils/layermapping.py
--- /dev/null
+++ b/django/contrib/gis/utils/layermapping.py
@@ -0,0 +394,1 @@
+            return {self.unique : kwargs[self.unique]}

````

</details>

## L058  redis  `src/acl.c:2920`

```
    2916     dictEntry *de;
    2917     dictIterator di;
    2918     dictInitIterator(&di, commands);
    2919     while ((de = dictNext(&di)) != NULL) {
>>  2920         struct redisCommand *cmd = dictGetVal(de);
    2921         if (cmd->acl_categories & cflag) {
    2922             addReplyBulkCBuffer(c, cmd->fullname, sdslen(cmd->fullname));
    2923             (*arraylen)++;
    2924         }
```

**Candidate commits, oldest first:**

- `e8bf9b03ed`  2019-01-24  ACL: ACLSetUserCommandBitsForCategory() low level API.
- `23325c135f`  2022-01-23  sub-command support for ACL CAT and COMMAND LIST. redisCommand always stores fullname (#10

<details><summary>Line history</summary>

````diff
### 23325c135  2022-01-23  sub-command support for ACL CAT and COMMAND LIST. redisCommand always stores fullname (#10127)

diff --git a/src/acl.c b/src/acl.c
--- a/src/acl.c
+++ b/src/acl.c
@@ -2438,0 +2443,1 @@
+        struct redisCommand *cmd = dictGetVal(de);

````

</details>

## L059  django  `django/db/models/query.py:1575`

```
    1571         qs._prefetch_related_lookups = self._prefetch_related_lookups[:]
    1572         return qs
    1573 
    1574     def _values(self, *fields, **expressions):
>>  1575         clone = self._chain()
    1576         if expressions:
    1577             # RemovedInDjango2028Warning: When the deprecation ends, deindent:
    1578             # clone = clone.annotate(**expressions)
    1579             with warnings.catch_warnings(
```

**Candidate commits, oldest first:**

- `4c3bfe9053`  2015-01-30  Fixed #24211 -- Removed ValuesQuerySet() and ValuesListQuerySet().
- `66933a6619`  2017-07-31  Refs #20880 -- Removed non-cloning logic from QuerySet._clone().

<details><summary>Line history</summary>

````diff
### 66933a6619  2013-08-08  Refs #20880 -- Removed non-cloning logic from QuerySet._clone().

diff --git a/django/db/models/query.py b/django/db/models/query.py
--- a/django/db/models/query.py
+++ b/django/db/models/query.py
@@ -681,1 +681,1 @@
-        clone = self._clone()
+        clone = self._chain()
### 4c3bfe9053  2015-01-30  Fixed #24211 -- Removed ValuesQuerySet() and ValuesListQuerySet().

diff --git a/django/db/models/query.py b/django/db/models/query.py
--- a/django/db/models/query.py
+++ b/django/db/models/query.py
@@ -603,0 +660,1 @@
+        clone = self._clone()

````

</details>

## L060  django  `django/contrib/auth/views.py:336`

```
     332         else:
     333             context.update(
     334                 {
     335                     "form": None,
>>   336                     "title": _("Password reset unsuccessful"),
     337                     "validlink": False,
     338                 }
     339             )
     340         return context
```

**Candidate commits, oldest first:**

- `255fb99284`  2016-07-16  Fixed #17209 -- Added password reset/change class-based views
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/contrib/auth/views.py b/django/contrib/auth/views.py
--- a/django/contrib/auth/views.py
+++ b/django/contrib/auth/views.py
@@ -321,5 +339,1 @@
-            context.update({
-                'form': None,
-                'title': _('Password reset unsuccessful'),
-                'validlink': False,
-            })
+                    "title": _("Password reset unsuccessful"),
### 255fb99284  2013-04-09  Fixed #17209 -- Added password reset/change class-based views

diff --git a/django/contrib/auth/views.py b/django/contrib/auth/views.py
--- a/django/contrib/auth/views.py
+++ b/django/contrib/auth/views.py
@@ -337,0 +441,5 @@
+            context.update({
+                'form': None,
+                'title': _('Password reset unsuccessful'),
+                'validlink': False,
+            })

````

</details>
