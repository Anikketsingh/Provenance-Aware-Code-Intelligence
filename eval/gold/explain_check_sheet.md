# RQ3 check sheet (Claude's independent labels)

For each explained question: is each claim supported by the evidence it cites, and is
the main reason correct (correct / partly / wrong)? The judge model's verdicts are not
shown. Labels go in `eval/gold/explain_claude_labels.json`.

## Q01 django django/contrib/gis/utils/__init__.py:16

`"LayerMapping",`

**Answer:** Commit d8426f64a7 resolved Ticket #36577 by removing an obsolete try-except block around the import of GIS layermapping utilities in django.contrib.gis.utils. Previously, LayerMapping was conditionally appended to __all__ inside a try block, which caused tooling to warn that the member was possibly unbound. Because ImproperlyConfigured is no longer raised at import time, LayerMapping could be listed and imported directly.
**Cites:** E1, E2, E3

1. Commit d8426f64a7 resolved Ticket #36577 by removing an obsolete try-except block around the import of GIS layermapping utilities in django.contrib.gis.utils. (relies on E1, E2, E3)
2. Previously, LayerMapping was conditionally appended to __all__ inside a try block. (relies on E2)
3. This conditional block caused tooling to warn that LayerMapping was possibly unbound. (relies on E2)
4. Because ImproperlyConfigured is no longer raised at import time, LayerMapping could be listed and imported directly. (relies on E1, E2, E3)

> **[E1] commit d8426f64a7**: Fixed #36577 -- Removed obsolete try-except for GIS layermapping imports.
>
> **[E2] ticket Ticket #36577**: I tried [https://docs.astral.sh/ty/ ty] on a client project and it reported this error:  {{{ warning[possibly-unbound-import]: Member `LayerMapError` of module `django.contrib.gis.utils` is possibly unbound   --> ...    | 36 | from django.contrib.contenttypes.models import ContentType 37 | from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Point, Polygon 38 | from django.contrib.gis.utils import LayerMapError    |                                      ^^^^^^^^^^^^^ 39 | from django.contrib.messages import get_messages 40 | from django.contrib.messages.middleware import MessageMiddleware    | info: rule `possibly-unbound-import` is enabled by default }}}  Looking at the `django.contrib.gis.utils` source code, there’s a `try`/`except ImproperlyConfigured` around the import of `LayerMapError` and `LayerMapping`:  {{{#!python try:     # LayerMapping requires D
>
> **[E3] pr PR #19784**: #### Trac ticket number  ticket-36577  #### Branch description  Per the investigation on the ticket, remove this now-unnecessary `try`/`except`.  #### Checklist - [x] This PR targets the `main` branch. <!-- Backports will be evaluated and done by mergers, when necessary. --> - [x] The commit message is written in past tense, mentions the ticket number, and ends with a period. - [x] I have checked the "Has patch" ticket flag in the Trac system. - [x] I have added or updated relevant tests. - [x] I have added or updated relevant docs, including release notes if applicable. - [x] I have attached screenshots in both light and dark modes for any UI changes.
>

## Q02 django django/utils/deconstruct.py:21

`def deconstruct(obj):`

**Answer:** This code was introduced in commit e565e1332d to resolve ticket #21275, which reported a serializer error when generating migrations for contrib.auth (E1). The issue occurred when the migration serializer raised a ValueError because it could not serialize certain objects, such as validators (E2). To fix this, the migration serializer was updated to look for a deconstruct method on any object (E1).
**Cites:** E1, E2

1. This code was introduced in commit e565e1332d to resolve ticket #21275, which reported a serializer error when generating migrations for contrib.auth. (relies on E1)
2. The issue occurred when the migration serializer raised a ValueError because it could not serialize certain objects, such as validators. (relies on E2)
3. To fix this, the migration serializer was updated to look for a deconstruct method on any object. (relies on E1)

> **[E1] commit e565e1332d**: Fixed #21275 -- Fixed a serializer error when generating migrations for contrib.auth.  The migration serializer now looks for a deconstruct method on any object.
>
> **[E2] ticket Ticket #21275**: My assumption is that we shouldn't try to serialize the `validators` attribute.  Traceback: {{{   File "/home/tim/.virtualenvs/foo/local/lib/python2.7/site-packages/django/db/migrations/writer.py", line 185, in serialize     raise ValueError("Cannot serialize: %r" % value) ValueError: Cannot serialize: <django.core.validators.RegexValidator object at 0x1bacc10> }}}
>

## Q03 django django/db/backends/postgresql/schema.py:54

`sql_drop_indentity = (`

**Answer:** This line was introduced in commit 2eea361eff to resolve ticket #30511 [E1]. Ticket #30511 requested support for PostgreSQL's identity column feature (GENERATED AS IDENTITY) as an alternative to serial columns [E2]. The commit fixed the ticket by using identity columns instead of serials on PostgreSQL, adding the necessary SQL handling for identity columns [E1, E2].
**Cites:** E1, E2

1. This line was introduced in commit 2eea361eff to resolve ticket #30511. (relies on E1)
2. Ticket #30511 requested support for PostgreSQL's identity column feature (GENERATED AS IDENTITY) as an alternative to serial columns. (relies on E2)
3. Commit 2eea361eff fixed ticket #30511 by using identity columns instead of serials on PostgreSQL and adding the necessary SQL handling for identity columns. (relies on E1, E2)

> **[E1] commit 2eea361eff**: Fixed #30511 -- Used identity columns instead of serials on PostgreSQL.
>
> **[E2] ticket Ticket #30511**: We are currently working on a Django / Postgresql 11 project. We needed an adjustment for the postgres module because of its compatibility with .NET Framework and dataset generation. In postgres 10/11 there is the new feature identity column called GENERATED AS IDENTITY instead of serial. column_name type GENERATED {ALWAYS | BY DEFAULT} AS IDENTITY [(sequence_option)] We have created a module based on db.backends.postgres that adds 2 new django model fields. I would like implement the new feature into pyodbc module or new module for postgres 10/11 useful for later versions of django.  Adjustments only in base.py (line 70ff): {{{ data_types = {         'IdentityAutoField': 'integer',         'IdentityBigAutoField': 'bigint', }}} and schema.py, def column_sql () (line 178ff): {{{ # Primary key / unique outputs         if field.primary_key:             sql + = "PRIMARY KEY" 
>

## Q04 django django/conf/locale/eo/formats.py:33

`"%Y-%m-%d %H:%M:%S",  # '1887-07-26 18:59:00'`

**Answer:** This line was added as part of introducing a formats.py file for Esperanto to fix ticket #19647 [E1]. The implementation was based on a draft from Translatewiki that defined DATETIME_INPUT_FORMATS using Python strftime syntax, which included '%Y-%m-%d %H:%M:%S' [E2].
**Cites:** E1, E2

1. This line was added as part of introducing a formats.py file for Esperanto to fix ticket #19647. (relies on E1)
2. The implementation was based on a draft Esperanto formats.py from Translatewiki. (relies on E1, E2)
3. The draft defined DATETIME_INPUT_FORMATS using Python strftime syntax and included '%Y-%m-%d %H:%M:%S'. (relies on E2)

> **[E1] commit b4f21d1807**: Fixed #19647 -- Added formats.py for Esperanto.  Thanks to Objectivesea and Guttorm Flatabø (dittaeva)!
>
> **[E2] ticket Ticket #19647**: Here's a draft Esperanto formats.py from [https://translatewiki.net/wiki/Thread:User_talk:Objectivesea/Thank_you_for_your_contributions_to_the_Esperanto_translation_of_Waymarked_Trails!/reply Translatewiki]:  {{{ # -*- encoding: utf-8 -*- # This file is distributed under the same license as the Django package. # from __future__ import unicode_literals  # The *_FORMAT strings use the Django date format syntax, # see http://docs.djangoproject.com/en/dev/ref/templates/builtins/#date DATE_FORMAT = r'j\-\a \d\e F\, Y' TIME_FORMAT = 'H:i' DATETIME_FORMAT = r'j\-\a \d\e F\, Y\, \j\e H:i' YEAR_MONTH_FORMAT = r'F \d\e Y' MONTH_DAY_FORMAT = r'j\-\a \d\e F' SHORT_DATE_FORMAT = 'Y-m-d'         # ISO 8601 SHORT_DATETIME_FORMAT = 'Y-m-d H:i' # ISO 8601 FIRST_DAY_OF_WEEK = 0  # DimanÄo  # The *_INPUT_FORMATS strings use the Python strftime format syntax, # see http://docs.python.or
>

## Q05 django django/db/migrations/operations/__init__.py:25

`"AlterModelTable",`

**Answer:** This code was introduced in commit 36ded01527 to resolve ticket #21302 by fixing unused imports and replacing wildcard imports [E1]. Ticket #21302 noted that `import *` was being used to import objects across namespaces for convenience, including from operations in migrations [E2]. The ticket called for replacing `import *` with explicit imports so flake8 rule F403 could be removed from the ignore list [E2].
**Cites:** E1, E2

1. This code was introduced in commit 36ded01527 to resolve ticket #21302 by fixing unused imports and replacing wildcard imports. (relies on E1)
2. Ticket #21302 noted that `import *` was being used to import objects across namespaces for convenience, including from operations in migrations. (relies on E2)
3. The ticket called for replacing `import *` with explicit imports so flake8 rule F403 could be removed from the ignore list. (relies on E2)

> **[E1] commit 36ded01527**: Fixed #21302 -- Fixed unused imports and import *.
>
> **[E2] ticket Ticket #21302**: The remaining `import *` statements are primarily to put all the objects from one module into another namespace for convenience imports. I'm unsure if we're fine with using `import *` to accomplish this or if we should be explicit. We should either replace `import *` with the appropriate imports, or mark each line as `# NOQA` so we can remove F403 from the flake8 ignore list in setup.cfg: {{{ ./django/forms/__init__.py:6:1: F403 'from django.forms.fields import *' used; unable to detect undefined names ./django/forms/__init__.py:7:1: F403 'from django.forms.forms import *' used; unable to detect undefined names ./django/forms/__init__.py:8:1: F403 'from django.forms.models import *' used; unable to detect undefined names ./django/forms/__init__.py:9:1: F403 'from django.forms.widgets import *' used; unable to detect undefined names ./django/forms/extras/__init__.py:1:1: F403 'from 
>

## Q06 django django/contrib/postgres/apps.py:76

`register_type_handlers(conn)`

**Answer:** Commit b91868507a added this line to fix ticket #28161, where queries on `ArrayField(CITextField())` returned an unparsed string instead of a proper list. Ticket #28161 noted that psycopg2 requires registering an adapter for citext array types to produce the expected return behavior. Calling `register_type_handlers(conn)` allows Django to automatically register the necessary type handlers for the connection.
**Cites:** E1, E2

1. Commit b91868507a added this line to fix ticket #28161, where queries on ArrayField(CITextField()) returned an unparsed string instead of a proper list. (relies on E1, E2)
2. Ticket #28161 noted that psycopg2 requires registering an adapter for citext array types to produce the expected return behavior. (relies on E2)
3. Calling register_type_handlers(conn) allows Django to automatically register the necessary type handlers for the connection. (relies on E1, E2)

> **[E1] commit b91868507a**: Fixed #28161 -- Fixed return type of ArrayField(CITextField()).  Thanks Tim for the review.
>
> **[E2] ticket Ticket #28161**: The following code  {{{ from django.db import models from django.contrib.postgres.fields import ArrayField, CITextField  class Foo(models.Model):     bar = ArrayField(models.TextField)     baz = ArrayField(CITextField()) }}}  has this wrong behaviour:  {{{ x = Foo.objects.get(id=1) x.bar #  => ["Foo", "Bar"] x.baz #  => "{Foo,Bar}" }}}  This is due to https://github.com/psycopg/psycopg2/issues/268 which requires registering a new adapter for citext fields:  Use   {{{ select typarray from pg_type where typname = 'citext'; }}}  to get the oid, then do  {{{ psycopg2.extensions.register_type(     psycopg2.extensions.new_array_type(         (the_returned_oid,), 'citext[]', psycopg2.STRING)) }}}  for the correct behaviour in plain psycopg2.  Django should do that automatically if any of the CI*Fields is used. Alternatively, the ArrayField should convert the
>

## Q07 django django/contrib/auth/urls.py:18

`name="password_change_done",`

**Answer:** This line exists because commit 4c457bca85 added names to URLs in the convenience contrib.auth urls.py file to resolve ticket #16789. The line was later updated when class-based views were introduced for password change and reset in ticket #17209, and again when simplified URL routing syntax was implemented per DEP 0201 in ticket #28593.
**Cites:** E1, E4, E9

1. This line exists because commit 4c457bca85 added names to URLs in the convenience contrib.auth urls.py file to resolve ticket #16789. (relies on E9)
2. The line was later updated when class-based views were introduced for password change and reset in ticket #17209. (relies on E4)
3. The line was updated again when simplified URL routing syntax was implemented per DEP 0201 in ticket #28593. (relies on E1)

> **[E1] commit df41b5a05d**: Fixed #28593 -- Added a simplified URL routing syntax per DEP 0201.  Thanks Aymeric Augustin for shepherding the DEP and patch review. Thanks Marten Kenbeek and Tim Graham for contributing to the code. Thanks Tom Christie, Shai Berger, and Tim Graham for the docs.
>
> **[E4] commit 255fb99284**: Fixed #17209 -- Added password reset/change class-based views  Thanks Tim Graham for the review.
>
> **[E9] commit 4c457bca85**: Fixed #16789 -- Added names to URLs in convenience contrib.auth urls.py.  Thanks wim AT go2people DOT nl for the report, cmheisel for the patch and fcurella for reviewing it.  git-svn-id: http://code.djangoproject.com/svn/django/trunk@16901 bcc190cf-cafb-0310-a4f2-bffc1f526a37
>

## Q08 django django/conf/locale/ta/formats.py:5

`DATE_FORMAT = "j F, Y"`

**Answer:** This line was added in commit 9233d04265 to fix Ticket #7980, which improved Django's i18n framework to support locale-aware formatting for dates and numbers, as well as form processing [E1]. Ticket #7980 specifically proposed customizing date and datetime display formats based on the current locale [E2].
**Cites:** E1, E2

1. This line was added in commit 9233d04265 to fix Ticket #7980. (relies on E1)
2. Commit 9233d04265 improved Django's i18n framework to support locale-aware formatting for dates and numbers, as well as form processing. (relies on E1)
3. Ticket #7980 specifically proposed customizing date and datetime display formats based on the current locale. (relies on E2)

> **[E1] commit 9233d04265**: Fixed #7980 - Improved i18n framework to support locale aware formatting (dates and numbers) and form processing.  Thanks to Marc Garcia for working on this during his Google Summer of Code 2009!  Additionally fixes #1061, #2203, #3940, #5526, #6449, #6231, #6693, #6783, #9366 and #10891.  git-svn-id: http://code.djangoproject.com/svn/django/trunk@11964 bcc190cf-cafb-0310-a4f2-bffc1f526a37
>
> **[E2] ticket Ticket #7980**: As described in http://vaig.be/2008/07/26/django-i18n-status/ Django's i18n has many features missing.  This ticket is a proposal to:  * Customize first day of week in admin's calendar (based on current locale).  * Customize date/datetime formats when a date/datetime is displayed (based on current locale).  * Customize number format when a decimal number is displayed (based on current locale).  * Customize input format for date/datetime widgets (based on current locale). It also includes displaying existing data in the same format, when shown on the widget.  * Customize input format for decimal number widgets (based on current locale). It also includes displaying existing data in the same format, when shown on the widget.  Some other i18n features should be added later, but those are basic for Web site i18n.
>

## Q09 django django/db/models/fields/__init__.py:2325

`def _check_blank_and_null_values(self, **kwargs):`

**Answer:** This method was added in commit d818e0c9b2 as part of an extensible checks (validation) framework [E1]. According to Ticket #16905, this framework was introduced so that fields could participate directly in the model-declaration validation phase instead of relying on a chain of `isinstance` checks in `management.validation.get_validation_errors` [E1, E2].
**Cites:** E1, E2

1. This method was added in commit d818e0c9b2 as part of an extensible checks (validation) framework. (relies on E1)
2. According to Ticket #16905, the framework was introduced so fields could participate directly in the model-declaration validation phase instead of relying on a chain of isinstance checks in management.validation.get_validation_errors. (relies on E1, E2)

> **[E1] commit d818e0c9b2**: Fixed #16905 -- Added extensible checks (nee validation) framework  This is the result of Christopher Medrela's 2013 Summer of Code project.  Thanks also to Preston Holmes, Tim Graham, Anssi Kääriäinen, Florian Apolloner, and Alex Gaynor for review notes along the way.  Also: Fixes #8579, fixes #3055, fixes #19844.
>
> **[E2] ticket Ticket #16905**: Right now, management.validation.get_validation_errors has a long chain of elif isinstance's for built-in fields.  It should be possible for custom fields to participate in this model-declaration validation phase.
>

## Q20 redis src/hyperloglog.c:1470

`_mm_storeu_si128((__m128i *)(t + 12), higher);`

**Answer:** This line was introduced in commit fdeb97629e (PR #13558) to optimize the performance of HyperLogLog commands such as PFCOUNT and PFMERGE using SIMD acceleration. It forms part of the AVX2 fast paths added for conversion between raw and dense HyperLogLog representations, providing significantly faster execution compared to the scalar implementation.
**Cites:** E1, E3

1. This line was introduced in commit fdeb97629e (PR #13558) to optimize the performance of HyperLogLog commands such as PFCOUNT and PFMERGE using SIMD acceleration. (relies on E1, E3)
2. It forms part of the AVX2 fast paths added for conversion between raw and dense HyperLogLog representations. (relies on E1, E3)
3. The AVX2 fast paths provide significantly faster execution compared to the scalar implementation. (relies on E1, E3)

> **[E1] commit fdeb97629e**: Optimize PFCOUNT, PFMERGE command by SIMD acceleration (#13558)  This PR optimizes the performance of HyperLogLog commands (PFCOUNT, PFMERGE) by adding AVX2 fast paths.  Two AVX2 functions are added for conversion between raw representation and dense representation. They are 15 ~ 30 times faster than scalar implementaion. Note that sparse representation is not accelerated.  AVX2 fast paths are enabled when the CPU supports AVX2 (checked at runtime) and the hyperloglog configuration is default (HLL_REGISTERS == 16384 && HLL_BITS == 6).  When merging 3 dense hll structures, the benchmark shows a 12x speedup compared to the scalar version.  ``` pfcount key1 key2 key3 pfmerge keyall key1 key2 ke
>
> **[E3] pr PR #13558**: This PR optimizes the performance of HyperLogLog commands (PFCOUNT, PFMERGE) by adding AVX2 fast paths.  Two AVX2 functions are added for conversion between raw representation and dense representation. They are 15 ~ 30 times faster than scalar implementaion. Note that sparse representation is not accelerated.  AVX2 fast paths are enabled when the CPU supports AVX2 (checked at runtime) and the hyperloglog configuration is default (HLL_REGISTERS == 16384 && HLL_BITS == 6).  When merging 3 dense hll structures, the benchmark shows a 12x speedup compared to the scalar version.  ``` pfcount key1 key2 key3 pfmerge keyall key1 key2 key3 ```  ``` ====================================================================================================== Type             Ops/sec    Avg. Latency     p50 Latency     p99 Latency   p99.9 Latency       KB/sec  -------------------------------
>

## Q22 redis deps/croaring/include/roaring/containers/mixed_intersection.h:42

`const array_container_t *src_1, const bitset_container_t *src_2);`

**Answer:** This line exists as part of vendoring the CRoaring v4.7.2 library into Redis under `deps/croaring` via commit f3b9b68ec6 and PR #15331 [E1, E3]. The library was added to provide a native compressed Roaring bitmap representation to address Issue #15296, cutting memory usage for sparse or large bitmap workloads while preserving bit semantics [E1, E2, E3].
**Cites:** E1, E2, E3

1. This line exists as part of vendoring the CRoaring v4.7.2 library into Redis under deps/croaring via commit f3b9b68ec6 and PR #15331. (relies on E1, E3)
2. The CRoaring library was added to provide a native compressed Roaring bitmap representation to address Issue #15296. (relies on E1, E2, E3)
3. The native Roaring bitmap representation cuts memory usage for sparse or large bitmap workloads while preserving bit semantics. (relies on E1, E2, E3)

> **[E1] commit f3b9b68ec6**: Redis native compressed bitmaps (redis-roaring) (#15331)  Fixes #15296  ## Native Roaring bitmaps  Adds a native **Roaring bitmap** representation for Redis bitmaps, backed by vendored **CRoaring v4.7.2** (`deps/croaring`, built with SIMD disabled and symbols hidden for portability). A string bitmap costs one byte per 8 bit positions up to its highest offset, regardless of how many bits are set; sparse or large bitmaps are instead stored compressed, cutting memory dramatically while preserving exact bit semantics.  ### Type & object model - New object type `OBJ_BITMAP` with encoding `OBJ_ENCODING_BITMAP_ROARING`. `TYPE` → `bitmap`, `OBJECT ENCODING` → `bitmap-roaring`. - Object header: `enco
>
> **[E2] issue Issue #15296**: **The problem/use-case that the feature addresses**  Redis current bitmap representation is very simple: raw string values have their bits set whenever an operation is performed. This preserves simple and powerful semantics, but it can be memory-inefficient for sparse or high-offset bitmap workloads:  - user activity flags - sparse ID membership - analytics  Today, users who need compressed bitmap storage often use external modules such as [redisroaring](https://redisroaring.com). That demonstrates demand for compressed bitmaps, but modules introduce separate types, commands,  and migration complexity.  This proposal is to integrate compressed bitmaps on Redis core.  As for the specific implementation, it's worth noting that [CRoaring](https://github.com/RoaringBitmap/CRoaring) is one of the most performant and well maintained libraries in the world, so it's the best first pick for this 
>
> **[E3] pr PR #15331**: Fixes #15296  ## Native Roaring bitmaps  Adds a native **Roaring bitmap** representation for Redis bitmaps, backed by vendored **CRoaring v4.7.2** (`deps/croaring`, built with SIMD disabled and symbols hidden for portability). A string bitmap costs one byte per 8 bit positions up to its highest offset, regardless of how many bits are set; sparse or large bitmaps are instead stored compressed, cutting memory dramatically while preserving exact bit semantics.  ### Type & object model - New object type `OBJ_BITMAP` with encoding `OBJ_ENCODING_BITMAP_ROARING`. `TYPE` → `bitmap`, `OBJECT ENCODING` → `bitmap-roaring`. - Object header: `encoding` widened 4→5 bits to fit the new encoding value; to keep `redisObject` the same width, `refcount` drops 23→22 bits, lowering the maximum non-shared refcount from 8388605 to 4194301 (still far above any real per-object refcount).  ### Enabling it — `bitm
>

## Q23 redis src/pubsub.c:746

`if (type.shard) {`

**Answer:** This line was added in commit 9f8885760b (PR #8621) to implement sharded pubsub based on shard channels and cluster hashing [E1, E2]. PR #8621 introduced this implementation along with shard-specific commands such as SPUBLISH, SSUBSCRIBE, and SUNSUBSCRIBE, where the prefix 'S' denotes 'SHARD' [E2].
**Cites:** E1, E2

1. This line was added in commit 9f8885760b (PR #8621) to implement sharded pubsub based on shard channels and cluster hashing. (relies on E1, E2)
2. PR #8621 introduced this implementation along with shard-specific commands such as SPUBLISH, SSUBSCRIBE, and SUNSUBSCRIBE, where the prefix 'S' denotes 'SHARD'. (relies on E2)

> **[E1] commit 9f8885760b**: Sharded pubsub implementation (#8621)  This commit implements a sharded pubsub implementation based off of shard channels.  Co-authored-by: Harkrishn Patro <harkrisp@amazon.com> Co-authored-by: Madelyn Olson <madelyneolson@gmail.com>
>
> **[E2] pr PR #8621**: This is a PR to support a sharded pubsub implementation based on cluster hashing.  API Definitions can be found [here](https://github.com/redis/redis/issues/8029#issuecomment-793160824)   New commands introduced: * SPUBLISH * SSUBSCRIBE * SUNSUBSCRIBE  Prefix `S` denotes `SHARD`.  New Sub commands * PUBSUB SHARDCHANNELS * PUBSUB SHARDNUMSUB  New Configs  * cluster-allow-pubsubshard-when-down: Controls whether local pubsub is allowed when the cluster is down (when a majority of slots can't be served or we can't reach a majority of primaries.) Unlike key based commands, which defaults to rejecting commands, pubusub by default allows pubsub messages, since they are best effort.   Considerations made: * Slot Migration and cleanup are handled. Slot migration works by having the migrating node continue to serve the pubsub channels, and at the very end of the migration clien
>

## Q28 react packages/react-dom-bindings/src/events/getEventTarget.js:24

`target = target.correspondingUseElement;`

**Answer:** This line was introduced in commit 2fdaba49c7 to resolve issue #4963, where SVG <use> elements swallowed click events [E1]. In Edge and IE11 or earlier, clicking an SVG icon rendered with a <use> tag would fail to bubble events to onClick handlers on parent elements such as anchors [E2].
**Cites:** E1, E2

1. This line was introduced in commit 2fdaba49c7 to resolve issue #4963, where SVG <use> elements swallowed click events. (relies on E1)
2. In Edge and IE11 or earlier, clicking an SVG icon rendered with a <use> tag would fail to bubble events to onClick handlers on parent elements such as anchors. (relies on E2)

> **[E1] commit 2fdaba49c7**: Fix #4963 - SVG <use> swallows click events
>
> **[E2] issue Issue #4963**: We've only managed to replicate this in Edge and <=IE11, not Chrome or Firefox. We've created a demo of the issue with [this jsbin](http://jsbin.com/jojosesupe).  We're using a common SVG element and linking to it with `xlink:href` as is common with SVG icons. When linking to the icons with a `<use>` tag inside an anchor, all click events on the icon will not bubble to onClick handlers on the anchor.  An example: I have a common SVG element with an icon `<svg><rect id="my-icon" width="100" height="100"></rect></svg>`. I then make a link containing my icon `<a href="https://github.com"><svg dangerouslySetInnerHTML={{__html: '<use xlink:href="#my-icon"></use>'}}></svg></a>`. As `xlink:href` isn't supported by react yet, we have to use `dangerouslySetInnerHTML`. If we now click the SVG **any onClick handlers on the anchor will not run**.  A temporary workaround is setting `pointer-events: n
>

## Q29 react packages/react-dom/npm/static.node.js:13

`exports.resumeAndPrerenderToNodeStream = s.resumeAndPrerenderToNodeStream;`

**Answer:** This line exists to add `resumeAndPrerender` capabilities to static rendering experimental exports alongside `resume`, as introduced in PR #30950. It enables performing a new prerender by resuming an already existing postponed state, useful with Postpone/Halt. This allows the creation of a chain of preludes where subsequent preludes include scripts to patch up the document.
**Cites:** E1, E2

1. This line exists to add resumeAndPrerender capabilities to static rendering experimental exports alongside resume, as introduced in PR #30950. (relies on E1, E2)
2. It enables performing a new prerender by resuming an already existing postponed state, which is useful with Postpone/Halt. (relies on E1, E2)
3. This allows creating a chain of preludes where subsequent preludes include scripts to patch up the document. (relies on E1, E2)

> **[E1] commit 473522093d**: [Fizz] Add resumeAndPrerender to Static Rendering (#30950)  This is only in the same experimental exports as `resume`. Useful with Postpone/Halt.  We already have `prerender()` to create a partial tree with postponed state. We also have `resume()` to dynamically resume such a tree.  This lets you do a new prerender by resuming an already existing postponed state. Basically creating a chain of preludes. The next prelude would include the scripts to patch up the document.  This mostly just works since both prerender and resume are already implemented using the same code so we just enable both at the root. I'm sure we'll find some edge cases since this wasn't considered when it was first writte
>
> **[E2] pr PR #30950**: This is only in the same experimental exports as `resume`. Useful with Postpone/Halt.  We already have `prerender()` to create a partial tree with postponed state. We also have `resume()` to dynamically resume such a tree.  This lets you do a new prerender by resuming an already existing postponed state. Basically creating a chain of preludes. The next prelude would include the scripts to patch up the document.  This mostly just works since both prerender and resume are already implemented using the same code so we just enable both at the root. I'm sure we'll find some edge cases since this wasn't considered when it was first written but so far I've only found an unrelated existing bug with `keyPath` fixed here.
>

## Q32 react packages/react-reconciler/src/ReactFiberPerformanceTrack.js:1483

`performance.clearMeasures('Errored');`

**Answer:** According to PR #34803 and commit b9ec735de2, performance measures must be cleared because recording copies of props can otherwise allocate too much memory in Chromium. This line adds a `performance.clearMeasures(...)` call in DEV mode to clean up these potentially large measures while still ensuring timeline entries appear in the Performance panel.
**Cites:** E1, E2

1. According to PR #34803 and commit b9ec735de2, performance measures must be cleared because recording copies of props can otherwise allocate too much memory in Chromium. (relies on E1, E2)
2. This line adds a `performance.clearMeasures(...)` call in DEV mode to clean up potentially large measures. (relies on E1, E2)
3. This cleanup is done while still ensuring timeline entries appear in the Performance panel. (relies on E1, E2)

> **[E1] commit b9ec735de2**: [Perf Tracks]: Clear potentially large measures (#34803)  Fixes https://github.com/facebook/react/issues/34770.  We need to clear measures at some point, otherwise all these copies of props that we end up recording will allocate too much memory in Chromium. This adds `performance.clearMeasures(...)` calls to such cases in DEV.  Validated that entries are still shown on Performance panel timeline.
>
> **[E2] pr PR #34803**: Fixes https://github.com/facebook/react/issues/34770.  We need to clear measures at some point, otherwise all these copies of props that we end up recording will allocate too much memory in Chromium.  This adds `performance.clearMeasures(...)` calls to such cases in DEV.  Validated that entries are still shown on Performance panel timeline.
>

## Q33 react packages/react-server-dom-parcel/server.node.js:16

`decodeAction,`

**Answer:** This code was added in PR #31725 to implement the `react-server-dom-parcel` package, which provides a React Server Components (RSC) integration for the Parcel bundler (E1, E2). The package was mostly copied from existing webpack and turbopack integrations, with modifications to use Parcel runtime APIs for loading and executing modules (E1, E2). In this setup, Parcel automatically injects references and registers server action IDs using `react-server-dom-parcel` (E2).
**Cites:** E1, E2

1. This code was added in PR #31725 to implement the react-server-dom-parcel package, which provides a React Server Components (RSC) integration for the Parcel bundler. (relies on E1, E2)
2. The package was mostly copied from existing webpack and turbopack integrations, with modifications to use Parcel runtime APIs for loading and executing modules. (relies on E1, E2)
3. In this setup, Parcel automatically injects references and registers server action IDs using react-server-dom-parcel. (relies on E2)

> **[E1] commit ca587425fe**: Implement react-server-dom-parcel (#31725)  This adds a new `react-server-dom-parcel-package`, which is an RSC integration for the Parcel bundler. It is mostly copied from the existing webpack/turbopack integrations, with some changes to utilize Parcel runtime APIs for loading and executing bundles/modules.  See https://github.com/parcel-bundler/parcel/pull/10043 for the Parcel side of this, which includes the plugin needed to generate client and server references. https://github.com/parcel-bundler/rsc-examples also includes examples of various ways to use RSCs with Parcel.  Differences from other integrations:  * Client and server modules are all part of the same graph, and we use Parcel's
>
> **[E2] pr PR #31725**: This adds a new `react-server-dom-parcel-package`, which is an RSC integration for the Parcel bundler. It is mostly copied from the existing webpack/turbopack integrations, with some changes to utilize Parcel runtime APIs for loading and executing bundles/modules.  See https://github.com/parcel-bundler/parcel/pull/10043 for the Parcel side of this, which includes the plugin needed to generate client and server references. https://github.com/parcel-bundler/rsc-examples also includes examples of various ways to use RSCs with Parcel.  Differences from other integrations:  * Client and server modules are all part of the same graph, and we use Parcel's [environments](https://parceljs.org/plugin-system/transformer/#the-environment) to distinguish them. The server is the Parcel build entry point, and it imports and renders server components in route handlers. When a `"use client"` directi
>

## Q34 react packages/react-devtools-shared/buildUtils.js:12

`let flagsPath;`

**Answer:** This line was introduced in commit 7e405d458d (PR #18994) to support adding DevTools forked feature flags [E1, E2]. The commit was also created to resolve an uncaught error in extension builds reported in issue #18843 [E1, E3].
**Cites:** E1, E2, E3

1. This line was introduced in commit 7e405d458d (PR #18994) to support adding DevTools forked feature flags. (relies on E1, E2)
2. The commit was also created to resolve an uncaught error in extension builds reported in issue #18843. (relies on E1, E3)

> **[E1] commit 7e405d458d**: [DevTools] Add DevTools forked Feature flags (#18994)  Also resolve an uncaught error in extension build (#18843).  Co-authored-by: Brian Vaughn <brian.david.vaughn@gmail.com> Co-authored-by: Brian Vaughn <bvaughn@fb.com>
>
> **[E2] pr PR #18994**: resolve #18843 another option is just use process.env.TARGET
>
> **[E3] issue Issue #18843**: In Chrome, when I am using the current stable version of react devtools extenison (4.6.0 (3/26/2020)), if I have "Pause on caught exceptions" enabled, I always hit this breakpoint:  https://github.com/facebook/react/blob/c2d1561c60507189b43ae96c6b89580874367e36/packages/react-devtools-shared/src/hook.js#L185  `ReferenceError: i is not defined     at Object.inject (<anonymous>:1:1116)     at injectInternals (react-dom.development.js:9842)     at injectIntoDevTools (react-dom.development.js:20715)     at eval (react-dom.development.js:21244)`  It would be nice if the published extension had an options page so that I could disable this try/catch block. (for example enabling NODE_ENV=test or something).   Or, perhaps that code block is not really relevant to the chrome extension case, and that code path could be ignored for the chrome extension.
>

## Q36 react packages/react-server/src/createFastHashJS.js:57

`let remainder, bytes, h1, h1b, c1, c2, k1, i;`

**Answer:** This code was introduced in commit 68ac6dbcf8 to provide a pure JS implementation of the MurmurHash3 algorithm when native hashing functions are unavailable [E1, E2]. According to PR #27399, it uses Gary Court's MurmurHash3 implementation to synchronously produce compact hashes where speed is prioritized over collision avoidance, such as hashing component key paths for useFormState [E2]. These variables are declared as part of that fallback hashing algorithm for environments lacking synchronous native hashing options like Node's crypto module or Bun.hash [E2].
**Cites:** E1, E2

1. This code was introduced in commit 68ac6dbcf8 to provide a pure JS implementation of the MurmurHash3 algorithm when native hashing functions are unavailable. (relies on E1, E2)
2. According to PR #27399, it uses Gary Court's MurmurHash3 implementation to synchronously produce compact hashes where speed is prioritized over collision avoidance, such as hashing component key paths for useFormState. (relies on E2)
3. These variables are declared as part of that fallback hashing algorithm for environments lacking synchronous native hashing options like Node's crypto module or Bun.hash. (relies on E2)

> **[E1] commit 68ac6dbcf8**: Use MurmurHash3 when native hashing function is not available (#27399)
>
> **[E2] pr PR #27399**: Adds a pure JS implementation of a string hashing function. We do not use it for security or obfuscation purposes, only to create compact hashes. So we prioritize speed over collision avoidance. For example, we use this to hash the component key path used by useFormState for MPA-style submissions. See #27397 for details.  In environments where built-in hashing functions are available, we prefer those instead. Like Node's crypto module, or Bun.hash. Unfortunately this does not include the web standard crypto API because those methods are all async. For our purposes, we need it to be sync because the cost of context switching is too high to be worth it.  The most popular hashing algorithm that meets these requirements in the JS ecosystem is MurmurHash3, and almost all implementations I could find used some version of the implementation by Gary Court. So that's the one I've used.  In 
>

## Q37 react fixtures/dom/src/components/Header.js:92

`<option value="/form-state">Form State</option>`

**Answer:** This line of code exists to provide a DOM test fixture option for manual tests verifying that controlled form component state updates correctly when browser autofill or autocomplete is used [E1, E2]. It was added in PR #17951 in connection with ticket 10468 [E1, E2].
**Cites:** E1, E2

1. This line of code provides a DOM test fixture option for manual tests verifying that controlled form component state updates correctly when browser autofill or autocomplete is used. (relies on E1, E2)
2. It was added in PR #17951 in connection with ticket 10468. (relies on E1, E2)

> **[E1] commit 2078aa9a40**: Add dom fixture for autofilled form state (#17951)
>
> **[E2] pr PR #17951**: ## Summary  <!-- Explain the **motivation** for making this change. What existing problem does the pull request solve? -->  This change is to introduce another test fixture for adding manual tests for checking to make sure form state (for controlled form components) is updated by browser autofill/autocomplete. This is tied to ticket [10468](https://github.com/facebook/react/issues/10468).  ## Test Plan  Streamable Video: https://streamable.com/fhx52
>

