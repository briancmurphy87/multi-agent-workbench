# Release History

This page provides a high-level summary of changes to SQLite. For more detail, see the Fossil checkin logs at [https://sqlite.org/src/timeline](https://sqlite.org/src/timeline) and [https://sqlite.org/src/timeline?t=release](https://sqlite.org/src/timeline?t=release). 

See the [chronology](chronology.html) a succinct listing of releases.

## 2026-04-09 (3.53.0)

1.  Fix the [WAL-reset database corruption bug](wal.html#walresetbug).
2.  Add the [Query Result Formatter (QRF)](https://sqlite.org/src/file/ext/qrf) library for formatting the results of SQL queries for human readability on a fixed-pitch font screen.
    1.  Add the [format method](tclsqlite.html#format) to the [TCL Interface](tclsqlite.html) so that QRF is accessible from TCL.
    2.  QRF is used for result formatting in the [CLI](cli.html), resulting in improved display capabilities.
3.  New SQL language features:
    1.  Enhance [ALTER TABLE](lang_altertable.html) to permit adding and removing NOT NULL and CHECK constraints.
    2.  The [REINDEX EXPRESSIONS](lang_reindex.html) statement rebuilds expression indexes. (Useful to repair [stale expression indexes](staleexpridx.html).)
    3.  The body of [TEMP triggers](lang_createtrigger.html#temptrig) may now modify and/or query tables in the main schema.
    4.  Enhance [VACUUM INTO](lang_vacuum.html#vacuuminto) so that if a [URI filename](uri.html) is used as the target and that filename has a reserve=N query parameter with N between 0 and 255, then the [reserve amount](fileformat2.html#resbyte) for the generated database copy is set to N.
4.  New SQL functions:
    1.  [json\_array\_insert()](json1.html#jarrayins)
    2.  [jsonb\_array\_insert()](json1.html#jarrayins)
5.  Renovations to the [CLI](cli.html):
    1.  Major enhancements to the [.mode command](climode.html).
    2.  Improved result formatting, due to the addition of the [QRF extension](https://sqlite.org/src/file/ext/qrf). For example, numeric values are now right-justified by default in [tabular output modes](climode.html#clmnr).
    3.  The default output mode for interactive CLI sessions now uses QRF to display query results in boxes formed using Unicode box-drawing characters, for improved legibility. Batch CLI sessions use the legacy output format for compatibility.
    4.  Bare (unquoted) semicolons at the end of [dot-commands](cli.html#dotcmd) are silently ignored.  ← Potential incompatibility!
    5.  Fix the .testcase and .check commands so that they actually work, and use those commands in scripts that are part of the standard SQLite test suite included with the source tree.
    6.  Command-line arguments that match \*.sql or \*.txt and are the names of non-empty files are read and interpreted as scripts of SQL statements and/or [dot-commands](cli.html#dotcmd).
    7.  The argument to the ".timer" command can now be "once", to run the timer on only the next SQL statement.
    8.  The new "--timeout S" option to the ".progress" dot-command causes SQL statements to interrupt after S seconds.
    9.  The ".indexes" command was changed so that the PATTERN argument matches the name of the index, not the name of the table being indexed (thus making the PATTERN argument actually useful). And, several new options were added to ".indexes".
6.  New C-language interfaces:
    1.  [sqlite3\_str\_truncate()](c3ref/str_append.html)
    2.  [sqlite3\_str\_free()](c3ref/str_finish.html)
    3.  [sqlite3\_carray\_bind\_v2()](c3ref/carray_bind.html)
    4.  Add the [SQLITE\_PREPARE\_FROM\_DDL](c3ref/c_prepare_dont_log.html#sqlitepreparefromddl) option to [sqlite3\_prepare\_v3()](c3ref/prepare.html) which permits [virtual table](vtab.html) implementations to safely prepare SQL statements that are derived from the database schema.
    5.  Added the [SQLITE\_UTF8\_ZT](c3ref/c_any.html#sqliteutf8zt) constant which can be used as the encoding parameter to [sqlite3\_result\_text64()](c3ref/result_blob.html) or [sqlite3\_bind\_text64()](c3ref/bind_blob.html) to indicate that the value is UTF-8 encoded and zero terminated.
    6.  The [SQLITE\_LIMIT\_PARSER\_DEPTH](c3ref/c_limit_attached.html#sqlitelimitparserdepth) option is added to [sqlite3\_limit()](c3ref/limit.html).
    7.  The [SQLITE\_DBCONFIG\_FP\_DIGITS](c3ref/c_dbconfig_defensive.html#sqlitedbconfigfpdigits) option is added to [sqlite3\_db\_config()](c3ref/db_config.html). See also item 9b below.
7.  Query planner improvements:
    1.  Always use a sort-and-merge algorithm for EXCEPT, INTERSECT, and UNION, since this is almost always faster than using a hash table.
    2.  Improvements to join order selection in large multi-way joins on a star schema.
    3.  Enhance the EXISTS-to-JOIN optimization so that the inserted JOIN terms are not required to be on the inner-most loops, as long as all dependencies for the EXISTS-to-JOIN loops are in outer loops.
    4.  Enhance the omit-noop-join optimization so that it is able to omit a chain of joins that do not affect the output.
    5.  Allow queries that use "GROUP BY e1 ORDER BY e2" where e1 and e2 are identical apart from ASC/DESC sort-orders to be optimized using a single index.
    6.  Allow virtual tables to optimize DISTINCT in cases where the result-set of a query does not exactly match the ORDER BY clause.
8.  Add new interfaces to the [session extension](sessionintro.html) that enable an application to add changes one at a time to the sqlite3\_changegroup object:
    1.  [sqlite3changegroup\_change\_begin()](session/sqlite3changegroup_change_begin.html)
    2.  [sqlite3changegroup\_change\_blob()](session/sqlite3changegroup_change_blob.html)
    3.  [sqlite3changegroup\_change\_double()](session/sqlite3changegroup_change_double.html)
    4.  [sqlite3changegroup\_change\_int64()](session/sqlite3changegroup_change_int64.html)
    5.  [sqlite3changegroup\_change\_null()](session/sqlite3changegroup_change_null.html)
    6.  [sqlite3changegroup\_change\_text()](session/sqlite3changegroup_change_text.html)
    7.  [sqlite3changegroup\_change\_finish()](session/sqlite3changegroup_change_finish.html)
    8.  [sqlite3changegroup\_config()](session/sqlite3changegroup_config.html)
9.  Improvements to floating-point ↔ text conversions.
    1.  Reimplemented to improve performance.
    2.  Rounding is now done by [default to 17 significant digits](floatingpoint.html#*fpdigits), instead of 15, as was the case for all prior versions. The [sqlite3\_db\_config](c3ref/db_config.html)([SQLITE\_DBCONFIG\_FP\_DIGITS](c3ref/c_dbconfig_defensive.html#sqlitedbconfigfpdigits)) API (item 6g above) can change this, if desired.
10.  Added the [self-healing index](staleexpridx.html#selfheal) feature to deal with the [stale expression index](staleexpridx.html) problem.
11.  Add the "-p|--port" option to [sqlite3\_rsync](rsync.html).
12.  Discontinue support for [Windows RT](https://en.wikipedia.org/wiki/Windows_RT).
13.  JavaScript/WASM
    1.  Add the "opfs-wl" VFS, functionally identical to the "opfs" VFS but using Web Locks for locking, which can promise fairer lock sharing than the "opfs" bespoke protocol can. "opfs-wl" requires `Atomics.waitAsync()`, so requires newer browsers than "opfs" does.

**Hashes:**

15.  SQLITE\_SOURCE\_ID: 2026-04-09 11:41:38 4525003a53a7fc63ca75c59b22c79608659ca12f0131f52c18637f829977f20b
16.  SHA3-256 for sqlite3.c: bb317fbbd2b3bc53233ddd5894bf4d2dc6f533445f350d4235dbcc86f65af4ec

## 2026-03-13 (3.51.3)

1.  Fix the [WAL-reset database corruption bug](wal.html#walresetbug).
2.  Other minor bug fixes.
3.  SQLITE\_SOURCE\_ID: 2026-03-13 10:38:09 737ae4a34738ffa0c3ff7f9bb18df914dd1cad163f28fd6b6e114a344fe6d618
4.  SHA3-256 for sqlite3.c: 32d5424f97e0a7fc5ed2f6335afbb58be4e0298bd7117a34e39d345ff13d859e

## 2026-03-06 (3.52.0)

_Withdrawn_

_All of the features that were originally scheduled for the 3.52.0 release have been moved forward into [version 3.53.0](#version_3_53_0)._

## 2026-01-09 (3.51.2)

1.  Fix an obscure deadlock in the new broken-posix-lock detection logic in item 17 above.
2.  Fix multiple problems in the EXISTS-to-JOIN optimization that was added as part of optimization item 6b above.
3.  Other minor bug fixes.
4.  SQLITE\_SOURCE\_ID: 2026-01-09 17:27:48 b270f8339eb13b504d0b2ba154ebca966b7dde08e40c3ed7d559749818cb2075
5.  SHA3-256 for sqlite3.c: 733b3fcc6cccb1e334424b9b91a9d68b618385b76ebfcbb106690bd3a9e61367

## 2025-11-28 (3.51.1)

1.  Fix incorrect results from nested EXISTS queries caused by the optimization in item 6b in the 3.51.0 release.
2.  Fix a latent bug in [fts5vocab](fts5.html#the_fts5vocab_virtual_table_module) virtual table, exposed by new optimizations in the 3.51.0 release
    
    **Hashes:**
    
3.  SQLITE\_SOURCE\_ID: 2025-11-28 17:28:25 281fc0e9afc38674b9b0991943b9e9d1e64c6cbdb133d35f6f5c87ff6af38a88
4.  SHA3-256 for sqlite3.c: 7cec3a104797bea93970408168197af37f178ab608ea55efd48d28daa87a8ce3

## 2025-11-04 (3.51.0)

1.  New macros in sqlite3.h:
    1.  SQLITE\_SCM\_BRANCH → the name of the branch from which the source code is taken.
    2.  SQLITE\_SCM\_TAGS → space-separated list of tags on the source code check-in.
    3.  SQLITE\_SCM\_DATETIME → ISO-8601 date and time of the source code check-in.
2.  Two new JSON functions, [jsonb\_each()](json1.html#jbeach) and [jsonb\_tree()](json1.html#jbtree) work the same as the existing json\_each() and json\_tree() functions except that they return [JSONB](json1.html#jsonbx) for the "value" column when the "type" is 'array' or 'object'.
3.  The [carray](carray.html) and [percentile](percentile.html) extensions are now built into [the amalgamation](amalgamation.html), though they are disabled by default and must be activated at compile-time using the [\-DSQLITE\_ENABLE\_CARRAY](compile.html#enable_carray) and/or [\-DSQLITE\_ENABLE\_PERCENTILE](compile.html#enable_percentile) options, respectively.
4.  Enhancements to [TCL Interface](tclsqlite.html):
    1.  Add the `-asdict` flag to the `eval` command to have it set the row data as a dict instead of an array.
    2.  User-defined functions may now `break` to return an SQL NULL.
5.  [CLI](cli.html) enhancements:
    1.  Increase the precision of ".timer" to microseconds.
    2.  Enhance the "box" and "column" formatting modes to deal with double-wide characters.
    3.  The ".imposter" command provides read-only [imposter tables](imposter.html) that work with [VACUUM](lang_vacuum.html) and do not require the --unsafe-testing option.
    4.  Add the --ifexists option to the CLI command-line option and to the [.open command](cli.html#dotopen).
    5.  Limit columns widths set by the ".width" command to 30,000 or less, as there is not good reason to have wider columns, but supporting wider columns provides opportunity to malefactors.
6.  Performance enhancements:
    1.  Use fewer CPU cycles to commit a read transaction.
    2.  Early detection of joins that return no rows due to one or more of the tables containing no rows.
    3.  Avoid evaluation of scalar subqueries if the result of the subquery does not change the result of the overall expression.
    4.  Faster window function queries when using "BETWEEN :x FOLLOWING AND :y FOLLOWING" with a large :y.
7.  Add the [PRAGMA wal\_checkpoint=NOOP;](pragma.html#pragma_wal_checkpoint) command and the [SQLITE\_CHECKPOINT\_NOOP](c3ref/c_checkpoint_full.html) argument for [sqlite3\_wal\_checkpoint\_v2()](c3ref/wal_checkpoint_v2.html).
8.  Add the [sqlite3\_set\_errmsg()](c3ref/set_errmsg.html) API for use by extensions.
9.  Add the [sqlite3\_db\_status64()](c3ref/db_status.html) API, which works just like the existing [sqlite3\_db\_status()](c3ref/db_status.html) API except that it returns 64-bit results.
10.  Add the [SQLITE\_DBSTATUS\_TEMPBUF\_SPILL](c3ref/c_dbstatus_options.html) option to the [sqlite3\_db\_status()](c3ref/db_status.html) and [sqlite3\_db\_status64()](c3ref/db_status.html) interfaces.
11.  In the [session extension](sessionintro.html) add the [sqlite3changeset\_apply\_v3()](session/sqlite3changeset_apply.html) interface.
12.  For the [built-in printf()](printf.html) and the [format() SQL function](lang_corefunc.html#format), omit the leading '-' from negative floating point numbers if the '+' flag is omitted and the "#" flag is present and all displayed digits are '0'. Use '%#f' or similar to avoid outputs like '-0.00' and instead show just '0.00'.
13.  Improved error messages generated by [FTS5](fts5.html).
14.  Enforce STRICT typing on computed columns.
15.  Improved support for VxWorks
16.  JavaScript/WASM now supports 64-bit WASM. The canonical builds continue to be 32-bit but creating one's own 64-bit build is now as simple as running "make".
17.  Improved resistance to database corruption caused by an application [breaking Posix advisory locks using close()](howtocorrupt.html#posix_close_bug).
    
    **Hashes:**
    
18.  SQLITE\_SOURCE\_ID: 2025-11-04 19:38:17 fb2c931ae597f8d00a37574ff67aeed3eced4e5547f9120744ae4bfa8e74527b
19.  SHA3-256 for sqlite3.c: e2add951748f73587cadd1b2684defb4f39fa58dca14b16162d4237e50af9afa

## 2025-07-30 (3.50.4)

1.  Fix two long-standings cases of the use of uninitialized variables in obscure circumstances.
    
    **Hashes:**
    
2.  SQLITE\_SOURCE\_ID: 2025-07-30 19:33:53 4d8adfb30e03f9cf27f800a2c1ba3c48fb4ca1b08b0f5ed59a4d5ecbf45e20a3
3.  SHA3-256 for sqlite3.c: 9145255e83da6529e70121ee4d7a4c88fe83ca4511da0c9ed13d10842df36782

## 2025-07-17 (3.50.3)

1.  Fix a possible memory error that can occur if a query is made against against FTS5 index that has been deliberately corrupted in a very specific way.
2.  Fix the parser so that it ignored SQL comments in all places of a CREATE TRIGGER statement. This resolves a problem that was introduced by the introduction of the SQLITE\_DBCONFIG\_ENABLE\_COMMENTS feature in version 3.49.0.
3.  Fix an incorrect answer due to over-optimization of an AND operator. [Forum post f4878de3e](https://sqlite.org/forum/forumpost/f4878de3e7dd4764).
4.  Fix minor makefile issues and documentation typos.
    
    **Hashes:**
    
5.  SQLITE\_SOURCE\_ID: 2025-07-17 13:25:10 3ce993b8657d6d9deda380a93cdd6404a8c8ba1b185b2bc423703e41ae5f2543
6.  SHA3-256 for sqlite3.c: 934fafe96caa7f4c16e82e0c2b674441a715c038acc9780bf15e09411daba70c

## 2025-06-28 (3.50.2)

1.  Fix the [concat\_ws()](lang_corefunc.html#concat_ws) SQL function so that it includes empty strings in the concatenation. [Forum post 52503ac21d](https://sqlite.org/forum/forumpost/52503ac21d).
2.  Fix the file-io extension (used by the CLI) so that it can be built using the MinGW compiler chain.
3.  Avoid writing frames with no checksums into the wal file if a savepoint is rolled back after dirty pages have already been spilled into the wal file. [Forum post b490f726db](https://sqlite.org/forum/forumpost/b490f726db).
4.  Fix the Bitvec object to avoid stack overflow when the database is within 60 pages of its maximum size.
5.  Fix a problem with UPDATEs on fts5 tables that contain BLOB values.
6.  Fix an issue with transitive IS constraints on a RIGHT JOIN.
7.  Raise an error early if the number of aggregate terms in a query exceeds the maximum number of columns, to avoid downstream assertion faults.
8.  Ensure that sqlite3\_setlk\_timeout() holds the database mutex.
9.  Fix typos in API documentation.
    
    **Hashes:**
    
10.  SQLITE\_SOURCE\_ID: 2025-06-28 14:00:48 2af157d77fb1304a74176eaee7fbc7c7e932d946bf25325e9c26c91db19e3079
11.  SHA3-256 for sqlite3.c: 889bf23942c52f38a6f182e71d3f0a03db490fd731f02147b1142c11153f3b3a

## 2025-06-06 (3.50.1)

1.  Fix a long-standing bug in [jsonb\_set()](json1.html#jsetb) and similar that was exposed by new optimizations added in version 3.50.0.
2.  Fix an apparently harmless ASAN warning that can occur on builds that use [\-DSQLITE\_DEFAULT\_MEMSTATUS=0](compile.html#default_memstatus).
3.  Fix an off-by-one bug in [sqlite3\_rsync](rsync.html) that can result in the last page not being transferred for the replicate database.
4.  Query planner optimization: Allow the right-hand side of a LEFT JOIN to be [flattened](optoverview.html#flattening) even if it is a virtual table.
5.  Fix [sqlite3\_setlk\_timeout()](c3ref/setlk_timeout.html) to use a blocking lock when opening a snapshot transaction and when blocked by another process running recovery.
6.  Other minor fixes that were reported after the 3.50.0 release.
    
    **Hashes:**
    
7.  SQLITE\_SOURCE\_ID: 2025-06-06 14:52:32 b77dc5e0f596d2140d9ac682b2893ff65d3a4140aa86067a3efebe29dc914c95
8.  SHA3-256 for sqlite3.c: c3bdffa01dab94be370bdcaeb819cda4a6e0c61f0c6e19a6f94ccba76fc9eeca
