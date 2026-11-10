# Check Sheet

For each line, two labellers named different commits as **the most recent change to what the line does**. Read the line and both commits, then put `A`, `B`, `neither` or `unsure` in the `answer` column of `check_sheet.csv`.

- A change that only moves code, re-wraps it, renames a local variable or edits a comment does **not** change what the line does.
- A different value, condition, function or attribute **does**.
- `-` lines are the old version and `+` lines the new version.
- If a commit removes the line from one file (`-`) and adds the same text to another (`+`), it only moved the code, so it is **not** the answer.


## T020  `src/defrag.c:794`

```
struct zskiplistNode *newheader;
```

**A**

```diff
5ab6a54cc  2017-01-02  active defrag improvements
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ src/defrag.c:  struct zskiplistNode *newheader;
```

**B**

```diff
be1b4aa9a  2018-02-18  active defrag v2
In this line's history:

+    struct zskiplistNode *newheader;

Text like this line, anywhere in the commit:
+ src/defrag.c:  struct zskiplistNode *newheader;
- src/defrag.c:  struct zskiplistNode *newheader;
```


## T029  `django/contrib/syndication/views.py:120`

```
return {}
```

**A**

```diff
a2be52fd2a  2008-08-16  Fixed #6547, added support for GeoRSS feeds in `django.contrib.gis.feeds`; added the `feed_extra_kwargs` and `item_extra_kwargs` to the `Feed` baseclass so that it's possible for subclasses to add dynamic attributes.
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ django/contrib/syndication/feeds.py:  return {}
+ django/contrib/syndication/feeds.py:  return {}
```

**B**

```diff
c4c27d8a04  2010-01-28  Fixed #6188, #6304, #6618, #6969, #8758, #8989, #10334, #11069, #11973 and #12403 -- Modified the syndication framework to use class-based views. Thanks to Ben Firshman for his work on this patch.
In this line's history:

+        return {}

Text like this line, anywhere in the commit:
- django/contrib/syndication/feeds.py:  return {}
- django/contrib/syndication/feeds.py:  return {}
+ django/contrib/syndication/views.py:  return {}
+ django/contrib/syndication/views.py:  return {}
```


## T034  `src/t_stream.c:5673`

```
addReplyStreamID(c,&s->last_id);
```

**A**

```diff
1e2aee391  2020-04-22  Extend XINFO STREAM output
In this line's history:

+    addReplyStreamID(c,&s->last_id);

Text like this line, anywhere in the commit:
+ src/t_stream.c:  addReplyStreamID(c,&s->last_id);
- src/t_stream.c:  addReplyStreamID(c,&s->last_id);
```

**B**

```diff
b4ba5ac84  2018-07-16  Streams: show last id for streams and groups
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ src/t_stream.c:  addReplyStreamID(c,&s->last_id);
```


## T037  `src/t_list.c:1307`

```
robj *o;
```

**A**

```diff
4409877e1  2009-12-29  not yet working BLPOP implementation
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ redis.c:  robj *o;
```

**B**

```diff
e2641e09c  2010-06-22  redis.c split into many different C files.
In this line's history:

+    robj *o;

Text like this line, anywhere in the commit:
- redis.c:  robj *o;
- redis.c:  robj *o;
- redis.c:  robj *o;
- redis.c:  robj *o;
- redis.c:  robj *o;
- redis.c:  robj *o;
- redis.c:  robj *o;
- redis.c:  robj *o;
- redis.c:  robj *o;
- redis.c:  robj *o;
- redis.c:  robj *o;
- redis.c:  robj *o;
```


## T038  `django/db/backends/mysql/features.py:16`

```
supports_regex_backreferencing = False
```

**A**

```diff
28308078f3  2015-01-12  Fixed #22603 -- Reorganized classes in django.db.backends.
In this line's history:

+    supports_regex_backreferencing = False

Text like this line, anywhere in the commit:
- django/db/backends/__init__.py:  supports_regex_backreferencing = True
+ django/db/backends/base/features.py:  supports_regex_backreferencing = True
- django/db/backends/mysql/base.py:  supports_regex_backreferencing = False
+ django/db/backends/mysql/features.py:  supports_regex_backreferencing = False
```

**B**

```diff
121d2e3678  2010-10-11  Fixed #12991 -- Added unittest2 support. Thanks to PaulM for the draft patch, and to Luke, Karen, Justin, Alex, Łukasz Rekucki, and Chuck Harmston for their help testing and reviewing the final patch.
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ django/db/backends/__init__.py:  supports_regex_backreferencing = True
+ django/db/backends/mysql/base.py:  supports_regex_backreferencing = False
+ tests/modeltests/lookup/models.py:  if connection.features.supports_regex_backreferencing:
```


## T042  `src/endianconv.c:81`

```
return v;
```

**A**

```diff
7a3e37202  2012-02-14  endian.c/h -> endianconv.c/h to avoid issues with broken libraries search paths.
In this line's history:

+    return v;

Text like this line, anywhere in the commit:
- src/endian.c:  return v;
- src/endian.c:  return v;
- src/endian.c:  return v;
+ src/endianconv.c:  return v;
+ src/endianconv.c:  return v;
+ src/endianconv.c:  return v;
```

**B**

```diff
565384771  2012-02-08  ziplist.c fixes for bigendian
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ src/endian.c:  return v;
+ src/endian.c:  return v;
+ src/endian.c:  return v;
```


## T052  `src/fwtree.c:92`

```
result = current;
```

**A**

```diff
9b63e99d0  2025-09-11  Refactor HFE: Introduce Per-Slot Expiration Store (estore) (#14294)
In this line's history:

+            result = current;

Text like this line, anywhere in the commit:
+ src/fwtree.c:  result = current;
- src/kvstore.c:  result = current;
```

**B**

```diff
f7fa48115  2023-10-27  Optimize finding the slot for a given key count in a fenwick tree (#12704)
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ src/db.c:  result = current;
```


## T053  `django/db/models/fields/json.py:530`

```
previous = previous.lhs
```

**A**

```diff
6789ded0a6  2019-06-09  Fixed #12990, Refs #27694 -- Added JSONField model field.
In this line's history:

+            previous = previous.lhs

Text like this line, anywhere in the commit:
- django/contrib/postgres/fields/jsonb.py:  previous = previous.lhs
+ django/db/models/fields/json.py:  previous = previous.lhs
```

**B**

```diff
33ea472f69  2015-05-30  Fixed #24604 -- Added JSONField to contrib.postgres.
Not in this line's history in its current file.
Text like this line, anywhere in the commit:
+ django/contrib/postgres/fields/jsonb.py:  previous = previous.lhs
```
