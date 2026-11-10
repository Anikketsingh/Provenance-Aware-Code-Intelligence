# Annotation Packet

Follow `RULES.md`, and record answers in `annotations.csv`.

## T001  django  `django/conf/global_settings.py:504`

```
     500 # Whether to use the HttpOnly flag.
     501 SESSION_COOKIE_HTTPONLY = True
     502 # Whether to set the flag restricting cookie leaks on cross-site requests.
     503 # This can be 'Lax', 'Strict', 'None', or False to disable the flag.
>>   504 SESSION_COOKIE_SAMESITE = "Lax"
     505 # Whether to save the session data on every request.
     506 SESSION_SAVE_EVERY_REQUEST = False
     507 # Whether a user's session cookie expires when the web browser is closed.
     508 SESSION_EXPIRE_AT_BROWSER_CLOSE = False
```

**Candidate commits, oldest first:**

- `9a56b4b13e`  2018-04-14  Fixed #27863 -- Added support for the SameSite cookie flag.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/conf/global_settings.py b/django/conf/global_settings.py
--- a/django/conf/global_settings.py
+++ b/django/conf/global_settings.py
@@ -487,1 +487,1 @@
-SESSION_COOKIE_SAMESITE = 'Lax'
+SESSION_COOKIE_SAMESITE = "Lax"
### 9a56b4b13e  2018-04-13  Fixed #27863 -- Added support for the SameSite cookie flag.

diff --git a/django/conf/global_settings.py b/django/conf/global_settings.py
--- a/django/conf/global_settings.py
+++ b/django/conf/global_settings.py
@@ -464,0 +466,1 @@
+SESSION_COOKIE_SAMESITE = 'Lax'

````

</details>

## T002  redis  `src/t_zset.c:1627`

```
    1623             serverPanic("Unknown target encoding");
    1624 
    1625         /* Approach similar to zslFree(), since we want to free the skiplist at
    1626          * the same time as creating the listpack. */
>>  1627         unsigned char *zl = lpNew(0);
    1628         zs = zobj->ptr;
    1629         dictRelease(zs->dict);
    1630         node = zs->zsl->header->level[0].forward;
    1631         zfree(zs->zsl->header);
```

**Candidate commits, oldest first:**

- `a669d5e999`  2011-03-09  Convert encoding when thresholds overflow
- `3ca6972ecd`  2021-09-09  Replace all usage of ziplist with listpack for t_zset (#9366)
- `81d653f5dc`  2026-10-23  Reduce large sorted set memory with a packed B+ tree (#15635)

<details><summary>Line history</summary>

````diff
### 81d653f5d  2026-10-23  Reduce large sorted set memory with a packed B+ tree (#15635)

diff --git a/src/t_zset.c b/src/t_zset.c
--- a/src/t_zset.c
+++ b/src/t_zset.c
@@ -1499,0 +1694,1 @@
+        unsigned char *zl = lpNew(0);

````

</details>

## T003  django  `django/conf/global_settings.py:118`

```
     114     ("lv", gettext_noop("Latvian")),
     115     ("mk", gettext_noop("Macedonian")),
     116     ("ml", gettext_noop("Malayalam")),
     117     ("mn", gettext_noop("Mongolian")),
>>   118     ("mr", gettext_noop("Marathi")),
     119     ("ms", gettext_noop("Malay")),
     120     ("my", gettext_noop("Burmese")),
     121     ("nb", gettext_noop("Norwegian Bokmål")),
     122     ("ne", gettext_noop("Nepali")),
```

**Candidate commits, oldest first:**

- `1c660d0de2`  2014-08-23  Added new supported languages
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/conf/global_settings.py b/django/conf/global_settings.py
--- a/django/conf/global_settings.py
+++ b/django/conf/global_settings.py
@@ -57,97 +119,1 @@
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
-    ('sr-latn', gettext_noop('Serbia
... (cut, so use `git log -L` for the rest)
````

</details>

## T004  redis  `src/t_zset.c:1542`

```
    1538             /* A corrupt listpack may contain a duplicate, even one that is
    1539              * still ordered by (score, member) such as (a,1),(a,2), so every
    1540              * member is looked up before it is inserted. dictAdd() used to
    1541              * catch this when the target was always a skiplist. */
>>  1542             while (eptr != NULL) {
    1543                 score = zzlGetScore(sptr);
    1544                 serverAssert(!isnan(score));
    1545                 char buf[LONG_STR_SIZE];
    1546                 size_t rawlen;
```

**Candidate commits, oldest first:**

- `81d653f5dc`  2026-10-23  Reduce large sorted set memory with a packed B+ tree (#15635)
- `5b69ba2ce9`  2026-11-06  Always check for duplicates when converting a listpack zset to a btree (#16164)

<details><summary>Line history</summary>

````diff
### 5b69ba2ce  2026-11-06  Always check for duplicates when converting a listpack zset to a btree (#16164)

diff --git a/src/t_zset.c b/src/t_zset.c
--- a/src/t_zset.c
+++ b/src/t_zset.c
@@ -1582,44 +1542,1 @@
-            if (zzlIsSortedNoDup(zl)) {
-                /* Uncorrupted listpack (the common case, verified above):
-                 * known sorted and duplicate-free, so every insert can use
-                 * the descent-free append path -- no per-element duplicate
-                 * search, and no separate full-tree descent to insert.
-                 * Batched: buf is a per-iteration stack scratch reused every
-                 * loop pass, so raw's bytes are only valid until the next
-                 * zzlDecodeElement() call -- zbtreeAppendBatchAdd() copies
-                 * them out synchronously before returning, same contract the
-                 * unbatched zbtreeInsertNewAppend() call it replaces had. */
-                zbtreeAppendBatch *batch = zbtreeAppendBatchCreate(bt);
-                while (eptr != NULL) {
-                    score = zzlGetScore(sptr);
-                    serverAssert(!isnan(score));
-                    char buf[LONG_STR_SIZE];
-                    size_t rawlen;
-                    const unsigned char *raw = zzlDecodeElement(eptr, buf, sizeof(buf), &rawlen);
-                    zbtreeAppendBatchAdd(batch, score, raw, rawlen);
-                    zzlNext(zl,&eptr,&sptr);
-                }
-                zbtreeAppendBatchFinish(batch);
-            } else {
-                while (eptr != NULL) {
-                    score = zzlGetScore(sptr);
-                    serverAssert(!isnan(score));
-                    vstr = lpGetValue(eptr,&vlen,&vlong);
-                    char buf[LONG_STR_SIZE];
-                    const unsigned char *raw;
-                    size_t rawlen;
-                    if (vstr == NULL) {
-                        rawlen = ll2string(buf,sizeof(buf),vlong);
-                        raw = (unsigned char *)buf;
-                    } else {
-                        raw = vstr;
-                        rawlen = vlen;
-                    }
-                    /* A corrupt listpack may contain a duplicate. dictAdd()
-                     * used to catch this when the target was always a
-                     * skiplist. */
-                    int duplicate = zbtreeScoreRaw(bt,raw,rawlen,NULL);
-                    serverAssert(!duplicate);
-                    zbtreeInsertNewRaw(bt,score,raw,rawlen,NULL);
-                    zzlNext(zl,&eptr,&sptr);
-                }
+            while (eptr != NULL) {
### 81d653f5d  2026-10-23  Reduce large sorted set memory with a packed B+ tree (#15635)

diff --git a/src/t_zset.c b/src/t_zset.c
--- a/src/t_zset.c
+++ b/src/t_zset.c
@@ -1458,0 +1575,44 @@
+            if (zzlIsSortedNoDup(zl)) {
+                /* Uncorrupted listpack (the common case, verified above):
+                 * known sorted and duplicate-free, so every insert can use
+                 * the descent-free append path -- no per-element duplicate
+                 * search, and no separate full-tree descent to insert.
+                 * Batched: buf is a per-iteration stack scratch reused every
+                 * loop pass, so raw's bytes are only valid until the next
+                 * zzlDecodeElement() call -- zbtreeAppendBatchAdd() copies
+                 * them out synchronously before returning, same contract the
+                 
... (cut, so use `git log -L` for the rest)
````

</details>

## T005  django  `django/db/migrations/graph.py:335`

```
     331         for node in plan:
     332             project_state = self.nodes[node].mutate_state(project_state, preserve=False)
     333         return project_state
     334 
>>   335     def __contains__(self, node):
     336         return node in self.nodes
```

**Candidate commits, oldest first:**

- `64887c644a`  2014-01-08  Fixed #21142: Dependency failures on unmigrated apps.

<details><summary>Line history</summary>

````diff
### 64887c644a  2014-01-08  Fixed #21142: Dependency failures on unmigrated apps.

diff --git a/django/db/migrations/graph.py b/django/db/migrations/graph.py
--- a/django/db/migrations/graph.py
+++ b/django/db/migrations/graph.py
@@ -148,0 +148,1 @@
+    def __contains__(self, node):

````

</details>

## T006  django  `django/db/migrations/state.py:356`

```
     352                 remote_field, to_fields = reference.to
     353                 if getattr(remote_field, "field_name", None) == old_name:
     354                     remote_field.field_name = new_name
     355                 if to_fields:
>>   356                     field.to_fields = tuple(
     357                         [
     358                             new_name if to_field_name == old_name else to_field_name
     359                             for to_field_name in to_fields
     360                         ]
```

**Candidate commits, oldest first:**

- `dcdd219ee1`  2017-12-30  Fixed #25817 -- Made RenameField repoint to_field/to_fields references.
- `503ee41497`  2021-06-29  Refs #29898 -- Moved state_forwards()'s logic from migration operations to ProjectState.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/db/migrations/state.py b/django/db/migrations/state.py
--- a/django/db/migrations/state.py
+++ b/django/db/migrations/state.py
@@ -297,4 +309,1 @@
-                    field.to_fields = tuple([
-                        new_name if to_field_name == old_name else to_field_name
-                        for to_field_name in to_fields
-                    ])
+                    field.to_fields = tuple(
### 503ee41497  2021-05-24  Refs #29898 -- Moved state_forwards()'s logic from migration operations to ProjectState.

diff --git a/django/db/migrations/state.py b/django/db/migrations/state.py
--- a/django/db/migrations/state.py
+++ b/django/db/migrations/state.py
@@ -110,0 +253,4 @@
+                    field.to_fields = tuple([
+                        new_name if to_field_name == old_name else to_field_name
+                        for to_field_name in to_fields
+                    ])

````

</details>

## T007  django  `django/contrib/sessions/backends/file.py:52`

```
      48         """
      49         Get the file associated with this session key.
      50         """
      51         if session_key is None:
>>    52             session_key = self._get_or_create_session_key()
      53 
      54         # Make sure we're not vulnerable to directory traversal. Session keys
      55         # should always be md5s, so they should never contain directory
      56         # components.
```

**Candidate commits, oldest first:**

- `07889c13a6`  2005-08-16  Fixed #1 -- Added anonymous session support via middleware and request.session. Removed th
- `f69cf70ed8`  2006-05-02  MERGED MAGIC-REMOVAL BRANCH TO TRUNK. This change is highly backwards-incompatible. Please
- `bcf7e9a9fe`  2007-09-15  Fixed #2066: session data can now be stored in the cache or on the filesystem. This should
- `bda21e2b9d`  2011-11-27  Fixed #11555 -- Made SessionBase.session_key read-only. Cleaned up code slightly. Refs #13

<details><summary>Line history</summary>

````diff
### bda21e2b9d  2011-11-27  Fixed #11555 -- Made SessionBase.session_key read-only. Cleaned up code slightly. Refs #13478.

diff --git a/django/contrib/sessions/backends/file.py b/django/contrib/sessions/backends/file.py
--- a/django/contrib/sessions/backends/file.py
+++ b/django/contrib/sessions/backends/file.py
@@ -36,1 +36,1 @@
-            session_key = self.session_key
+            session_key = self._get_or_create_session_key()
### bcf7e9a9fe  2007-09-15  Fixed #2066: session data can now be stored in the cache or on the filesystem. This should be fully backwards-compatible (the database cache store is still the default). A big thanks to John D'Agostino for the bulk of this code.

diff --git a/django/contrib/sessions/backends/file.py b/django/contrib/sessions/backends/file.py
--- /dev/null
+++ b/django/contrib/sessions/backends/file.py
@@ -0,0 +20,1 @@
+            session_key = self.session_key

````

</details>

## T008  django  `django/db/backends/postgresql/features.py:140`

```
     136                     "test_group_by_nested_expression_with_params",
     137                 }
     138             )
     139         if not is_psycopg3:
>>   140             expected_failures.update(
     141                 {
     142                     # operator does not exist: bigint[] = integer[]
     143                     "postgres_tests.test_array.TestQuerying.test_gt",
     144                     "postgres_tests.test_array.TestQuerying.test_in",
```

**Candidate commits, oldest first:**

- `82dad11bfe`  2023-01-27  Refs #34255 -- Skipped test_group_by_nested_expression_with_params test on PostgreSQL when
- `2a636118da`  2025-09-05  Fixed #36564 -- Changed DEFAULT_AUTO_FIELD from AutoField to BigAutoField.

<details><summary>Line history</summary>

````diff
### 2a636118da  2025-08-19  Fixed #36564 -- Changed DEFAULT_AUTO_FIELD from AutoField to BigAutoField.

diff --git a/django/db/backends/postgresql/features.py b/django/db/backends/postgresql/features.py
--- a/django/db/backends/postgresql/features.py
+++ b/django/db/backends/postgresql/features.py
@@ -126,0 +127,1 @@
+            expected_failures.update(

````

</details>

## T009  django  `django/contrib/admin/options.py:2194`

```
    2190             ),
    2191             readonly_fields,
    2192             model_admin=self,
    2193         )
>>  2194         media = self.media + admin_form.media
    2195 
    2196         inline_formsets = self.get_inline_formsets(
    2197             request, formsets, inline_instances, obj
    2198         )
```

**Candidate commits, oldest first:**

- `a19ed8aea3`  2008-07-18  Merged the newforms-admin branch into trunk.
- `cd11664066`  2022-09-15  Changed camel case variable to snake case in contrib.admin/auth.

<details><summary>Line history</summary>

````diff
### cd11664066  2022-06-03  Changed camel case variable to snake case in contrib.admin/auth.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -1837,1 +1837,1 @@
-        media = self.media + adminForm.media
+        media = self.media + admin_form.media
### a19ed8aea3  2008-07-18  Merged the newforms-admin branch into trunk.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- /dev/null
+++ b/django/contrib/admin/options.py
@@ -0,0 +559,1 @@
+        media = self.media + adminForm.media

````

</details>

## T010  django  `django/db/backends/postgresql/features.py:119`

```
     115         if self.uses_server_side_binding:
     116             skips.update(
     117                 {
     118                     "The actual query cannot be determined for server side bindings": {
>>   119                         "backends.base.test_base.ExecuteWrapperTests."
     120                         "test_wrapper_debug",
     121                     }
     122                 },
     123             )
```

**Candidate commits, oldest first:**

- `4426b1a72d`  2024-03-06  Fixed #35021 -- Fixed capturing queries when using client-side parameters binding with psy

<details><summary>Line history</summary>

````diff
### 4426b1a72d  2024-02-02  Fixed #35021 -- Fixed capturing queries when using client-side parameters binding with psycopg 3+.

diff --git a/django/db/backends/postgresql/features.py b/django/db/backends/postgresql/features.py
--- a/django/db/backends/postgresql/features.py
+++ b/django/db/backends/postgresql/features.py
@@ -108,0 +112,1 @@
+                        "backends.base.test_base.ExecuteWrapperTests."

````

</details>

## T011  redis  `src/t_stream.c:1757`

```
    1753         *fieldptr = lpGet(si->lp_ele,fieldlen,si->field_buf);
    1754         si->lp_ele = lpNext(si->lp,si->lp_ele);
    1755     }
    1756     *valueptr = lpGet(si->lp_ele,valuelen,si->value_buf);
>>  1757     si->lp_ele = lpNext(si->lp,si->lp_ele);
    1758 }
    1759 
    1760 /* Remove the current entry from the stream: can be called after the
    1761  * GetID() API or after any GetField() call, however we need to iterate
```

**Candidate commits, oldest first:**

- `a58733cacf`  2017-12-01  Streams: stream iteration refactoring, WIP 2.
- `b1ec333633`  2017-12-01  Streams: stream iteration refactoring, WIP 1.

<details><summary>Line history</summary>

````diff
### a58733cac  2017-09-14  Streams: stream iteration refactoring, WIP 2.

diff --git a/src/t_stream.c b/src/t_stream.c
--- a/src/t_stream.c
+++ b/src/t_stream.c
@@ -306,0 +322,1 @@
+    si->lp_ele = lpNext(si->lp,si->lp_ele);

````

</details>

## T012  django  `django/db/models/fields/json.py:507`

```
     503             return sql, all_params
     504         return self.as_sql(compiler, connection)
     505 
     506 
>>   507 JSONField.register_lookup(DataContains)
     508 JSONField.register_lookup(ContainedBy)
     509 JSONField.register_lookup(HasKey)
     510 JSONField.register_lookup(HasKeys)
     511 JSONField.register_lookup(HasAnyKeys)
```

**Candidate commits, oldest first:**

- `6789ded0a6`  2020-05-08  Fixed #12990, Refs #27694 -- Added JSONField model field.

<details><summary>Line history</summary>

````diff
### 6789ded0a6  2019-06-09  Fixed #12990, Refs #27694 -- Added JSONField model field.

diff --git a/django/db/models/fields/json.py b/django/db/models/fields/json.py
--- /dev/null
+++ b/django/db/models/fields/json.py
@@ -0,0 +279,1 @@
+JSONField.register_lookup(DataContains)

````

</details>

## T013  redis  `src/cluster.h:123`

```
     119 void clusterCommandMyShardId(client *c);
     120 
     121 sds clusterGenNodeDescription(client *c, clusterNode *node, int tls_primary);
     122 
>>   123 int clusterNodeCoversSlot(clusterNode *n, int slot);
     124 int clusterDefaultClientPortIsTLS(void);
     125 int getNodeDefaultClientPort(clusterNode *n);
     126 int clusterNodeIsMyself(clusterNode *n);
     127 clusterNode *getMyClusterNode(void);
```

**Candidate commits, oldest first:**

- `0270abda82`  2023-10-15  Replace cluster metadata with slot specific dictionaries (#11695)
- `33ef6a3003`  2023-11-22  Cluster refactor: s/clusterNodeGetSlotBit/clusterNodeCoversSlot/

<details><summary>Line history</summary>

````diff
### 33ef6a300  2023-11-01  Cluster refactor: s/clusterNodeGetSlotBit/clusterNodeCoversSlot/

diff --git a/src/cluster.h b/src/cluster.h
--- a/src/cluster.h
+++ b/src/cluster.h
@@ -59,1 +59,1 @@
-int clusterNodeGetSlotBit(clusterNode *n, int slot);
+int clusterNodeCoversSlot(clusterNode *n, int slot);
### 0270abda8  2023-10-14  Replace cluster metadata with slot specific dictionaries (#11695)

diff --git a/src/cluster.h b/src/cluster.h
--- a/src/cluster.h
+++ b/src/cluster.h
@@ -442,0 +415,1 @@
+int clusterNodeGetSlotBit(clusterNode *n, int slot);

````

</details>

## T014  django  `django/contrib/admin/options.py:2618`

```
    2614             "subtitle": None,
    2615             "action_list": page_obj,
    2616             "page_range": page_range,
    2617             "page_var": PAGE_VAR,
>>  2618             "pagination_required": paginator.count > 100,
    2619             "module_name": str(capfirst(self.opts.verbose_name_plural)),
    2620             "object": obj,
    2621             "opts": self.opts,
    2622             "preserved_filters": self.get_preserved_filters(request),
```

**Candidate commits, oldest first:**

- `ac5cc6cf01`  2021-12-15  Fixed #33316 -- Added pagination to admin history view.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -1956,10 +2208,1 @@
-            'title': _('Change history: %s') % obj,
-            'subtitle': None,
-            'action_list': page_obj,
-            'page_range': page_range,
-            'page_var': PAGE_VAR,
-            'pagination_required': paginator.count > 100,
-            'module_name': str(capfirst(opts.verbose_name_plural)),
-            'object': obj,
-            'opts': opts,
-            'preserved_filters': self.get_preserved_filters(request),
+            "pagination_required": paginator.count > 100,
### ac5cc6cf01  2021-12-14  Fixed #33316 -- Added pagination to admin history view.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -1950,7 +1956,10 @@
             'title': _('Change history: %s') % obj,
             'subtitle': None,
-            'action_list': action_list,
+            'action_list': page_obj,
+            'page_range': page_range,
+            'page_var': PAGE_VAR,
+            'pagination_required': paginator.count > 100,
             'module_name': str(capfirst(opts.verbose_name_plural)),
             'object': obj,
             'opts': opts,
             'preserved_filters': self.get_preserved_filters(request),
### 4e5bbb6ef2  2021-04-24  Fixed #32681 -- Fixed VariableDoesNotExist when rendering some admin template.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -1932,6 +1933,7 @@
             'title': _('Change history: %s') % obj,
+            'subtitle': None,
             'action_list': action_list,
             'module_name': str(capfirst(opts.verbose_name_plural)),
             'object': obj,
             'opts': opts,
             'preserved_filters': self.get_preserved_filters(request),
### d13a9e44de  2017-12-11  Fixed #28909 -- Simplified code using tuple/list/set/dict unpacking.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -1818,10 +1818,6 @@
-        context = dict(
-            self.admin_site.each_context(request),
-            title=_('Change history: %s') % obj,
-            action_list=action_list,
-            module_name=str(capfirst(opts.verbose_name_plural)),
-            object=obj,
-            opts=opts,
-            preserved_filters=self.get_preserved_filters(request),
-        )
-        context.update(extra_context or {})
+            'title': _('Change history: %s') % obj,
+            'action_list': action_list,
+            'module_name': str(capfirst(opts.verbose_name_plural)),
+            'object': obj,
+            'opts': opts,
+            'preserved_filters': self.get_preserved_filters(request),
### 301de774c2  2017-04-21  Refs #27795 -- Replaced many force_text() with str()

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -1768,10 +1767,10 @@
         context = dict(
             self.admin_site.each_context(request),
             title=_('Change history: %s') % obj,
             action_list
... (cut, so use `git log -L` for the rest)
````

</details>

## T015  django  `django/db/backends/postgresql/client.py:53`

```
      49             env["PGSSLCERT"] = str(sslcert)
      50         if sslkey:
      51             env["PGSSLKEY"] = str(sslkey)
      52         if passfile:
>>    53             env["PGPASSFILE"] = str(passfile)
      54         return args, (env or None)
      55 
      56     def runshell(self, parameters):
      57         sigint_handler = signal.getsignal(signal.SIGINT)
```

**Candidate commits, oldest first:**

- `8380fe08a0`  2021-03-01  Fixed #32456 -- Added dbshell support for specifying a password file on PostgreSQL.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/db/backends/postgresql/client.py b/django/db/backends/postgresql/client.py
--- a/django/db/backends/postgresql/client.py
+++ b/django/db/backends/postgresql/client.py
@@ -53,1 +53,1 @@
-            env['PGPASSFILE'] = str(passfile)
+            env["PGPASSFILE"] = str(passfile)
### 8380fe08a0  2021-02-24  Fixed #32456 -- Added dbshell support for specifying a password file on PostgreSQL.

diff --git a/django/db/backends/postgresql/client.py b/django/db/backends/postgresql/client.py
--- a/django/db/backends/postgresql/client.py
+++ b/django/db/backends/postgresql/client.py
@@ -51,0 +53,1 @@
+            env['PGPASSFILE'] = str(passfile)

````

</details>

## T016  redis  `src/acl.c:2100`

```
    2096 
    2097         if (open_bracket_start == -1 &&
    2098             (op[0] == '(' && op[sdslen(op) - 1] != ')')) {
    2099             selector = sdsdup(argv[j]);
>>  2100             open_bracket_start = j;
    2101             continue;
    2102         }
    2103 
    2104         if (open_bracket_start != -1) {
```

**Candidate commits, oldest first:**

- `55c81f2cd3`  2022-01-20  ACL V2 - Selectors and key based permissions (#9974)

<details><summary>Line history</summary>

````diff
### 55c81f2cd  2022-01-20  ACL V2 - Selectors and key based permissions (#9974)

diff --git a/src/acl.c b/src/acl.c
--- a/src/acl.c
+++ b/src/acl.c
@@ -1430,9 +1891,1 @@
- * idx and count are the index and count of channel arguments from the
- * command. The literal argument controls whether the user's ACL channels are 
- * evaluated as literal values or matched as glob-like patterns.
- *
- * If the user can execute the command ACL_OK is returned, otherwise 
- * ACL_DENIED_CHANNEL. */
-int ACLCheckPubsubPerm(const user *u, robj **argv, int idx, int count, int literal, int *idxptr) {
-    /* If there is no associated user, the connection can run anything. */
-    if (u == NULL) return ACL_OK;
+            open_bracket_start = j;
### a56d4533b  2021-09-23  Adding ACL support for modules (#9309)

diff --git a/src/acl.c b/src/acl.c
--- a/src/acl.c
+++ b/src/acl.c
@@ -1348,11 +1357,9 @@
  * idx and count are the index and count of channel arguments from the
  * command. The literal argument controls whether the user's ACL channels are 
  * evaluated as literal values or matched as glob-like patterns.
  *
  * If the user can execute the command ACL_OK is returned, otherwise 
  * ACL_DENIED_CHANNEL. */
-int ACLCheckPubsubPerm(client *c, int idx, int count, int literal, int *idxptr) {
-    user *u = c->user;
-
+int ACLCheckPubsubPerm(const user *u, robj **argv, int idx, int count, int literal, int *idxptr) {
     /* If there is no associated user, the connection can run anything. */
     if (u == NULL) return ACL_OK;
### c1b1e8c32  2020-12-01  Adds pub/sub channel patterns to ACL (#7993)

diff --git a/src/acl.c b/src/acl.c
--- a/src/acl.c
+++ b/src/acl.c
@@ -1196,0 +1340,11 @@
+ * idx and count are the index and count of channel arguments from the
+ * command. The literal argument controls whether the user's ACL channels are 
+ * evaluated as literal values or matched as glob-like patterns.
+ *
+ * If the user can execute the command ACL_OK is returned, otherwise 
+ * ACL_DENIED_CHANNEL. */
+int ACLCheckPubsubPerm(client *c, int idx, int count, int literal, int *idxptr) {
+    user *u = c->user;
+
+    /* If there is no associated user, the connection can run anything. */
+    if (u == NULL) return ACL_OK;

````

</details>

## T017  redis  `src/t_set.c:3936`

```
    3932             vecPush(vdeleted, c->argv[pos]);
    3933             res = SME_DELETED;
    3934         } else {
    3935             setTypeConvertToExpireEncoding(set);
>>  3936             const setTypeOps *ops = setTypeGetOps(set->encoding);
    3937             serverAssert(ops->setExpire(set, member, sdslen(member), 0, 1, (uint64_t)args.expireTime));
    3938             vecPush(vupdated, c->argv[pos]);
    3939             res = SME_UPDATED;
    3940         }
```

**Candidate commits, oldest first:**

- `38087a9f7f`  2026-10-11  Refactor t_set.c: dispatch per-encoding logic via setTypeOps (#15766)
- `a76a3689a0`  2026-10-28  Set member expiration (#15938)

<details><summary>Line history</summary>

````diff
### a76a3689a  2026-10-28  Set member expiration (#15938)

diff --git a/src/t_set.c b/src/t_set.c
--- a/src/t_set.c
+++ b/src/t_set.c
@@ -1794,0 +3936,1 @@
+            const setTypeOps *ops = setTypeGetOps(set->encoding);

````

</details>

## T018  redis  `src/server.c:2726`

```
    2722             oom_score_adj_base = atoi(buf);
    2723             close(fd);
    2724         }
    2725 
>>  2726         val = server.oom_score_adj_values[process_class];
    2727         if (server.oom_score_adj == OOM_SCORE_RELATIVE)
    2728             val += oom_score_adj_base;
    2729         if (val > 1000) val = 1000;
    2730         if (val < -1000) val = -1000;
```

**Candidate commits, oldest first:**

- `2530dc0ebd`  2020-08-12  Add oom-score-adj configuration option to control Linux OOM killer. (#1690)
- `61954951ed`  2020-11-22  Fix oom-score-adj-values range, abs options, and bug when used in config file (#8046)
- `0e5b813ef9`  2021-12-01  Multiparam config set (#9748)

<details><summary>Line history</summary>

````diff
### 0e5b813ef  2021-12-01  Multiparam config set (#9748)

diff --git a/src/server.c b/src/server.c
--- a/src/server.c
+++ b/src/server.c
@@ -3853,5 +3852,1 @@
-    val = server.oom_score_adj_values[process_class];
-    if (server.oom_score_adj == OOM_SCORE_RELATIVE)
-        val += server.oom_score_adj_base;
-    if (val > 1000) val = 1000;
-    if (val < -1000) val = -1000;
+        val = server.oom_score_adj_values[process_class];
### 61954951e  2020-11-22  Fix oom-score-adj-values range, abs options, and bug when used in config file (#8046)

diff --git a/src/server.c b/src/server.c
--- a/src/server.c
+++ b/src/server.c
@@ -2681,3 +2681,5 @@
-    val = server.oom_score_adj_base + server.oom_score_adj_values[process_class];
+    val = server.oom_score_adj_values[process_class];
+    if (server.oom_score_adj == OOM_SCORE_RELATIVE)
+        val += server.oom_score_adj_base;
     if (val > 1000) val = 1000;
     if (val < -1000) val = -1000;
### 2530dc0eb  2020-08-12  Add oom-score-adj configuration option to control Linux OOM killer. (#1690)

diff --git a/src/server.c b/src/server.c
--- a/src/server.c
+++ b/src/server.c
@@ -2530,0 +2565,3 @@
+    val = server.oom_score_adj_base + server.oom_score_adj_values[process_class];
+    if (val > 1000) val = 1000;
+    if (val < -1000) val = -1000;

````

</details>

## T019  redis  `src/zset_btree.c:2524`

```
    2520  * The current score encoding can represent every remaining score, so a
    2521  * fresh encoding never needs more bits. */
    2522 static size_t zbtScoreLeafLiveBytes(zbtScoreLeaf *leaf) {
    2523     return offsetof(zbtScoreLeaf, data) +
>>  2524            zbtScoreLeafScoreBytes(leaf->n.count, leaf->score_bits) +
    2525            leaf->n.count * (sizeof(uint16_t) + sizeof(uint8_t)) +
    2526            zbtScoreLeafRecordBytes(leaf);
    2527 }
    2528 
```

**Candidate commits, oldest first:**

- `81d653f5dc`  2026-10-23  Reduce large sorted set memory with a packed B+ tree (#15635)

<details><summary>Line history</summary>

````diff
### 81d653f5d  2026-10-23  Reduce large sorted set memory with a packed B+ tree (#15635)

diff --git a/src/zset_btree.c b/src/zset_btree.c
--- /dev/null
+++ b/src/zset_btree.c
@@ -0,0 +2524,1 @@
+           zbtScoreLeafScoreBytes(leaf->n.count, leaf->score_bits) +

````

</details>

## T020  redis  `src/defrag.c:794`

```
     790     zset *zs = (zset*)ob->ptr;
     791     zset *newzs;
     792     zskiplist *newzsl;
     793     dict *newdict;
>>   794     struct zskiplistNode *newheader;
     795     serverAssert(ob->type == OBJ_ZSET && ob->encoding == OBJ_ENCODING_SKIPLIST);
     796     if ((newzs = activeDefragAlloc(zs)))
     797         ob->ptr = zs = newzs;
     798     if ((newzsl = activeDefragAlloc(zs->zsl)))
```

**Candidate commits, oldest first:**

- `5ab6a54cc6`  2017-01-02  active defrag improvements
- `be1b4aa9aa`  2018-03-12  active defrag v2

<details><summary>Line history</summary>

````diff
### be1b4aa9a  2018-02-18  active defrag v2

diff --git a/src/defrag.c b/src/defrag.c
--- a/src/defrag.c
+++ b/src/defrag.c
@@ -272,0 +534,1 @@
+    struct zskiplistNode *newheader;

````

</details>

## T021  django  `django/contrib/admin/options.py:1361`

```
    1357 
    1358             term_queries = []
    1359             for bit in smart_split(search_term):
    1360                 if bit.startswith(('"', "'")) and bit[0] == bit[-1]:
>>  1361                     bit = unescape_string_literal(bit)
    1362                 # Build term lookups, skipping values that cannot be converted
    1363                 # to the expected type.
    1364                 bit_lookups = []
    1365                 for orm_lookup, validate_field in orm_lookups:
```

**Candidate commits, oldest first:**

- `26a413507a`  2020-06-18  Fixed #6933 -- Added support for searching against quoted phrases in ModelAdmin.search_fie

<details><summary>Line history</summary>

````diff
### 26a413507a  2020-05-26  Fixed #6933 -- Added support for searching against quoted phrases in ModelAdmin.search_fields.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -1025,1 +1029,1 @@
-            for bit in search_term.split():
+                    bit = unescape_string_literal(bit)
### 470a9bb22d  2013-08-04  Moved get_search_results from BaseModelAdmin to ModelAdmin.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -778,0 +770,1 @@
+            for bit in search_term.split():

````

</details>

## T022  django  `django/contrib/gis/utils/ogrinspect.py:199`

```
     195 
     196     yield "class %s(models.Model):" % model_name
     197 
     198     for field_name, width, precision, field_type in zip(
>>   199         ogr_fields, layer.field_widths, layer.field_precisions, layer.field_types
     200     ):
     201         # The model field name.
     202         mfield = field_name.lower()
     203         if mfield[-1:] == "_":
```

**Candidate commits, oldest first:**

- `79e68c225b`  2008-08-05  Merged the gis branch into trunk.
- `1aae1cba99`  2012-05-07  Imported zip from future_builtins instead of itertools.izip.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/contrib/gis/utils/ogrinspect.py b/django/contrib/gis/utils/ogrinspect.py
--- a/django/contrib/gis/utils/ogrinspect.py
+++ b/django/contrib/gis/utils/ogrinspect.py
@@ -177,1 +197,1 @@
-            ogr_fields, layer.field_widths, layer.field_precisions, layer.field_types):
+        ogr_fields, layer.field_widths, layer.field_precisions, layer.field_types
### 1101467ce0  2014-09-04  Limited lines to 119 characters in django/

diff --git a/django/contrib/gis/utils/ogrinspect.py b/django/contrib/gis/utils/ogrinspect.py
--- a/django/contrib/gis/utils/ogrinspect.py
+++ b/django/contrib/gis/utils/ogrinspect.py
@@ -177,1 +178,1 @@
-    for field_name, width, precision, field_type in zip(ogr_fields, layer.field_widths, layer.field_precisions, layer.field_types):
+            ogr_fields, layer.field_widths, layer.field_precisions, layer.field_types):
### 1aae1cba99  2012-05-07  Imported zip from future_builtins instead of itertools.izip.

diff --git a/django/contrib/gis/utils/ogrinspect.py b/django/contrib/gis/utils/ogrinspect.py
--- a/django/contrib/gis/utils/ogrinspect.py
+++ b/django/contrib/gis/utils/ogrinspect.py
@@ -168,1 +168,1 @@
-    for field_name, width, precision, field_type in izip(ogr_fields, layer.field_widths, layer.field_precisions, layer.field_types):
+    for field_name, width, precision, field_type in zip(ogr_fields, layer.field_widths, layer.field_precisions, layer.field_types):
### 79e68c225b  2008-08-05  Merged the gis branch into trunk.

diff --git a/django/contrib/gis/utils/ogrinspect.py b/django/contrib/gis/utils/ogrinspect.py
--- /dev/null
+++ b/django/contrib/gis/utils/ogrinspect.py
@@ -0,0 +168,1 @@
+    for field_name, width, precision, field_type in izip(ogr_fields, layer.field_widths, layer.field_precisions, layer.field_types):

````

</details>

## T023  django  `django/db/models/options.py:984`

```
     980         of fields guaranteed to be unique for all rows.
     981         """
     982         return [
     983             constraint
>>   984             for constraint in self.constraints
     985             if (
     986                 isinstance(constraint, UniqueConstraint)
     987                 and constraint.condition is None
     988                 and not constraint.contains_expressions
```

**Candidate commits, oldest first:**

- `d270c10a72`  2020-02-19  Refs #31187 -- Added total_unique_constraints property to model's Options.

<details><summary>Line history</summary>

````diff
### d270c10a72  2020-02-19  Refs #31187 -- Added total_unique_constraints property to model's Options.

diff --git a/django/db/models/options.py b/django/db/models/options.py
--- a/django/db/models/options.py
+++ b/django/db/models/options.py
@@ -831,0 +838,1 @@
+            for constraint in self.constraints

````

</details>

## T024  redis  `src/module.c:8469`

```
    8465 
    8466     if (level < server.verbosity) return;
    8467 
    8468     name_len = snprintf(msg, sizeof(msg),"<%s> ", module? module->name: "module");
>>  8469     vsnprintf(msg + name_len, sizeof(msg) - name_len, fmt, ap);
    8470     serverLogRaw(level,msg);
    8471 }
    8472 
    8473 /* Produces a log message to the standard Redis log, the format accepts
```

**Candidate commits, oldest first:**

- `715794b829`  2016-06-23  Add RedisModule_Log() logging API function.
- `a1b1fd4f39`  2016-10-02  Modules: API to log from module I/O callbacks.

<details><summary>Line history</summary>

````diff
### a1b1fd4f3  2016-10-02  Modules: API to log from module I/O callbacks.

diff --git a/src/module.c b/src/module.c
--- a/src/module.c
+++ b/src/module.c
@@ -2911,1 +2929,1 @@
-/* Produces a log message to the standard Redis log, the format accepts
+    vsnprintf(msg + name_len, sizeof(msg) - name_len, fmt, ap);
### 4b12c6a36  2016-06-23  Modules: changes to logging function.

diff --git a/src/module.c b/src/module.c
--- a/src/module.c
+++ b/src/module.c
@@ -2775,3 +2775,1 @@
-/* Produces a log message to the standard Redis log. */
-void RM_Log(RedisModuleCtx *ctx, int level, const char *fmt, ...)
-{
+/* Produces a log message to the standard Redis log, the format accepts
### 715794b82  2016-06-15  Add RedisModule_Log() logging API function.

diff --git a/src/module.c b/src/module.c
--- a/src/module.c
+++ b/src/module.c
@@ -2772,0 +2775,3 @@
+/* Produces a log message to the standard Redis log. */
+void RM_Log(RedisModuleCtx *ctx, int level, const char *fmt, ...)
+{

````

</details>

## T025  redis  `src/t_set.c:2637`

```
    2633             lp = lpBatchDelete(lp, ps, remaining);
    2634             zfree(ps);
    2635             set->ptr = lp;
    2636         } else {
>>  2637             const int keepExpire = setTypeHasExpireSupport(set);
    2638             while(remaining--) {
    2639                 int encoding = setTypeRandomElement(set, &str, &len, &llele);
    2640                 uint64_t expire = EB_EXPIRE_TIME_INVALID;
    2641                 if (keepExpire) {
```

**Candidate commits, oldest first:**

- `a76a3689a0`  2026-10-28  Set member expiration (#15938)

<details><summary>Line history</summary>

````diff
### a76a3689a  2026-10-28  Set member expiration (#15938)

diff --git a/src/t_set.c b/src/t_set.c
--- a/src/t_set.c
+++ b/src/t_set.c
@@ -750,0 +2637,1 @@
+            const int keepExpire = setTypeHasExpireSupport(set);

````

</details>

## T026  django  `django/test/utils.py:223`

```
     219                 with time_keeper.timed("  Creating '%s'" % alias):
     220                     connection.creation.create_test_db(
     221                         verbosity=verbosity,
     222                         autoclobber=not interactive,
>>   223                         keepdb=keepdb,
     224                     )
     225                     if serialized_aliases is None or alias in serialized_aliases:
     226                         serialize_connections.append(connection)
     227                 if parallel > 1:
```

**Candidate commits, oldest first:**

- `9012833af8`  2013-05-11  Fixed #17365, #17366, #18727 -- Switched to discovery test runner.
- `b7aa7c4ab4`  2014-05-28  Fixed #20550 -- Added ability to preserve test db between runs
- `8c12d51ea2`  2014-06-09  Fixed #22487: Optional rollback emulation for migrated apps
- `e76981b433`  2016-08-17  Fixed #26840 -- Added test.utils.setup/teardown_databases().
- `61a0ba43cf`  2020-08-13  Refs #31811 -- Added optional timing outputs to the test runner.

<details><summary>Line history</summary>

````diff
### 61a0ba43cf  2020-07-22  Refs #31811 -- Added optional timing outputs to the test runner.

diff --git a/django/test/utils.py b/django/test/utils.py
--- a/django/test/utils.py
+++ b/django/test/utils.py
@@ -170,6 +177,1 @@
-                connection.creation.create_test_db(
-                    verbosity=verbosity,
-                    autoclobber=not interactive,
-                    keepdb=keepdb,
-                    serialize=connection.settings_dict['TEST'].get('SERIALIZE', True),
-                )
+                        keepdb=keepdb,
### 2540c5f08c  2019-12-04  Removed unnecessary dict.get() call in favor of direct indexing.

diff --git a/django/test/utils.py b/django/test/utils.py
--- a/django/test/utils.py
+++ b/django/test/utils.py
@@ -169,6 +169,6 @@
                 connection.creation.create_test_db(
                     verbosity=verbosity,
                     autoclobber=not interactive,
                     keepdb=keepdb,
-                    serialize=connection.settings_dict.get('TEST', {}).get('SERIALIZE', True),
+                    serialize=connection.settings_dict['TEST'].get('SERIALIZE', True),
                 )
### e76981b433  2016-07-03  Fixed #26840 -- Added test.utils.setup/teardown_databases().

diff --git a/django/test/utils.py b/django/test/utils.py
--- a/django/test/utils.py
+++ b/django/test/utils.py
@@ -158,0 +177,6 @@
+                connection.creation.create_test_db(
+                    verbosity=verbosity,
+                    autoclobber=not interactive,
+                    keepdb=keepdb,
+                    serialize=connection.settings_dict.get('TEST', {}).get('SERIALIZE', True),
+                )

````

</details>

## T027  redis  `src/t_set.c:2634`

```
    2630                 p = lpNext(lp, p);
    2631                 index++;
    2632             }
    2633             lp = lpBatchDelete(lp, ps, remaining);
>>  2634             zfree(ps);
    2635             set->ptr = lp;
    2636         } else {
    2637             const int keepExpire = setTypeHasExpireSupport(set);
    2638             while(remaining--) {
```

**Candidate commits, oldest first:**

- `4e472a1a7f`  2022-11-09  Listpack encoding for sets (#11290)

<details><summary>Line history</summary>

````diff
### 4e472a1a7  2022-11-09  Listpack encoding for sets (#11290)

diff --git a/src/t_set.c b/src/t_set.c
--- a/src/t_set.c
+++ b/src/t_set.c
@@ -556,6 +855,1 @@
-        while(remaining--) {
-            encoding = setTypeRandomElement(set,&sdsele,&llele);
-            if (encoding == OBJ_ENCODING_INTSET) {
-                sdsele = sdsfromlonglong(llele);
-            } else {
-                sdsele = sdsdup(sdsele);
+            zfree(ps);
### 86d48efbf  2015-07-31  Lazyfree: Convert Sets to use plains SDS (several commits squashed).

diff --git a/src/t_set.c b/src/t_set.c
--- a/src/t_set.c
+++ b/src/t_set.c
@@ -512,6 +505,6 @@
         while(remaining--) {
-            encoding = setTypeRandomElement(set,&objele,&llele);
+            encoding = setTypeRandomElement(set,&sdsele,&llele);
             if (encoding == OBJ_ENCODING_INTSET) {
-                objele = createStringObjectFromLongLong(llele);
+                sdsele = sdsfromlonglong(llele);
             } else {
-                incrRefCount(objele);
+                sdsele = sdsdup(sdsele);
### 14ff57248  2015-07-26  RDMF: OBJ_ macros for object related stuff.

diff --git a/src/t_set.c b/src/t_set.c
--- a/src/t_set.c
+++ b/src/t_set.c
@@ -512,6 +512,6 @@
         while(remaining--) {
             encoding = setTypeRandomElement(set,&objele,&llele);
-            if (encoding == REDIS_ENCODING_INTSET) {
+            if (encoding == OBJ_ENCODING_INTSET) {
                 objele = createStringObjectFromLongLong(llele);
             } else {
                 incrRefCount(objele);
### 9feee428f  2015-02-10  SPOP: reimplemented for speed and better distribution.

diff --git a/src/t_set.c b/src/t_set.c
--- a/src/t_set.c
+++ b/src/t_set.c
@@ -585,1 +498,6 @@
-        decrRefCount(propargv[0]);
+        while(remaining--) {
+            encoding = setTypeRandomElement(set,&objele,&llele);
+            if (encoding == REDIS_ENCODING_INTSET) {
+                objele = createStringObjectFromLongLong(llele);
+            } else {
+                incrRefCount(objele);
### cc7f0434b  2015-02-09  Change alsoPropagate() behavior to make it more usable.

diff --git a/src/t_set.c b/src/t_set.c
--- a/src/t_set.c
+++ b/src/t_set.c
@@ -588,0 +585,1 @@
+        decrRefCount(propargv[0]);

````

</details>

## T028  django  `django/contrib/postgres/fields/ranges.py:270`

```
     266 
     267 class RangeContainedBy(PostgresOperatorLookup):
     268     lookup_name = "contained_by"
     269     type_mapping = {
>>   270         "smallint": "int4range",
     271         "integer": "int4range",
     272         "bigint": "int8range",
     273         "double precision": "numrange",
     274         "numeric": "numrange",
```

**Candidate commits, oldest first:**

- `5d674eac87`  2019-12-05  Fixed #31039 -- Added support for contained_by lookup with AutoFields, SmallIntegerField, 
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/contrib/postgres/fields/ranges.py b/django/contrib/postgres/fields/ranges.py
--- a/django/contrib/postgres/fields/ranges.py
+++ b/django/contrib/postgres/fields/ranges.py
@@ -237,7 +249,1 @@
-        'smallint': 'int4range',
-        'integer': 'int4range',
-        'bigint': 'int8range',
-        'double precision': 'numrange',
-        'numeric': 'numrange',
-        'date': 'daterange',
-        'timestamp with time zone': 'tstzrange',
+        "smallint": "int4range",
### 5d674eac87  2019-12-05  Fixed #31039 -- Added support for contained_by lookup with AutoFields, SmallIntegerField, and DecimalField.

diff --git a/django/contrib/postgres/fields/ranges.py b/django/contrib/postgres/fields/ranges.py
--- a/django/contrib/postgres/fields/ranges.py
+++ b/django/contrib/postgres/fields/ranges.py
@@ -202,5 +202,7 @@
+        'smallint': 'int4range',
         'integer': 'int4range',
         'bigint': 'int8range',
         'double precision': 'numrange',
+        'numeric': 'numrange',
         'date': 'daterange',
         'timestamp with time zone': 'tstzrange',
### 7bda2d8ebc  2015-05-21  Fixed #24837 -- field__contained_by=Range

diff --git a/django/contrib/postgres/fields/ranges.py b/django/contrib/postgres/fields/ranges.py
--- a/django/contrib/postgres/fields/ranges.py
+++ b/django/contrib/postgres/fields/ranges.py
@@ -101,0 +104,5 @@
+        'integer': 'int4range',
+        'bigint': 'int8range',
+        'double precision': 'numrange',
+        'date': 'daterange',
+        'timestamp with time zone': 'tstzrange',

````

</details>

## T029  django  `django/contrib/syndication/views.py:120`

```
     116         """
     117         Return an extra keyword arguments dictionary that is used with
     118         the `add_item` call of the feed generator.
     119         """
>>   120         return {}
     121 
     122     def get_object(self, request, *args, **kwargs):
     123         return None
     124 
```

**Candidate commits, oldest first:**

- `c4c27d8a04`  2010-01-28  Fixed #6188, #6304, #6618, #6969, #8758, #8989, #10334, #11069, #11973 and #12403 -- Modif

<details><summary>Line history</summary>

````diff
### c4c27d8a04  2010-01-28  Fixed #6188, #6304, #6618, #6969, #8758, #8989, #10334, #11069, #11973 and #12403 -- Modified the syndication framework to use class-based views. Thanks to Ben Firshman for his work on this patch.

diff --git a/django/contrib/syndication/views.py b/django/contrib/syndication/views.py
--- a/django/contrib/syndication/views.py
+++ b/django/contrib/syndication/views.py
@@ -3,0 +84,1 @@
+        return {}

````

</details>

## T030  django  `django/db/models/options.py:220`

```
     216 
     217             self.unique_together = normalize_together(self.unique_together)
     218             # App label/class name interpolation for names of constraints and
     219             # indexes.
>>   220             if not self.abstract:
     221                 self.constraints = self._format_names(self.constraints)
     222                 self.indexes = self._format_names(self.indexes)
     223 
     224             # verbose_name_plural is a special case because it uses a 's'
```

**Candidate commits, oldest first:**

- `9e35c8b2e3`  2024-03-07  Refs #30397 -- Optimized interpolation of index and constraint names a bit.

<details><summary>Line history</summary>

````diff
### 9e35c8b2e3  2024-03-07  Refs #30397 -- Optimized interpolation of index and constraint names a bit.

diff --git a/django/db/models/options.py b/django/db/models/options.py
--- a/django/db/models/options.py
+++ b/django/db/models/options.py
@@ -206,4 +206,1 @@
-            if not getattr(cls._meta, "abstract", False):
-                for attr_name in {"constraints", "indexes"}:
-                    objs = getattr(self, attr_name, [])
-                    setattr(self, attr_name, self._format_names_with_class(cls, objs))
+            if not self.abstract:
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/db/models/options.py b/django/db/models/options.py
--- a/django/db/models/options.py
+++ b/django/db/models/options.py
@@ -180,4 +205,4 @@
-            if not getattr(cls._meta, 'abstract', False):
-                for attr_name in {'constraints', 'indexes'}:
+            if not getattr(cls._meta, "abstract", False):
+                for attr_name in {"constraints", "indexes"}:
                     objs = getattr(self, attr_name, [])
                     setattr(self, attr_name, self._format_names_with_class(cls, objs))
### febe136d4c  2019-07-05  Fixed #30397 -- Added app_label/class interpolation for names of indexes and constraints.

diff --git a/django/db/models/options.py b/django/db/models/options.py
--- a/django/db/models/options.py
+++ b/django/db/models/options.py
@@ -183,0 +185,4 @@
+            if not getattr(cls._meta, 'abstract', False):
+                for attr_name in {'constraints', 'indexes'}:
+                    objs = getattr(self, attr_name, [])
+                    setattr(self, attr_name, self._format_names_with_class(cls, objs))

````

</details>

## T031  django  `django/db/models/functions/window.py:5`

```
       1 from django.db.models.expressions import Func
       2 from django.db.models.fields import FloatField, IntegerField
       3 
       4 __all__ = [
>>     5     "CumeDist",
       6     "DenseRank",
       7     "FirstValue",
       8     "Lag",
       9     "LastValue",
```

**Candidate commits, oldest first:**

- `d549b88050`  2017-09-18  Fixed #26608 -- Added support for window expressions (OVER clause).
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/db/models/functions/window.py b/django/db/models/functions/window.py
--- a/django/db/models/functions/window.py
+++ b/django/db/models/functions/window.py
@@ -5,2 +5,1 @@
-    'CumeDist', 'DenseRank', 'FirstValue', 'Lag', 'LastValue', 'Lead',
-    'NthValue', 'Ntile', 'PercentRank', 'Rank', 'RowNumber',
+    "CumeDist",
### d549b88050  2017-09-18  Fixed #26608 -- Added support for window expressions (OVER clause).

diff --git a/django/db/models/functions/window.py b/django/db/models/functions/window.py
--- /dev/null
+++ b/django/db/models/functions/window.py
@@ -0,0 +4,2 @@
+    'CumeDist', 'DenseRank', 'FirstValue', 'Lag', 'LastValue', 'Lead',
+    'NthValue', 'Ntile', 'PercentRank', 'Rank', 'RowNumber',

````

</details>

## T032  django  `django/contrib/auth/password_validation.py:245`

```
     241     """
     242 
     243     @functools.cached_property
     244     def DEFAULT_PASSWORD_LIST_PATH(self):
>>   245         return Path(__file__).resolve().parent / "common-passwords.txt.gz"
     246 
     247     def __init__(self, password_list_path=DEFAULT_PASSWORD_LIST_PATH):
     248         if password_list_path is CommonPasswordValidator.DEFAULT_PASSWORD_LIST_PATH:
     249             password_list_path = self.DEFAULT_PASSWORD_LIST_PATH
```

**Candidate commits, oldest first:**

- `11b8c30b9e`  2018-04-20  Ref #23919 -- Replaced some os.path usage with pathlib.Path.
- `edeec1247e`  2019-11-05  Passed strict=True to Path.resolve() to enforce that the path must exist.
- `e39e727ded`  2020-08-28  Fixed #31912 -- Removed strict=True in Path.resolve() in project template and CommonPasswo
- `9ee693bd6c`  2021-04-01  Fixed #32316 -- Deferred accessing __file__.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/contrib/auth/password_validation.py b/django/contrib/auth/password_validation.py
--- a/django/contrib/auth/password_validation.py
+++ b/django/contrib/auth/password_validation.py
@@ -209,1 +225,1 @@
-        return Path(__file__).resolve().parent / 'common-passwords.txt.gz'
+        return Path(__file__).resolve().parent / "common-passwords.txt.gz"
### 9ee693bd6c  2021-01-04  Fixed #32316 -- Deferred accessing __file__.

diff --git a/django/contrib/auth/password_validation.py b/django/contrib/auth/password_validation.py
--- a/django/contrib/auth/password_validation.py
+++ b/django/contrib/auth/password_validation.py
@@ -170,1 +173,1 @@
-    DEFAULT_PASSWORD_LIST_PATH = Path(__file__).resolve().parent / 'common-passwords.txt.gz'
+        return Path(__file__).resolve().parent / 'common-passwords.txt.gz'
### e39e727ded  2020-08-28  Fixed #31912 -- Removed strict=True in Path.resolve() in project template and CommonPasswordValidator.

diff --git a/django/contrib/auth/password_validation.py b/django/contrib/auth/password_validation.py
--- a/django/contrib/auth/password_validation.py
+++ b/django/contrib/auth/password_validation.py
@@ -170,1 +170,1 @@
-    DEFAULT_PASSWORD_LIST_PATH = Path(__file__).resolve(strict=True).parent / 'common-passwords.txt.gz'
+    DEFAULT_PASSWORD_LIST_PATH = Path(__file__).resolve().parent / 'common-passwords.txt.gz'
### edeec1247e  2019-11-01  Passed strict=True to Path.resolve() to enforce that the path must exist.

diff --git a/django/contrib/auth/password_validation.py b/django/contrib/auth/password_validation.py
--- a/django/contrib/auth/password_validation.py
+++ b/django/contrib/auth/password_validation.py
@@ -170,1 +170,1 @@
-    DEFAULT_PASSWORD_LIST_PATH = Path(__file__).resolve().parent / 'common-passwords.txt.gz'
+    DEFAULT_PASSWORD_LIST_PATH = Path(__file__).resolve(strict=True).parent / 'common-passwords.txt.gz'
### 11b8c30b9e  2017-07-21  Ref #23919 -- Replaced some os.path usage with pathlib.Path.

diff --git a/django/contrib/auth/password_validation.py b/django/contrib/auth/password_validation.py
--- a/django/contrib/auth/password_validation.py
+++ b/django/contrib/auth/password_validation.py
@@ -168,3 +168,1 @@
-    DEFAULT_PASSWORD_LIST_PATH = os.path.join(
-        os.path.dirname(os.path.realpath(__file__)), 'common-passwords.txt.gz'
-    )
+    DEFAULT_PASSWORD_LIST_PATH = Path(__file__).resolve().parent / 'common-passwords.txt.gz'
### 4e729feaa6  2017-01-20  Refs #23919 -- Removed django.utils._os.upath()/npath()/abspathu() usage.

diff --git a/django/contrib/auth/password_validation.py b/django/contrib/auth/password_validation.py
--- a/django/contrib/auth/password_validation.py
+++ b/django/contrib/auth/password_validation.py
@@ -170,3 +169,3 @@
     DEFAULT_PASSWORD_LIST_PATH = os.path.join(
-        os.path.dirname(os.path.realpath(upath(__file__))), 'common-passwords.txt.gz'
+        os.path.dirname(os.path.realpath(__file__)), 'common-passwords.txt.gz'
     )
### 55b3bd8468  2015-06-08  Refs #16860 -- Minor edits and fixes to password validation.

diff --git a/django/contrib/auth/password_validation.py b/django/contrib/auth/password_validation.py
--- a/django/contrib/auth/password_validation.py
+++ b/django/contrib/auth/password_validation.py
@@ -148,1 +156,3 @@
-    DEFAULT_PASSWORD_LIST_PATH = os.path.dirname(os.path.realpath(__file__)) + '/common-passwords.txt.gz'
+    DEFAULT_PASSWORD_LI
... (cut, so use `git log -L` for the rest)
````

</details>

## T033  django  `django/test/utils.py:934`

```
     930                 "APP_DIRS": True,
     931             },
     932             {
     933                 "BACKEND": "django.template.backends.jinja2.Jinja2",
>>   934                 "APP_DIRS": True,
     935                 "OPTIONS": {"keep_trailing_newline": True},
     936             },
     937         ]
     938     )(test_func)
```

**Candidate commits, oldest first:**

- `2133f3157e`  2015-02-03  Fixed #24168 -- Allowed selecting a template engine in a few APIs.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/test/utils.py b/django/test/utils.py
--- a/django/test/utils.py
+++ b/django/test/utils.py
@@ -831,8 +874,1 @@
-    return override_settings(TEMPLATES=[{
-        'BACKEND': 'django.template.backends.django.DjangoTemplates',
-        'APP_DIRS': True,
-    }, {
-        'BACKEND': 'django.template.backends.jinja2.Jinja2',
-        'APP_DIRS': True,
-        'OPTIONS': {'keep_trailing_newline': True},
-    }])(test_func)
+                "APP_DIRS": True,
### 8b3f1c35dd  2019-04-24  Removed unnecessary assignments in various code.

diff --git a/django/test/utils.py b/django/test/utils.py
--- a/django/test/utils.py
+++ b/django/test/utils.py
@@ -760,8 +759,8 @@
-    test_func = override_settings(TEMPLATES=[{
+    return override_settings(TEMPLATES=[{
         'BACKEND': 'django.template.backends.django.DjangoTemplates',
         'APP_DIRS': True,
     }, {
         'BACKEND': 'django.template.backends.jinja2.Jinja2',
         'APP_DIRS': True,
         'OPTIONS': {'keep_trailing_newline': True},
     }])(test_func)
### 2133f3157e  2015-01-26  Fixed #24168 -- Allowed selecting a template engine in a few APIs.

diff --git a/django/test/utils.py b/django/test/utils.py
--- a/django/test/utils.py
+++ b/django/test/utils.py
@@ -576,0 +589,8 @@
+    test_func = override_settings(TEMPLATES=[{
+        'BACKEND': 'django.template.backends.django.DjangoTemplates',
+        'APP_DIRS': True,
+    }, {
+        'BACKEND': 'django.template.backends.jinja2.Jinja2',
+        'APP_DIRS': True,
+        'OPTIONS': {'keep_trailing_newline': True},
+    }])(test_func)

````

</details>

## T034  redis  `src/t_stream.c:5673`

```
    5669     addReplyLongLong(c,raxSize(s->rax));
    5670     addReplyBulkCString(c,"radix-tree-nodes");
    5671     addReplyLongLong(c,s->rax->numnodes);
    5672     addReplyBulkCString(c,"last-generated-id");
>>  5673     addReplyStreamID(c,&s->last_id);
    5674     addReplyBulkCString(c,"max-deleted-entry-id");
    5675     addReplyStreamID(c,&s->max_deleted_entry_id);
    5676     addReplyBulkCString(c,"entries-added");
    5677     addReplyLongLong(c,s->entries_added);
```

**Candidate commits, oldest first:**

- `b4ba5ac840`  2018-07-16  Streams: show last id for streams and groups
- `1e2aee3919`  2020-04-28  Extend XINFO STREAM output

<details><summary>Line history</summary>

````diff
### 1e2aee391  2020-04-22  Extend XINFO STREAM output

diff --git a/src/t_stream.c b/src/t_stream.c
--- a/src/t_stream.c
+++ b/src/t_stream.c
@@ -2478,0 +2522,1 @@
+    addReplyStreamID(c,&s->last_id);

````

</details>

## T035  redis  `src/defrag.c:216`

```
     212 void *activeDefragAlloc(void *ptr) {
     213     void *newptr = activeDefragAllocWithoutFree(ptr);
     214     if (newptr)
     215         activeDefragFree(ptr);
>>   216     return newptr;
     217 }
     218 
     219 void *activeDefragAllocRaw(size_t size) {
     220     return zmalloc(size);
```

**Candidate commits, oldest first:**

- `d649637ebd`  2025-09-08  Fix defrag issues for stream defrag and HFE (#14323)
- `60adba48aa`  2025-09-10  Introduce DEBUG_DEFRAG compilation option to allow run test with activedefrag when allocat

<details><summary>Line history</summary>

````diff
### 60adba48a  2025-09-10  Introduce DEBUG_DEFRAG compilation option to allow run test with activedefrag when allocator is not jemalloc (#14326)

diff --git a/src/defrag.c b/src/defrag.c
--- a/src/defrag.c
+++ b/src/defrag.c
@@ -191,0 +211,1 @@
+    return newptr;

````

</details>

## T036  django  `django/db/migrations/state.py:409`

```
     405         related_models.update(direct_related_models)
     406         for rel_app_label, rel_model_name in direct_related_models:
     407             try:
     408                 rel_model = self.apps.get_model(rel_app_label, rel_model_name)
>>   409             except LookupError:
     410                 pass
     411             else:
     412                 if delay:
     413                     related_models.update(get_related_models_tuples(rel_model))
```

**Candidate commits, oldest first:**

- `1aa3e09c20`  2015-01-02  Fixed #23745 -- Reused states as much as possible in migrations
- `b93690c465`  2015-04-21  Fixed #24573 -- Considered new related models for reloading

<details><summary>Line history</summary>

````diff
### 1aa3e09c20  2014-11-05  Fixed #23745 -- Reused states as much as possible in migrations

diff --git a/django/db/migrations/state.py b/django/db/migrations/state.py
--- a/django/db/migrations/state.py
+++ b/django/db/migrations/state.py
@@ -33,2 +56,1 @@
-    def add_model_state(self, model_state):
-        self.models[(model_state.app_label, model_state.name.lower())] = model_state
+            except LookupError:
### 38a8cf1cdc  2013-05-18  Fix state tests a little

diff --git a/django/db/migrations/state.py b/django/db/migrations/state.py
--- a/django/db/migrations/state.py
+++ b/django/db/migrations/state.py
@@ -17,0 +17,2 @@
+    def add_model_state(self, model_state):
+        self.models[(model_state.app_label, model_state.name.lower())] = model_state

````

</details>

## T037  redis  `src/t_list.c:1307`

```
    1303  *
    1304  * When count is -1, a reply of a single bulk-string will be used.
    1305  * When count > 0, an array reply will be used. */
    1306 void blockingPopGenericCommand(client *c, robj **keys, int numkeys, int where, int timeout_idx, long count) {
>>  1307     robj *o;
    1308     robj *key;
    1309     uint64_t timeout;
    1310     int j;
    1311 
```

**Candidate commits, oldest first:**

- `e2641e09cc`  2010-07-01  redis.c split into many different C files.

<details><summary>Line history</summary>

````diff
### e2641e09c  2010-06-22  redis.c split into many different C files.

diff --git a/src/t_list.c b/src/t_list.c
--- /dev/null
+++ b/src/t_list.c
@@ -0,0 +775,1 @@
+    robj *o;

````

</details>

## T038  django  `django/db/backends/mysql/features.py:16`

```
      12     has_select_for_update = True
      13     has_select_for_update_nowait = True
      14     has_select_for_update_skip_locked = True
      15     supports_forward_references = False
>>    16     supports_regex_backreferencing = False
      17     supports_date_lookup_using_string = False
      18     supports_timezones = False
      19     requires_explicit_null_ordering_when_grouping = True
      20     atomic_transactions = False
```

**Candidate commits, oldest first:**

- `121d2e3678`  2010-10-11  Fixed #12991 -- Added unittest2 support. Thanks to PaulM for the draft patch, and to Luke,
- `28308078f3`  2015-01-14  Fixed #22603 -- Reorganized classes in django.db.backends.

<details><summary>Line history</summary>

````diff
### 28308078f3  2015-01-12  Fixed #22603 -- Reorganized classes in django.db.backends.

diff --git a/django/db/backends/mysql/features.py b/django/db/backends/mysql/features.py
--- /dev/null
+++ b/django/db/backends/mysql/features.py
@@ -0,0 +22,1 @@
+    supports_regex_backreferencing = False

````

</details>

## T039  redis  `src/debug.c:1958`

```
    1954         (unsigned long) uc->uc_mcontext.__gregs[21],
    1955         (unsigned long) uc->uc_mcontext.__gregs[22],
    1956         (unsigned long) uc->uc_mcontext.__gregs[23],
    1957         (unsigned long) uc->uc_mcontext.__gregs[24],
>>  1958         (unsigned long) uc->uc_mcontext.__gregs[25],
    1959         (unsigned long) uc->uc_mcontext.__gregs[26],
    1960         (unsigned long) uc->uc_mcontext.__gregs[27],
    1961         (unsigned long) uc->uc_mcontext.__gregs[28],
    1962         (unsigned long) uc->uc_mcontext.__gregs[29],
```

**Candidate commits, oldest first:**

- `ef4bb4e374`  2023-06-27  Add RISC-V debug support (#12349)

<details><summary>Line history</summary>

````diff
### ef4bb4e37  2023-06-27  Add RISC-V debug support (#12349)

diff --git a/src/debug.c b/src/debug.c
--- a/src/debug.c
+++ b/src/debug.c
@@ -1455,0 +1491,1 @@
+        (unsigned long) uc->uc_mcontext.__gregs[25],

````

</details>

## T040  django  `django/contrib/auth/migrations/0001_initial.py:132`

```
     128                     ),
     129                 ),
     130                 (
     131                     "last_name",
>>   132                     models.CharField(
     133                         max_length=30, verbose_name="last name", blank=True
     134                     ),
     135                 ),
     136                 (
```

**Candidate commits, oldest first:**

- `b341f33697`  2014-06-16  Added database migration for contrib.auth.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/contrib/auth/migrations/0001_initial.py b/django/contrib/auth/migrations/0001_initial.py
--- a/django/contrib/auth/migrations/0001_initial.py
+++ b/django/contrib/auth/migrations/0001_initial.py
@@ -54,39 +127,1 @@
-                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
-                ('password', models.CharField(max_length=128, verbose_name='password')),
-                ('last_login', models.DateTimeField(default=timezone.now, verbose_name='last login')),
-                ('is_superuser', models.BooleanField(
-                    default=False,
-                    help_text='Designates that this user has all permissions without explicitly assigning them.',
-                    verbose_name='superuser status'
-                )),
-                ('username', models.CharField(
-                    help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True,
-                    max_length=30, verbose_name='username',
-                    validators=[validators.UnicodeUsernameValidator()],
-                )),
-                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
-                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
-                ('email', models.EmailField(max_length=75, verbose_name='email address', blank=True)),
-                ('is_staff', models.BooleanField(
-                    default=False, help_text='Designates whether the user can log into this admin site.',
-                    verbose_name='staff status'
-                )),
-                ('is_active', models.BooleanField(
-                    default=True, verbose_name='active', help_text=(
-                        'Designates whether this user should be treated as active. Unselect this instead of deleting '
-                        'accounts.'
-                    )
-                )),
-                ('date_joined', models.DateTimeField(default=timezone.now, verbose_name='date joined')),
-                ('groups', models.ManyToManyField(
-                    to='auth.Group', verbose_name='groups', blank=True, related_name='user_set',
-                    related_query_name='user', help_text=(
-                        'The groups this user belongs to. A user will get all permissions granted to each of their '
-                        'groups.'
-                    )
-                )),
-                ('user_permissions', models.ManyToManyField(
-                    to='auth.Permission', verbose_name='user permissions', blank=True,
-                    help_text='Specific permissions for this user.', related_name='user_set',
-                    related_query_name='user')
-                 ),
+                    models.CharField(
### c716fe8782  2016-12-01  Refs #23919 -- Removed six.PY2/PY3 usage

diff --git a/django/contrib/auth/migrations/0001_initial.py b/django/contrib/auth/migrations/0001_initial.py
--- a/django/contrib/auth/migrations/0001_initial.py
+++ b/django/contrib/auth/migrations/0001_initial.py
@@ -55,41 +55,39 @@
                 ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                 ('password', models.CharField(max_length=128, verbose_name='password')),
                 ('last_login', models.Dat
... (cut, so use `git log -L` for the rest)
````

</details>

## T041  django  `django/db/models/fields/files.py:207`

```
     203         # If this value is a DatabaseDefault, initialize the attribute class
     204         # for this field with its db_default value.
     205         elif isinstance(file, DatabaseDefault):
     206             attr = self.field.attr_class(instance, self.field, self.field.db_default)
>>   207             instance.__dict__[self.field.attname] = attr
     208 
     209         # Other types of files may be assigned as well, but they need to have
     210         # the FieldFile interface added to them. Thus, we wrap any other type
     211         # of File inside a FieldFile (well, the field's attr_class, which is
```

**Candidate commits, oldest first:**

- `a93425a37f`  2020-06-30  Fixed #31701 -- Made FileDescriptor subclass DeferredAttribute.
- `8deb6bb1fc`  2024-08-05  Fixed #35657 -- Made FileField handle db_default values.

<details><summary>Line history</summary>

````diff
### 8deb6bb1fc  2024-08-05  Fixed #35657 -- Made FileField handle db_default values.

diff --git a/django/db/models/fields/files.py b/django/db/models/fields/files.py
--- a/django/db/models/fields/files.py
+++ b/django/db/models/fields/files.py
@@ -200,0 +205,1 @@
+            instance.__dict__[self.field.attname] = attr

````

</details>

## T042  redis  `src/endianconv.c:81`

```
      77 }
      78 
      79 uint64_t intrev64(uint64_t v) {
      80     memrev64(&v);
>>    81     return v;
      82 }
      83 
      84 #ifdef REDIS_TEST
      85 #include <stdio.h>
```

**Candidate commits, oldest first:**

- `5653847714`  2012-02-08  ziplist.c fixes for bigendian
- `7a3e372025`  2012-02-14  endian.c/h -> endianconv.c/h to avoid issues with broken libraries search paths.

<details><summary>Line history</summary>

````diff
### 7a3e37202  2012-02-14  endian.c/h -> endianconv.c/h to avoid issues with broken libraries search paths.

diff --git a/src/endianconv.c b/src/endianconv.c
--- /dev/null
+++ b/src/endianconv.c
@@ -0,0 +101,1 @@
+    return v;

````

</details>

## T043  redis  `src/pubsub.c:502`

```
     498          * pubsubStampCurrentUser). dictAddRaw leaves the value uninitialized
     499          * and flat-lazy reads it, hence the explicit NULL. Content-equal keys
     500          * hash identically, so the in-place key swap is safe. */
     501         dictSetKey(type.clientPubSubChannels(c), client_de, channel);
>>   502         dictSetVal(type.clientPubSubChannels(c), client_de, NULL);
     503         incrRefCount(channel);
     504         c->pubsub_names_mem += getStringObjectMemory(channel);
     505     }
     506     /* Notify the client */
```

**Candidate commits, oldest first:**

- `43c88eb451`  2026-08-05  Track Pub/Sub subscription provenance across AUTH changes (#15468)

<details><summary>Line history</summary>

````diff
### 43c88eb45  2026-08-05  Track Pub/Sub subscription provenance across AUTH changes (#15468)

diff --git a/src/pubsub.c b/src/pubsub.c
--- a/src/pubsub.c
+++ b/src/pubsub.c
@@ -273,1 +501,1 @@
-        dictSetKeyAtLink(type.clientPubSubChannels(c), channel, &bucket, 1);
+        dictSetVal(type.clientPubSubChannels(c), client_de, NULL);
### e1789e436  2025-05-12  keyspace - Unify key and value & use dict no_value=1 (#13806)

diff --git a/src/pubsub.c b/src/pubsub.c
--- a/src/pubsub.c
+++ b/src/pubsub.c
@@ -266,1 +267,1 @@
-        serverAssert(dictInsertAtPosition(type.clientPubSubChannels(c), channel, position));
+        dictSetKeyAtLink(type.clientPubSubChannels(c), channel, &bucket, 1);
### ad1273033  2024-03-04  Implement defragmentation for pubsub kvstore (#13058)

diff --git a/src/pubsub.c b/src/pubsub.c
--- a/src/pubsub.c
+++ b/src/pubsub.c
@@ -285,0 +286,1 @@
+        serverAssert(dictInsertAtPosition(type.clientPubSubChannels(c), channel, position));

````

</details>

## T044  django  `django/utils/crypto.py:23`

```
      19     pass
      20 
      21 
      22 # RemovedInDjango2028Warning: algorithm="sha256"
>>    23 def salted_hmac(key_salt, value, secret=None, *, algorithm=None):
      24     """
      25     Return the HMAC of 'value', using a key generated from key_salt and a
      26     secret (which defaults to settings.SECRET_KEY). Default algorithm is SHA1,
      27     but any algorithm name supported by hashlib can be passed.
```

**Candidate commits, oldest first:**

- `45c7f427ce`  2010-10-14  Fixed #14445 - Use HMAC and constant-time comparison functions where needed.
- `50cf183d21`  2020-01-27  Refs #27468 -- Added algorithm parameter to django.utils.crypto.salted_hmac().
- `0f4fff79d3`  2026-05-04  Fixed #37078 -- Deprecated SHA-1 default for salted_hmac() and base64_hmac() algorithm.

<details><summary>Line history</summary>

````diff
### 0f4fff79d3  2026-04-30  Fixed #37078 -- Deprecated SHA-1 default for salted_hmac() and base64_hmac() algorithm.

diff --git a/django/utils/crypto.py b/django/utils/crypto.py
--- a/django/utils/crypto.py
+++ b/django/utils/crypto.py
@@ -19,1 +22,1 @@
-def salted_hmac(key_salt, value, secret=None, *, algorithm="sha1"):
+def salted_hmac(key_salt, value, secret=None, *, algorithm=None):
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/utils/crypto.py b/django/utils/crypto.py
--- a/django/utils/crypto.py
+++ b/django/utils/crypto.py
@@ -18,1 +19,1 @@
-def salted_hmac(key_salt, value, secret=None, *, algorithm='sha1'):
+def salted_hmac(key_salt, value, secret=None, *, algorithm="sha1"):
### 50cf183d21  2020-01-08  Refs #27468 -- Added algorithm parameter to django.utils.crypto.salted_hmac().

diff --git a/django/utils/crypto.py b/django/utils/crypto.py
--- a/django/utils/crypto.py
+++ b/django/utils/crypto.py
@@ -12,1 +17,1 @@
-def salted_hmac(key_salt, value, secret=None):
+def salted_hmac(key_salt, value, secret=None, *, algorithm='sha1'):
### 45c7f427ce  2010-10-14  Fixed #14445 - Use HMAC and constant-time comparison functions where needed.

diff --git a/django/utils/crypto.py b/django/utils/crypto.py
--- /dev/null
+++ b/django/utils/crypto.py
@@ -0,0 +10,1 @@
+def salted_hmac(key_salt, value, secret=None):

````

</details>

## T045  django  `django/contrib/admin/options.py:2706`

```
    2702     from ``model`` to its parent. This is required if ``model`` has more than
    2703     one ``ForeignKey`` to its parent.
    2704     """
    2705 
>>  2706     model = None
    2707     fk_name = None
    2708     formset = BaseInlineFormSet
    2709     extra = 3
    2710     min_num = None
```

**Candidate commits, oldest first:**

- `a19ed8aea3`  2008-07-18  Merged the newforms-admin branch into trunk.

<details><summary>Line history</summary>

````diff
### a19ed8aea3  2008-07-18  Merged the newforms-admin branch into trunk.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- /dev/null
+++ b/django/contrib/admin/options.py
@@ -0,0 +703,1 @@
+    model = None

````

</details>

## T046  django  `django/contrib/contenttypes/fields.py:852`

```
     848             return super().using(db).get_or_create(**kwargs)
     849 
     850         get_or_create.alters_data = True
     851 
>>   852         async def aget_or_create(self, **kwargs):
     853             return await sync_to_async(self.get_or_create)(**kwargs)
     854 
     855         aget_or_create.alters_data = True
     856 
```

**Candidate commits, oldest first:**

- `7b94847e38`  2022-11-08  Fixed #34139 -- Fixed acreate(), aget_or_create(), and aupdate_or_create() methods for rel

<details><summary>Line history</summary>

````diff
### 7b94847e38  2022-11-04  Fixed #34139 -- Fixed acreate(), aget_or_create(), and aupdate_or_create() methods for related managers.

diff --git a/django/contrib/contenttypes/fields.py b/django/contrib/contenttypes/fields.py
--- a/django/contrib/contenttypes/fields.py
+++ b/django/contrib/contenttypes/fields.py
@@ -758,0 +765,1 @@
+        async def aget_or_create(self, **kwargs):

````

</details>

## T047  django  `django/db/backends/mysql/features.py:13`

```
       9     related_fields_match_type = True
      10     # MySQL doesn't support sliced subqueries with IN/ALL/ANY/SOME.
      11     allow_sliced_subqueries_with_in = False
      12     has_select_for_update = True
>>    13     has_select_for_update_nowait = True
      14     has_select_for_update_skip_locked = True
      15     supports_forward_references = False
      16     supports_regex_backreferencing = False
      17     supports_date_lookup_using_string = False
```

**Candidate commits, oldest first:**

- `b719688b21`  2023-08-03  Fixed #34761 -- Dropped support for MySQL < 8.0.11.

<details><summary>Line history</summary>

````diff
### b719688b21  2023-08-03  Fixed #34761 -- Dropped support for MySQL < 8.0.11.

diff --git a/django/db/backends/mysql/features.py b/django/db/backends/mysql/features.py
--- a/django/db/backends/mysql/features.py
+++ b/django/db/backends/mysql/features.py
@@ -14,0 +14,1 @@
+    has_select_for_update_nowait = True

````

</details>

## T048  django  `django/db/models/functions/window.py:81`

```
      77 
      78     def __init__(self, expression, nth=1, **extra):
      79         if expression is None:
      80             raise ValueError(
>>    81                 "%s requires a non-null source expression." % self.__class__.__name__
      82             )
      83         if nth is None or nth <= 0:
      84             raise ValueError(
      85                 "%s requires a positive integer as for nth." % self.__class__.__name__
```

**Candidate commits, oldest first:**

- `d549b88050`  2017-09-18  Fixed #26608 -- Added support for window expressions (OVER clause).
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/db/models/functions/window.py b/django/db/models/functions/window.py
--- a/django/db/models/functions/window.py
+++ b/django/db/models/functions/window.py
@@ -72,1 +81,1 @@
-            raise ValueError('%s requires a non-null source expression.' % self.__class__.__name__)
+                "%s requires a non-null source expression." % self.__class__.__name__
### d549b88050  2017-09-18  Fixed #26608 -- Added support for window expressions (OVER clause).

diff --git a/django/db/models/functions/window.py b/django/db/models/functions/window.py
--- /dev/null
+++ b/django/db/models/functions/window.py
@@ -0,0 +78,1 @@
+            raise ValueError('%s requires a non-null source expression.' % self.__class__.__name__)

````

</details>

## T049  django  `django/test/client.py:887`

```
     883     def force_login(self, user, backend=None):
     884         if backend is None:
     885             backend = self._get_backend()
     886         user.backend = backend
>>   887         self._login(user, backend)
     888 
     889     async def aforce_login(self, user, backend=None):
     890         if backend is None:
     891             backend = self._get_backend()
```

**Candidate commits, oldest first:**

- `b643386668`  2016-01-07  Fixed #24855 -- Allowed using contrib.auth.login() without credentials.
- `fc0fa72ff4`  2020-03-18  Fixed #31224 -- Added support for asynchronous views and middleware.
- `5e98959d92`  2023-06-27  Fixed #34391 -- Added async-compatible interface to auth functions and related methods tes

<details><summary>Line history</summary>

````diff
### fc0fa72ff4  2020-02-12  Fixed #31224 -- Added support for asynchronous views and middleware.

diff --git a/django/test/client.py b/django/test/client.py
--- a/django/test/client.py
+++ b/django/test/client.py
@@ -424,1 +610,1 @@
-class Client(RequestFactory):
+        self._login(user, backend)
### eec45e8b71  2010-10-12  Fixed #9002 -- Added a RequestFactory. This allows you to create request instances so you can unit test views as standalone functions. Thanks to Simon Willison for the suggestion and snippet on which this patch was originally based.

diff --git a/django/test/client.py b/django/test/client.py
--- a/django/test/client.py
+++ b/django/test/client.py
@@ -159,1 +317,1 @@
-class Client(object):
+class Client(RequestFactory):
### eeb230aa1c  2008-09-17  Fixed #9117: Made the test client a new-style class. Thanks to Jan Oberst for the report.

diff --git a/django/test/client.py b/django/test/client.py
--- a/django/test/client.py
+++ b/django/test/client.py
@@ -137,2 +138,1 @@
-    
-class Client:
+class Client(object):
### 9dabd1f8ff  2008-07-07  Fixed #7651: uploading multiple files with the same name now work. Also, in order to test the problem the test client now handles uploading multiple files at once. Patch from Mike Axiak.

diff --git a/django/test/client.py b/django/test/client.py
--- a/django/test/client.py
+++ b/django/test/client.py
@@ -126,1 +138,2 @@
+    
 class Client:
### 7dce86ce02  2006-08-27  Refs #2333 - Added test framework. This includes doctest and unittest finders, Django-specific doctest and unittest wrappers, and a pseudo-client that can be used to stimulate and test views.

diff --git a/django/test/client.py b/django/test/client.py
--- /dev/null
+++ b/django/test/client.py
@@ -0,0 +80,1 @@
+class Client:

````

</details>

## T050  django  `django/contrib/postgres/fields/ranges.py:250`

```
     246         sql, params = super().as_postgresql(compiler, connection)
     247         # Cast the rhs if needed.
     248         cast_sql = ""
     249         if (
>>   250             isinstance(self.rhs, models.Expression)
     251             and self.rhs._output_field_or_none
     252             and
     253             # Skip cast if rhs has a matching range type.
     254             not isinstance(
```

**Candidate commits, oldest first:**

- `6b048b364c`  2017-02-07  Fixed #26903 -- Fixed __contains lookup for Date/DateTimeRangeField.
- `7991111af1`  2019-07-10  Fixed #30621 -- Fixed crash of __contains lookup for Date/DateTimeRangeField when the righ
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/contrib/postgres/fields/ranges.py b/django/contrib/postgres/fields/ranges.py
--- a/django/contrib/postgres/fields/ranges.py
+++ b/django/contrib/postgres/fields/ranges.py
@@ -220,2 +229,1 @@
-            isinstance(self.rhs, models.Expression) and
-            self.rhs._output_field_or_none and
+            isinstance(self.rhs, models.Expression)
### 7991111af1  2019-07-10  Fixed #30621 -- Fixed crash of __contains lookup for Date/DateTimeRangeField when the right hand side is the same type.

diff --git a/django/contrib/postgres/fields/ranges.py b/django/contrib/postgres/fields/ranges.py
--- a/django/contrib/postgres/fields/ranges.py
+++ b/django/contrib/postgres/fields/ranges.py
@@ -173,1 +174,2 @@
-        if isinstance(self.rhs, models.Expression) and self.rhs._output_field_or_none:
+            isinstance(self.rhs, models.Expression) and
+            self.rhs._output_field_or_none and
### 6b048b364c  2017-02-07  Fixed #26903 -- Fixed __contains lookup for Date/DateTimeRangeField.

diff --git a/django/contrib/postgres/fields/ranges.py b/django/contrib/postgres/fields/ranges.py
--- a/django/contrib/postgres/fields/ranges.py
+++ b/django/contrib/postgres/fields/ranges.py
@@ -134,0 +156,1 @@
+        if isinstance(self.rhs, models.Expression) and self.rhs._output_field_or_none:

````

</details>

## T051  django  `django/utils/dateparse.py:101`

```
      97         if match := time_re.match(value):
      98             kw = match.groupdict()
      99             kw["microsecond"] = kw["microsecond"] and kw["microsecond"].ljust(6, "0")
     100             kw = {k: int(v) for k, v in kw.items() if v is not None}
>>   101             return datetime.time(**kw)
     102 
     103 
     104 def parse_datetime(value):
     105     """Parse a string and return a datetime.datetime.
```

**Candidate commits, oldest first:**

- `9b1cb755a2`  2011-11-18  Added support for time zones. Thanks Luke Plant for the review. Fixed #2626.
- `f35ab74752`  2021-07-06  Fixed #32892 -- Optimized django.utils.dateparse functions by using fromisoformat().

<details><summary>Line history</summary>

````diff
### f35ab74752  2021-07-01  Fixed #32892 -- Optimized django.utils.dateparse functions by using fromisoformat().

diff --git a/django/utils/dateparse.py b/django/utils/dateparse.py
--- a/django/utils/dateparse.py
+++ b/django/utils/dateparse.py
@@ -90,6 +103,1 @@
-    match = time_re.match(value)
-    if match:
-        kw = match.groupdict()
-        kw['microsecond'] = kw['microsecond'] and kw['microsecond'].ljust(6, '0')
-        kw = {k: int(v) for k, v in kw.items() if v is not None}
-        return datetime.time(**kw)
+            return datetime.time(**kw)
### d7b2aa24f7  2018-01-03  Fixed #28982 -- Simplified code with and/or.

diff --git a/django/utils/dateparse.py b/django/utils/dateparse.py
--- a/django/utils/dateparse.py
+++ b/django/utils/dateparse.py
@@ -89,7 +89,6 @@
     match = time_re.match(value)
     if match:
         kw = match.groupdict()
-        if kw['microsecond']:
-            kw['microsecond'] = kw['microsecond'].ljust(6, '0')
+        kw['microsecond'] = kw['microsecond'] and kw['microsecond'].ljust(6, '0')
         kw = {k: int(v) for k, v in kw.items() if v is not None}
         return datetime.time(**kw)
### 2b281cc35e  2017-01-07  Refs #23919 -- Removed most of remaining six usage

diff --git a/django/utils/dateparse.py b/django/utils/dateparse.py
--- a/django/utils/dateparse.py
+++ b/django/utils/dateparse.py
@@ -76,7 +75,7 @@
     match = time_re.match(value)
     if match:
         kw = match.groupdict()
         if kw['microsecond']:
             kw['microsecond'] = kw['microsecond'].ljust(6, '0')
-        kw = {k: int(v) for k, v in six.iteritems(kw) if v is not None}
+        kw = {k: int(v) for k, v in kw.items() if v is not None}
         return datetime.time(**kw)
### 4468c08d70  2014-12-06  Fixed #23968 -- Replaced list comprehension with generators and dict comprehension

diff --git a/django/utils/dateparse.py b/django/utils/dateparse.py
--- a/django/utils/dateparse.py
+++ b/django/utils/dateparse.py
@@ -52,7 +52,7 @@
     match = time_re.match(value)
     if match:
         kw = match.groupdict()
         if kw['microsecond']:
             kw['microsecond'] = kw['microsecond'].ljust(6, '0')
-        kw = dict((k, int(v)) for k, v in six.iteritems(kw) if v is not None)
+        kw = {k: int(v) for k, v in six.iteritems(kw) if v is not None}
         return datetime.time(**kw)
### ee191715ea  2012-07-20  [py3] Fixed access to dict keys/values/items.

diff --git a/django/utils/dateparse.py b/django/utils/dateparse.py
--- a/django/utils/dateparse.py
+++ b/django/utils/dateparse.py
@@ -51,7 +52,7 @@
     match = time_re.match(value)
     if match:
         kw = match.groupdict()
         if kw['microsecond']:
             kw['microsecond'] = kw['microsecond'].ljust(6, '0')
-        kw = dict((k, int(v)) for k, v in kw.iteritems() if v is not None)
+        kw = dict((k, int(v)) for k, v in six.iteritems(kw) if v is not None)
         return datetime.time(**kw)
### 9b1cb755a2  2011-11-18  Added support for time zones. Thanks Luke Plant for the review. Fixed #2626.

diff --git a/django/utils/dateparse.py b/django/utils/dateparse.py
--- /dev/null
+++ b/django/utils/dateparse.py
@@ -0,0 +58,7 @@
+    match = time_re.match(value)
+    if match:
+        kw = match.groupdict()
+        if kw['microsecond']:
+            kw['microsecond'] = kw['microsecond'].ljust(6, '0')
+        kw = dict((k, int(v)) for k, v in kw.iteritems() if v is not None)
+        return datetime.time(**kw)

````

</details>

## T052  redis  `src/fwtree.c:92`

```
      88         /* When the target index is greater than 'current' node value the we will update
      89          * the target and search in the 'current' node tree. */
      90         if (target > ft->tree[current]) {
      91             target -= ft->tree[current];
>>    92             result = current;
      93         }
      94     }
      95     /* Adjust the result to get the correct index:
      96      * 1. result += 1;
```

**Candidate commits, oldest first:**

- `9b63e99d05`  2025-09-11  Refactor HFE: Introduce Per-Slot Expiration Store (estore) (#14294)

<details><summary>Line history</summary>

````diff
### 9b63e99d0  2025-09-11  Refactor HFE: Introduce Per-Slot Expiration Store (estore) (#14294)

diff --git a/src/fwtree.c b/src/fwtree.c
--- /dev/null
+++ b/src/fwtree.c
@@ -0,0 +93,1 @@
+            result = current;

````

</details>

## T053  django  `django/db/models/fields/json.py:530`

```
     526         key_transforms = [self.key_name]
     527         previous = self.lhs
     528         while isinstance(previous, KeyTransform):
     529             key_transforms.insert(0, previous.key_name)
>>   530             previous = previous.lhs
     531         lhs, params = compiler.compile(previous)
     532         if connection.vendor == "oracle":
     533             # Escape string-formatting.
     534             key_transforms = [key.replace("%", "%%") for key in key_transforms]
```

**Candidate commits, oldest first:**

- `33ea472f69`  2015-05-30  Fixed #24604 -- Added JSONField to contrib.postgres.
- `6789ded0a6`  2020-05-08  Fixed #12990, Refs #27694 -- Added JSONField model field.

<details><summary>Line history</summary>

````diff
### 6789ded0a6  2019-06-09  Fixed #12990, Refs #27694 -- Added JSONField model field.

diff --git a/django/db/models/fields/json.py b/django/db/models/fields/json.py
--- /dev/null
+++ b/django/db/models/fields/json.py
@@ -0,0 +302,1 @@
+            previous = previous.lhs

````

</details>

## T054  django  `django/db/backends/sqlite3/base.py:280`

```
     276         with self.cursor() as cursor:
     277             if table_names is None:
     278                 violations = cursor.execute("PRAGMA foreign_key_check").fetchall()
     279             else:
>>   280                 violations = chain.from_iterable(
     281                     cursor.execute(
     282                         "PRAGMA foreign_key_check(%s)" % self.ops.quote_name(table_name)
     283                     ).fetchall()
     284                     for table_name in table_names
```

**Candidate commits, oldest first:**

- `a939d630a4`  2018-12-17  Refs #29928 -- Implemented fast constraint checking on SQLite 3.20+.
- `95a101a690`  2022-12-08  Fixed #34201 -- Bumped minimum supported SQLite to 3.21.0.

<details><summary>Line history</summary>

````diff
### 95a101a690  2022-12-08  Fixed #34201 -- Bumped minimum supported SQLite to 3.21.0.

diff --git a/django/db/backends/sqlite3/base.py b/django/db/backends/sqlite3/base.py
--- a/django/db/backends/sqlite3/base.py
+++ b/django/db/backends/sqlite3/base.py
@@ -242,62 +246,1 @@
-        if self.features.supports_pragma_foreign_key_check:
-            with self.cursor() as cursor:
-                if table_names is None:
-                    violations = cursor.execute("PRAGMA foreign_key_check").fetchall()
-                else:
-                    violations = chain.from_iterable(
-                        cursor.execute(
-                            "PRAGMA foreign_key_check(%s)"
-                            % self.ops.quote_name(table_name)
-                        ).fetchall()
-                        for table_name in table_names
-                    )
-                # See https://www.sqlite.org/pragma.html#pragma_foreign_key_check
-                for (
-                    table_name,
-                    rowid,
-                    referenced_table_name,
-                    foreign_key_index,
-                ) in violations:
-                    foreign_key = cursor.execute(
-                        "PRAGMA foreign_key_list(%s)" % self.ops.quote_name(table_name)
-                    ).fetchall()[foreign_key_index]
-                    column_name, referenced_column_name = foreign_key[3:5]
-                    primary_key_column_name = self.introspection.get_primary_key_column(
-                        cursor, table_name
-                    )
-                    primary_key_value, bad_value = cursor.execute(
-                        "SELECT %s, %s FROM %s WHERE rowid = %%s"
-                        % (
-                            self.ops.quote_name(primary_key_column_name),
-                            self.ops.quote_name(column_name),
-                            self.ops.quote_name(table_name),
-                        ),
-                        (rowid,),
-                    ).fetchone()
-                    raise IntegrityError(
-                        "The row in table '%s' with primary key '%s' has an "
-                        "invalid foreign key: %s.%s contains a value '%s' that "
-                        "does not have a corresponding value in %s.%s."
-                        % (
-                            table_name,
-                            primary_key_value,
-                            table_name,
-                            column_name,
-                            bad_value,
-                            referenced_table_name,
-                            referenced_column_name,
-                        )
-                    )
-        else:
-            with self.cursor() as cursor:
-                if table_names is None:
-                    table_names = self.introspection.table_names(cursor)
-                for table_name in table_names:
-                    primary_key_column_name = self.introspection.get_primary_key_column(
-                        cursor, table_name
-                    )
-                    if not primary_key_column_name:
-                        continue
-                    relations = self.introspection.get_relations(cursor, table_name)
-                    for column_name, (
-                        referenced_column_name,
+                violations = chain.from_iterable(
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/db/b
... (cut, so use `git log -L` for the rest)
````

</details>

## T055  django  `django/contrib/postgres/fields/ranges.py:196`

```
     192     range_type = NumericRange
     193     form_field = forms.DecimalRangeField
     194 
     195     def db_type(self, connection):
>>   196         return "numrange"
     197 
     198 
     199 class DateTimeRangeField(ContinuousRangeField):
     200     base_field = models.DateTimeField
```

**Candidate commits, oldest first:**

- `6de7f9ec60`  2018-10-02  Fixed #29598 -- Deprecated FloatRangeField in favor of DecimalRangeField.
- `9c19aff7c7`  2022-02-07  Refs #33476 -- Reformatted code with Black.

<details><summary>Line history</summary>

````diff
### 9c19aff7c7  2022-02-03  Refs #33476 -- Reformatted code with Black.

diff --git a/django/contrib/postgres/fields/ranges.py b/django/contrib/postgres/fields/ranges.py
--- a/django/contrib/postgres/fields/ranges.py
+++ b/django/contrib/postgres/fields/ranges.py
@@ -174,1 +182,1 @@
-        return 'numrange'
+        return "numrange"
### 6de7f9ec60  2018-10-03  Fixed #29598 -- Deprecated FloatRangeField in favor of DecimalRangeField.

diff --git a/django/contrib/postgres/fields/ranges.py b/django/contrib/postgres/fields/ranges.py
--- a/django/contrib/postgres/fields/ranges.py
+++ b/django/contrib/postgres/fields/ranges.py
@@ -103,0 +110,1 @@
+        return 'numrange'

````

</details>

## T056  django  `django/utils/lorem_ipsum.py:152`

```
     148     "rerum",
     149     "error",
     150     "minus",
     151     "eius",
>>   152     "ab",
     153     "ad",
     154     "nemo",
     155     "fugit",
     156     "officia",
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
@@ -18,29 +152,1 @@
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
+    "ab",
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
-        'quo', 'aliquam', 'saepe', 'culpa', 'libero', 'ipsa', 'dicta',
... (cut, so use `git log -L` for the rest)
````

</details>

## T057  redis  `src/module.c:15686`

```
   15682  * used.
   15683  */
   15684 int *RM_GetCommandKeysWithFlags(RedisModuleCtx *ctx, RedisModuleString **argv, int argc, int *num_keys, int **out_flags) {
   15685     UNUSED(ctx);
>> 15686     struct redisCommand *cmd;
   15687     int *res = NULL;
   15688 
   15689     /* Find command */
   15690     if ((cmd = lookupCommand(argv,argc)) == NULL) {
```

**Candidate commits, oldest first:**

- `6dead2cff5`  2016-05-10  Modules: first preview 31 March 2016.
- `7d117d7591`  2020-10-11  Modules: add RM_GetCommandKeys().

<details><summary>Line history</summary>

````diff
### 7d117d759  2020-10-05  Modules: add RM_GetCommandKeys().

diff --git a/src/module.c b/src/module.c
--- a/src/module.c
+++ b/src/module.c
@@ -7890,0 +7907,1 @@
+    struct redisCommand *cmd;

````

</details>

## T058  django  `django/core/management/commands/sqlmigrate.py:69`

```
      65             raise CommandError(
      66                 "Cannot find a migration matching '%s' from app '%s'. Is it in "
      67                 "INSTALLED_APPS?" % (migration_name, app_label)
      68             )
>>    69         target = (app_label, migration.name)
      70 
      71         # Show begin/end around output for atomic migrations, if the database
      72         # supports transactional DDL.
      73         self.output_transaction = (
```

**Candidate commits, oldest first:**

- `efd1e6096e`  2013-09-06  Adding 'sqlmigrate' command and quote_parameter to support it.
- `e12fea24f0`  2020-03-06  Optimized a bit handle() of sqlmigrate management command.

<details><summary>Line history</summary>

````diff
### e12fea24f0  2020-03-06  Optimized a bit handle() of sqlmigrate management command.

diff --git a/django/core/management/commands/sqlmigrate.py b/django/core/management/commands/sqlmigrate.py
--- a/django/core/management/commands/sqlmigrate.py
+++ b/django/core/management/commands/sqlmigrate.py
@@ -56,1 +56,1 @@
-        targets = [(app_label, migration.name)]
+        target = (app_label, migration.name)
### f17b24e407  2014-06-06  Converted remaining management commands to argparse

diff --git a/django/core/management/commands/sqlmigrate.py b/django/core/management/commands/sqlmigrate.py
--- a/django/core/management/commands/sqlmigrate.py
+++ b/django/core/management/commands/sqlmigrate.py
@@ -33,13 +41,1 @@
-        if len(args) != 2:
-            raise CommandError("Wrong number of arguments (expecting 'sqlmigrate app_label migrationname')")
-        else:
-            app_label, migration_name = args
-            if app_label not in executor.loader.migrated_apps:
-                raise CommandError("App '%s' does not have migrations" % app_label)
-            try:
-                migration = executor.loader.get_migration_by_prefix(app_label, migration_name)
-            except AmbiguityError:
-                raise CommandError("More than one migration matches '%s' in app '%s'. Please be more specific." % (app_label, migration_name))
-            except KeyError:
-                raise CommandError("Cannot find a migration matching '%s' from app '%s'. Is it in INSTALLED_APPS?" % (app_label, migration_name))
-            targets = [(app_label, migration.name)]
+        targets = [(app_label, migration.name)]
### c81fae6b95  2013-12-28  Used app_label instead of appname.

diff --git a/django/core/management/commands/sqlmigrate.py b/django/core/management/commands/sqlmigrate.py
--- a/django/core/management/commands/sqlmigrate.py
+++ b/django/core/management/commands/sqlmigrate.py
@@ -33,13 +33,13 @@
         if len(args) != 2:
-            raise CommandError("Wrong number of arguments (expecting 'sqlmigrate appname migrationname')")
+            raise CommandError("Wrong number of arguments (expecting 'sqlmigrate app_label migrationname')")
         else:
             app_label, migration_name = args
             if app_label not in executor.loader.migrated_apps:
                 raise CommandError("App '%s' does not have migrations" % app_label)
             try:
                 migration = executor.loader.get_migration_by_prefix(app_label, migration_name)
             except AmbiguityError:
                 raise CommandError("More than one migration matches '%s' in app '%s'. Please be more specific." % (app_label, migration_name))
             except KeyError:
                 raise CommandError("Cannot find a migration matching '%s' from app '%s'. Is it in INSTALLED_APPS?" % (app_label, migration_name))
             targets = [(app_label, migration.name)]
### efd1e6096e  2013-09-06  Adding 'sqlmigrate' command and quote_parameter to support it.

diff --git a/django/core/management/commands/sqlmigrate.py b/django/core/management/commands/sqlmigrate.py
--- /dev/null
+++ b/django/core/management/commands/sqlmigrate.py
@@ -0,0 +33,13 @@
+        if len(args) != 2:
+            raise CommandError("Wrong number of arguments (expecting 'sqlmigrate appname migrationname')")
+        else:
+            app_label, migration_name = args
+            if app_label not in executor.loader.migrated_apps:
+                raise CommandError("
... (cut, so use `git log -L` for the rest)
````

</details>

## T059  django  `django/db/backends/ddl_references.py:36`

```
      32         Rename all references to the old_name to the new_table.
      33         """
      34         pass
      35 
>>    36     def rename_column_references(self, table, old_column, new_column):
      37         """
      38         Rename all references to the old_column to the new_column.
      39         """
      40         pass
```

**Candidate commits, oldest first:**

- `b50815ee41`  2017-06-21  Refs #25530 -- Renamed deferred SQL references on rename operation.

<details><summary>Line history</summary>

````diff
### b50815ee41  2016-05-24  Refs #25530 -- Renamed deferred SQL references on rename operation.

diff --git a/django/db/backends/ddl_references.py b/django/db/backends/ddl_references.py
--- a/django/db/backends/ddl_references.py
+++ b/django/db/backends/ddl_references.py
@@ -22,0 +28,1 @@
+    def rename_column_references(self, table, old_column, new_column):

````

</details>

## T060  django  `django/contrib/admin/options.py:1191`

```
    1187             return self.get_action_choices(request, default_choices=default_choices)
    1188 
    1189     def _get_choice_description(self, action, action_location):
    1190         if action_location == ActionLocation.CHANGE_LIST:
>>  1191             return action.plural_description % model_format_dict(self.opts)
    1192         return action.description % model_format_dict(self.opts)
    1193 
    1194     def get_action_choices(
    1195         self,
```

**Candidate commits, oldest first:**

- `f30acb184f`  2026-05-13  Fixed #12090 -- Added admin actions to the admin change form.

<details><summary>Line history</summary>

````diff
### f30acb184f  2026-04-22  Fixed #12090 -- Added admin actions to the admin change form.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -1076,4 +1184,1 @@
-        actions = self._filter_actions_by_permissions(request, self._get_base_actions())
-        return {name: (func, name, desc) for func, name, desc in actions}
-
-    def get_action_choices(self, request, default_choices=None):
+            return action.plural_description % model_format_dict(self.opts)
### 63c56cda13  2026-01-18  Fixed #35870 -- Made blank choice label in forms more accessible.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -1049,4 +1050,4 @@
         actions = self._filter_actions_by_permissions(request, self._get_base_actions())
         return {name: (func, name, desc) for func, name, desc in actions}
 
-    def get_action_choices(self, request, default_choices=models.BLANK_CHOICE_DASH):
+    def get_action_choices(self, request, default_choices=None):
### 335c9c94ac  2019-08-20  Simplified imports from django.db and django.contrib.gis.db.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -889,4 +888,4 @@
         actions = self._filter_actions_by_permissions(request, self._get_base_actions())
         return {name: (func, name, desc) for func, name, desc in actions}
 
-    def get_action_choices(self, request, default_choices=BLANK_CHOICE_DASH):
+    def get_action_choices(self, request, default_choices=models.BLANK_CHOICE_DASH):
### 24b82cd201  2019-02-05  Fixed #30159 -- Removed unneeded use of OrderedDict.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -890,8 +886,4 @@
         actions = self._filter_actions_by_permissions(request, self._get_base_actions())
-        # Convert the actions into an OrderedDict keyed by name.
-        return OrderedDict(
-            (name, (func, name, desc))
-            for func, name, desc in actions
-        )
+        return {name: (func, name, desc) for func, name, desc in actions}
 
     def get_action_choices(self, request, default_choices=BLANK_CHOICE_DASH):
### 958c7b301e  2018-06-18  Fixed #29419 -- Allowed permissioning of admin actions.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -881,7 +898,8 @@
+        actions = self._filter_actions_by_permissions(request, self._get_base_actions())
         # Convert the actions into an OrderedDict keyed by name.
         return OrderedDict(
             (name, (func, name, desc))
             for func, name, desc in actions
         )
 
     def get_action_choices(self, request, default_choices=BLANK_CHOICE_DASH):
### acc8dd4142  2018-01-03  Fixed #28984 -- Made assorted code simplifications.

diff --git a/django/contrib/admin/options.py b/django/contrib/admin/options.py
--- a/django/contrib/admin/options.py
+++ b/django/contrib/admin/options.py
@@ -843,9 +843,7 @@
         # Convert the actions into an OrderedDict keyed by name.
-        actions = OrderedDict(
+        return OrderedDict(
             (name, (func, name, de
... (cut, so use `git log -L` for the rest)
````

</details>
