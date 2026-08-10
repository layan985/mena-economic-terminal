# Why I am keeping vintages

I started with ordinary country-period tables. That representation loses the fact that an observation can be revised after its first release. If I train or evaluate a forecast on the latest table, earlier forecast origins can silently see those later revisions.

The warehouse therefore stores releases rather than overwriting a period with the newest value. A query asks what the most recent available release was at a stated cutoff. Later revisions stay in the database but are invisible to earlier cutoffs.

This makes the data model more cumbersome. It also makes it possible to distinguish a genuine real-time forecast from one evaluated on hindsight.
