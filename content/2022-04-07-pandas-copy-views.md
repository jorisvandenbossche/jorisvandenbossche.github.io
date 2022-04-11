Title: On copies and views: getting rid of the SettingWithCopyWarning
Date: 2022-04-07 09:00
Tags: python, pandas
Slug: pandas-copy-views
Comments: false
Githubcomments: true

<em>
<!-- PELICAN_BEGIN_SUMMARY -->
Pandas' current behavior on whether indexing returns a view or copy is confusing, even for experienced users. But it doesn’t have to be this way. We can make this aspect of pandas easier to grasp by simplifying the copy/view rules, and at the same time make pandas more memory-efficient. And get rid of the SettingWithCopyWarning.
<!-- PELICAN_END_SUMMARY -->
</em>

### Context

The infamous "SettingWithCopyWarning" has probably confused / annoyed / enraged (delete what does not apply for you) many users of pandas. This can also be seen by the [many](https://www.dataquest.io/blog/settingwithcopywarning/) [blogposts](https://realpython.com/pandas-settingwithcopywarning/) [on](https://www.geeksforgeeks.org/how-to-fix-settingwithcopywarning-in-pandas/) [this](https://towardsdatascience.com/explaining-the-settingwithcopywarning-in-pandas-ebc19d799d25) [topic](https://stackoverflow.com/questions/20625582/how-to-deal-with-settingwithcopywarning-in-pandas) that go into the details on what it is and how to deal with it.

<!-- Users of pandas probably have run into the infamous “SettingWithCopyWarning”. Several lengthy blog posts and popular stack overflow questions go into the details on what it is and how to deal with it. At the core of this, pandas’ current behavior on whether indexing returns a view or copy is confusing.  Pandas’ internals will, for most users, be kind of a black box, and it is hard to reason about how the column’s memory is stored. Even for experienced users, it’s hard to tell whether a view or copy will be returned. -->

As a quick recap, let's consider the following example where we filter a DataFrame `df` to create `subset`, and then modify `subset`:

```pycon
>>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4], "C": [5, 6]})
>>> subset = df[df["A"] > 1]
>>> subset["C"] = 10
SettingWithCopyWarning: 
A value is trying to be set on a copy of a slice from a DataFrame.
Try using .loc[row_indexer,col_indexer] = value instead

See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
```

Does this last line only change `subset`, or also `df`?

In general, it is not always clear when a new object (`subset` in the example above) is a *view* on the original data (`df`) or a *copy*. With a *view*, we mean the new object isn't a copy of the original data but is "viewing" the same data in memory. That means that when you edit this view, you are actually updating the original data as well.

Even expert pandas developers (let alone new users) probably won't be able to correctly predict this in all cases whether a certain operation will result in a view or a copy. 
And because this is not always clear, pandas warns users with the SettingWithCopyWarning about potential unexpected behaviour.

### A proposal for a simpler behaviour

Therefore, here is a new proposal to simplify this situation and move towards a single rule: **any DataFrame or Series derived from another in any way (e.g. with an indexing operation) always *behaves as* a copy**.

A single rule, but one that we can phraze in different ways. For example, an implication of this is: **mutating a DataFrame only changes the object itself, and not any other.** Or, put differently in another way: if you want to change values in a DataFrame or Series, you can only do that by directly mutating the DataFrame/Series at hand.

So with this in mind, we can go back to the original example:

```pycon
>>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4], "C": [5, 6]})
>>> subset = df[df["A"] > 1]
>>> subset["C"] = 10
```

and try to answer the question again: will mutating `subset` also modify `df`? Following this proposed new rule, we can say: since `subset` is not the same object as `df`, mutating `subset` will not change `df`.

### Several advantages

This proposal has several advantages:

- A simpler, more consistent user experience
- We can get rid of the SettingWithCopyWarning (since there is no confusion about whether we are mutating a view or a copy)
- We would no longer need defensive copying in many places in pandas, improving memory usage

I will go into more detail on those different aspects in follow-up blog posts.

**Important!** This is only a *proposal*, and not yet reality in pandas. Does this sound interesting? Then you can read the full proposal [here](https://docs.google.com/document/d/1ZCQ9mx3LBMy-nhwRl33_jgcvWo9IWdEfxDNQ2thyTb0/edit#heading=h.iexejdstiz8u), and feedback is very welcome!
