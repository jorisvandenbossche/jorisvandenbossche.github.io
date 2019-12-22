Title: Towards consistent missing value handling in Pandas
Date: 2019-11-30 09:00
Tags: python, pandas
Slug: pandas-consistent-missing-values
Comments: true

<!-- PELICAN_BEGIN_SUMMARY -->

This blogpost gives some background and motivation for my proposal on better
missing value support in pandas, and the ongoing changes landing in the
development version (to be released in pandas 1.0): a new `pd.NA` scalar is
introduced.

<!-- PELICAN_END_SUMMARY -->

```python
>>> pd.Series([1, 2, pd.NA], dtype="Int64")
0     1
1     2
2    NA
dtype: Int64
```

See below for more examples.

### Background

The handling of missing values in pandas is currently a bit "messy", so to say.
The biggest gotcha is that a column with integer data cannot hold missing
values. If for some reason a missing value gets introduced (e.g. as a result of
a certain operation, or just when reading in data), the values are converted to
floats:

```python
>>> s = pd.Series([1, 2, 3])
>>> s
0    1
1    2
2    3
dtype: int64

>>>  s[0] = np.nan
>>> s
0    NaN
1    2.0
2    3.0
dtype: float64
```

In addition to the above gotcha, there are some other confusing aspects about
the missing value story in pandas:

* Also boolean data (in addition to integer data) do not support missing values.
* For object dtype data (which is typically used to store strings), we use
  ``np.nan`` (a float number!) as the missing value indicator, and also allow
  ``None`` (so you can have both ``np.nan`` and ``None`` acting as a missing
  value).
* For datetime-like data, pandas uses ``pd.NaT`` ("not-a-time").

As a result, we have a situation that is inconsistent and at times confusing,
ànd lacking fundamental features.

There are **good historical reasons** for this situation. Numpy, which backs the
columns of a pandas DataFrame, has no built-in support for missing values. In
absence of this support, the "NaN" value was the obvious choice as missing value
for float data. Although NaN in itself is not an indicator for missing values
(rather it can be the result of a computation), it's the closest concept
available, so pandas decided to use NaN as the missing value indicator.

Pandas has already extended the numpy type system for many years (e.g. for
categorical data, for timezone support, ..). But more recently, there is an
effort to formalize this in the concept of the "**ExtensionArray**" (see the
[pandas blogpost](https://dev.pandas.io/pandas-blog/pandas-extension-arrays.html)
for more details). Along with this effort, some new data types, such as an
[integer dtype](https://pandas.pydata.org/pandas-docs/stable/user_guide/integer_na.html)
with missing value support, were implemented. And those new dtypes give us a
chance to experiment with better missing value support in pandas!

### A proposal for a new NA scalar to represent missing values

With the above background in mind, I wrote up a proposal to introduce **a new NA
value for representing scalar missing values** that can be used consistently
across all data types.

This new `pd.NA` value (a "singleton) can be used instead of np.nan or None as
the scalar missing value (the value you get back when you access a missing value
in a Series or DataFrame).

The motivation for this change:

- **Consistent user interface.** Currently, the value that is displayed or that
  you get back for a missing scalar (e.g. from scalar access `s[idx]`) depends
  on the data type. Some types support missing values, others don't. This
  proposal would (eventually) ensure that all data types support missing values
  and that you get back `pd.NA` regardless of the dtype.
- **No "mis-use" of the np.nan floating-point value.** The NaN value is a
  specific floating-point value, and not necessarily an indicator for missing
  values (although pandas has always used it that way, also for non-float
  dtypes).
- **A missing value that behaves accordingly.** Our current behaviour of missing
  values is inherited from the behaviour of `np.nan`. Other languages that have
  a NA/NULL value that is distinguished from NaN (e.g. Julia, SQL, R) typically
  have different behaviour in comparison and logical operations. For example,
  comparison with NA could give NA instead of False, and consequently we need to
  have a boolean dtype with NA support. A new NA value opens up the possibility
  of having such NA-specific behaviour.
- An "NA" scalar **matches the terminology** that is used throughout pandas in
  functions and argument names (`isna`, `dropna`, `fillna`, `skipna`, ...).

See the full [proposal](https://hackmd.io/@jorisvandenbossche/Sk0wMeAmB) and the
[GitHub issue](https://github.com/pandas-dev/pandas/issues/28095) where it has
been discussed for more details.

### A few examples

Basic support for `pd.NA` has landed in the development version of pandas now
(to be released in pandas 1.0), while we are still working on further
integration. But so we can already show a few examples of how it looks like.

For example, creating a "nullable" integer Series with missing value support
(which was already introduced in pandas 0.24, but will now start to use the new
`pd.NA`):

```python
>>> s1 = pd.Series([1, 2, None], dtype="Int64")
>>> s1
0     1
1     2
2    NA
dtype: Int64

>>> s1[2]
NA
```

and the same missing value is used for strings:

```python
>>> s2 = pd.Series(["a", pd.NA, "b"], dtype="string")
>>> s2
0     a
1    NA
2     b
dtype: string
```

Comparison operations now propagate missing values:

```python
>>> s1 > 1
0    False
1     True
2       NA
dtype: boolean
```

while before, when using `np.nan` as missing value, such comparisons resulted in
`False` values:

```python
>>> s_nan = pd.Series([1, 2, np.nan])
>>> s_nan
0    1.0
1    2.0
2    NaN
dtype: float64

>>> s_nan > 1
0    False
1     True
2    False
dtype: bool
```

### How does this work?

The integer and boolean data types shown above are still based on numpy arrays,
and numpy still doesn't support missing values. So how does this then work?

The `pd.NA` value is the scalar, user-facing object. It is returned when
accessing or returning a single value that is missing, but is not necessarily
stored as such under the hood.

For example, for the new integer dtype with missing value support, the
implementation uses a "masked array" approach: one numpy array to store the
integer values, and one boolean numpy array (mask) to store for each value
whether it is a valid value or a missing value.

### How can I use this? Feedback welcome!

For now, `pd.NA` as missing value is only used in some of the new,
ExtensionArray-based data types for integers, bools and strings (but we are
planning to add support for more data types).

Those data types are not yet used by default. Meaning that, when creating a
Series or DataFrame or importing from a file, you need to explicitly specify the
data type to be one of those new data types (e.g. `dtype="Int64"` with a
capital). We are looking into making it easier to start using those data types
without needing to always specify them (see e.g.
[GH-29752](https://github.com/pandas-dev/pandas/issues/29752)).

This is all very new. There are still some API questions we are not fully sure
about (e.g. what should (boolean) indexing do with missing values?), and we
probably overlooked some others. **So feedback is very welcome!**

Thanks to all the people that already contributed to the discussions. And
especially thanks to Tom Augspurger for his PRs helping to get this into pandas.
