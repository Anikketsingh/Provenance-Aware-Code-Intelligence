# Check Sheet

For each line, two labellers named different commits as **the most recent change to what the line does**. Read the line and both commits, then put `A`, `B`, `neither` or `unsure` in the `answer` column of `check_sheet.csv`.

- A change that only moves code, re-wraps it, renames a local variable or edits a comment does **not** change what the line does.
- A different value, condition, function or attribute **does**.
- `-` lines are the old version and `+` lines the new version.
- If a commit removes the line from one file (`-`) and adds the same text to another (`+`), it only moved the code, so it is **not** the answer.


## L002  `src/cluster_legacy.h:329`

```
int cport;                  /* Latest known cluster port of this node. */
```

**A**

```diff
11436b144  2016-01-21  Cluster announce ip / port initial implementation.
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ src/cluster.h:  int cport;                  /* Latest known cluster port of this node. */
```

**B**

```diff
d9a047859  2023-10-30  Cluster refactor: Make clusterNode private
In this line's history:

+    int cport;                  /* Latest known cluster port of this node. */

Text like this line, anywhere in the commit:
- src/cluster.h:  int cport;                  /* Latest known cluster port of this node. */
+ src/cluster_legacy.h:  int cport;                  /* Latest known cluster port of this node. */
```


## L014  `src/server.c:4162`

```
static long long prev_err_count = 0;
```

**A**

```diff
90b9f08e5  2020-12-31  Add errorstats info section, Add failed_calls and rejected_calls to commandstats (#8217)
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ src/server.c:  static long long prev_err_count;
```

**B**

```diff
aa856b39f  2022-02-27  Sort out the mess around Lua error messages and error stats (#10329)
In this line's history:

+    static long long prev_err_count = 0;

Text like this line, anywhere in the commit:
+ src/server.c:  static long long prev_err_count = 0;
- src/server.c:  static long long prev_err_count;
```


## L019  `django/http/response.py:297`

```
return self.set_cookie(key, value, **kwargs)
```

**A**

```diff
b4066d7d21  2012-10-21  Cleaned up the the http module. Moved all of the code from __init__.py to request.py, response.py and utils.py
In this line's history:

+        return self.set_cookie(key, value, **kwargs)

Text like this line, anywhere in the commit:
- django/http/__init__.py:  return self.set_cookie(key, value, **kwargs)
+ django/http/response.py:  return self.set_cookie(key, value, **kwargs)
```

**B**

```diff
f60d428463  2011-05-21  Fixed #12417 -- Added signing functionality, including signing cookies. Many thanks to Simon, Stephan, Paul and everyone else involved.
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ django/http/__init__.py:  return self.set_cookie(key, value, **kwargs)
```


## L020  `src/server.h:1079`

```
int options;    /* Module options and capabilities. */
```

**A**

```diff
4339706e0  2019-07-30  Avoid diskelss-load if modules did not declare they handle read errors
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ src/module.c:  int options;    /* Moduile options and capabilities. */
```

**B**

```diff
babe3c7b2  2018-04-20  Modules: rewrite config loadmodule option
In this line's history:

+    int options;    /* Module options and capabilities. */

Text like this line, anywhere in the commit:
- src/module.c:  int options;    /* Module options and capabilities. */
+ src/server.h:  int options;    /* Module options and capabilities. */
```


## L025  `src/module.c:13966`

```
for (int j = 0; cmd->history && cmd->history[j].since; j++) {
```

**A**

```diff
23325c135  2022-01-23  sub-command support for ACL CAT and COMMAND LIST. redisCommand always stores fullname (#10127)
In this line's history:

+    for (int j = 0; cmd->history && cmd->history[j].since; j++) {

Text like this line, anywhere in the commit:
+ src/module.c:  for (int j = 0; cmd->history && cmd->history[j].since; j++) {
- src/module.c:  for (int j = 0; cmd->history && cmd->history[j].since; j++) {
```

**B**

```diff
867816003  2021-12-15  Auto-generate the command table from JSON files (#9656)
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ src/module.c:  for (int j = 0; cmd->history && cmd->history[j].since; j++) {
```


## L027  `django/db/backends/postgresql/base.py:252`

```
if settings_dict["NAME"] == "" and not settings_dict["OPTIONS"].get("service"):
```

**A**

```diff
dcb3ad3319  2020-12-23  Fixed #32292 -- Added support for connection by service name to PostgreSQL.
In this line's history:

-        if settings_dict['NAME'] == '':
+        if (
+            settings_dict['NAME'] == '' and
+            not settings_dict.get('OPTIONS', {}).get('service')
+        ):

```

**B**

```diff
50e95ad536  2024-02-23  Simplified using DATABASES["OPTIONS"].
In this line's history:

-        if settings_dict["NAME"] == "" and not settings_dict.get("OPTIONS", {}).get(
-            "service"
-        ):
+        if settings_dict["NAME"] == "" and not settings_dict["OPTIONS"].get("service"):

Text like this line, anywhere in the commit:
- django/db/backends/postgresql/base.py:  if settings_dict["NAME"] == "" and not settings_dict.get("OPTIONS", {}).get(
+ django/db/backends/postgresql/base.py:  if settings_dict["NAME"] == "" and not settings_dict["OPTIONS"].get("service"):
```


## L029  `django/contrib/contenttypes/forms.py:86`

```
can_order=False,
```

**A**

```diff
10e3faf191  2014-01-22  Fixed #19774 -- Deprecated the contenttypes.generic module.
In this line's history:

+def generic_inlineformset_factory(model, form=ModelForm,
+                                  formset=BaseGenericInlineFormSet,
+                                  ct_field="content_type", fk_field="object_id",
+                                  fields=None, exclude=None,
+                                  extra=3, can_order=False, can_delete=True,
+                                  max_num=None,
+                                  formfield_callback=None, validate_max=False,
+                                  for_concrete_model=True):

Text like this line, anywhere in the commit:
+ django/contrib/contenttypes/forms.py:  extra=3, can_order=False, can_delete=True,
- django/contrib/contenttypes/generic.py:  extra=3, can_order=False, can_delete=True,
+ docs/ref/contrib/contenttypes.txt:  .. function:: generic_inlineformset_factory(model, form=ModelForm, formset=BaseGenericInlineFormSet, ct_field="content_type", fk_field="object_id", fields=None, exclude=None, extra=3, can_order=False, can_delete=True, max_num=None, formfield_callback=None, validate_max=False, for_concrete_model=True)
- docs/ref/contrib/contenttypes.txt:  .. function:: generic_inlineformset_factory(model, form=ModelForm, formset=BaseGenericInlineFormSet, ct_field="content_type", fk_field="object_id", fields=None, exclude=None, extra=3, can_order=False, can_delete=True, max_num=None, formfield_callback=None, validate_max=False, for_concrete_model=True)
```

**B**

```diff
02cc59187b  2008-08-10  Fixed #4667 -- Added support for inline generic relations in the admin. Thanks to Honza Král and Alex Gaynor for their work on this ticket.
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ django/contrib/contenttypes/generic.py:  extra=3, can_order=False, can_delete=True,
```


## L031  `django/core/files/images.py:61`

```
if not data:
```

**A**

```diff
7899568e01  2008-08-08  File storage refactoring, adding far more flexibility to Django's file handling. The new files.txt document has details of the new features.
In this line's history:

+    while 1:
+        data = file.read(1024)
+        if not data:
+            break
+        p.feed(data)
+        if p.image:
+            return p.image.size
+    return None

Text like this line, anywhere in the commit:
+ django/core/files/images.py:  if not data:
- django/utils/images.py:  if not data:
```

**B**

```diff
ed114e1510  2005-07-13  Imported Django from private SVN repository (created from r. 8825)
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ django/core/formfields.py:  if not data:
+ django/utils/images.py:  if not data:
```


## L032  `src/script_lua.c:1233`

```
luaLoadLib(lua, "cmsgpack", luaopen_cmsgpack);
```

**A**

```diff
63505e0b5  2012-02-24  Lua_cmsgpack added to Redis scripting.
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ src/scripting.c:  luaLoadLib(lua, "cmsgpack", luaopen_cmsgpack);
```

**B**

```diff
22aab1ce9  2021-10-05  Redis Functions - Move code to make review process easier.
In this line's history:

+    luaLoadLib(lua, "cmsgpack", luaopen_cmsgpack);

Text like this line, anywhere in the commit:
- src/scripting.c:  luaLoadLib(lua, "cmsgpack", luaopen_cmsgpack);
+ src/script_lua.c:  luaLoadLib(lua, "cmsgpack", luaopen_cmsgpack);
```


## L036  `src/script_lua.c:210`

```
.null_callback = redisProtocolToLuaType_Null,
```

**A**

```diff
2237131e1  2021-08-04  Unified Lua and modules reply parsing and added RESP3 support to RM_Call (#9202)
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ src/scripting.c:  .null_callback = redisProtocolToLuaType_Null,
```

**B**

```diff
22aab1ce9  2021-10-05  Redis Functions - Move code to make review process easier.
In this line's history:

+    .null_callback = redisProtocolToLuaType_Null,

Text like this line, anywhere in the commit:
- src/scripting.c:  .null_callback = redisProtocolToLuaType_Null,
+ src/script_lua.c:  .null_callback = redisProtocolToLuaType_Null,
```


## L041  `django/contrib/admin/options.py:622`

```
def has_change_permission(self, request, obj=None):
```

**A**

```diff
b1b1da1eac  2011-10-07  Fixed #8060 - Added permissions-checking for admin inlines. Thanks p.patruno for report and Stephan Jaensch for work on the patch.
In this line's history:

+    def has_change_permission(self, request, obj=None):

Text like this line, anywhere in the commit:
+ django/contrib/admin/options.py:  def has_change_permission(self, request, obj=None):
- django/contrib/admin/options.py:  def has_change_permission(self, request, obj=None):
+ django/contrib/admin/options.py:  def has_change_permission(self, request, obj=None):
```

**B**

```diff
a19ed8aea3  2008-07-18  Merged the newforms-admin branch into trunk.
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ django/contrib/admin/options.py:  def has_change_permission(self, request, obj=None):
```


## L047  `src/db.c:3264`

```
int slot = getKeySlot(key);
```

**A**

```diff
e1789e436  2025-05-12  keyspace - Unify key and value & use dict no_value=1 (#13806)
In this line's history:

-static inline dictEntry *dbFindWithKeySlot(redisDb *db, void *key, int keySlot) {
-    return dbFindGenericWithKeySlot(db->keys, key, keySlot);
-}
+    int slot = getKeySlot(key);

Text like this line, anywhere in the commit:
+ src/db.c:  int slot = getKeySlot(key);
+ src/db.c:  int slot = getKeySlot(key);
```

**B**

```diff
0270abda8  2023-10-14  Replace cluster metadata with slot specific dictionaries (#11695)
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ src/db.c:  int slot = getKeySlot(key);
+ src/db.c:  int slot = getKeySlot(key);
```


## L050  `django/db/models/fields/related.py:1778`

```
"where the field is attached to."
```

**A**

```diff
aaad3e27ac  2014-03-07  Fixed #22217 - ManyToManyField.through_fields fixes.
In this line's history:

+                    "where the field is attached to."

Text like this line, anywhere in the commit:
+ django/db/models/fields/related.py:  "where the field is attached to."
```

**B**

```diff
d818e0c9b2  2014-01-20  Fixed #16905 -- Added extensible checks (nee validation) framework
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ django/db/models/fields/related.py:  "where the field is attached to."
```


## L052  `src/lolwut5.c:72`

```
if (rand() % 2) r3 = -r3;
```

**A**

```diff
c560ade83  2018-09-14  LOLWUT: split the command from version-specific implementations.
In this line's history:

+                if (rand() % 2) r3 = -r3;

Text like this line, anywhere in the commit:
- src/lolwut.c:  if (rand() % 2) r3 = -r3;
+ src/lolwut5.c:  if (rand() % 2) r3 = -r3;
```

**B**

```diff
eac2a79cf  2018-09-12  LOLWUT: draw Schotter by Georg Nees.
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ src/lolwut.c:  if (rand() % 2) r3 = -r3;
```


## L058  `src/acl.c:2920`

```
struct redisCommand *cmd = dictGetVal(de);
```

**A**

```diff
23325c135  2022-01-23  sub-command support for ACL CAT and COMMAND LIST. redisCommand always stores fullname (#10127)
In this line's history:

+        struct redisCommand *cmd = dictGetVal(de);

Text like this line, anywhere in the commit:
+ src/acl.c:  struct redisCommand *cmd = dictGetVal(de);
- src/acl.c:  struct redisCommand *cmd = dictGetVal(de);
+ src/server.c:  struct redisCommand *cmd = dictGetVal(de);
+ src/server.c:  struct redisCommand *cmd = dictGetVal(de);
- src/server.c:  struct redisCommand *cmd = dictGetVal(de);
- src/server.c:  struct redisCommand *cmd = dictGetVal(de);
```

**B**

```diff
b9c97c0b2  2019-02-12  ACL: CAT subcommand implemented.
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ src/acl.c:  struct redisCommand *cmd = dictGetVal(de);
```
