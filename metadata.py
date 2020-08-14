# -*- coding: utf-8 -*-
"""Utilities for file handling.

@Author       :  Sean Howard
@CreationDate :  2020/04/19
@UpdateDate   :  2020/04/19

Purpose
-------
The purpose of this library is to provide functions for streamlining
exploratory data analysis.

"""

import pandas as pd
import numpy as np


def generate_meta_table(d_f, location):
    """Generate metadata table for the provided data frame.

    Summary
    -------
    This function is used to generate a standard meta table for the provided
    data frame.

    Requires
    --------
    pandas
    numpy
    get_basic_meta
    get_char_meta
    get_numeric_meta

    Parameters
    ----------
    d_f : pandas.DataFrame
        This is a pandas data frame for which metadata should be created.

    Returns
    -------
    msg : STRING
        A message string describing results of the function. Any msg starting
        with "Error" means that the function didn't work properly
    meta_dict : DICTIONARY
        A dictionary object with standard metadata attributes for both table
        level and column level.

    """
    # Create the metadata table to retain information about each column
    meta = pd.DataFrame(index=d_f.columns)
    meta.index.name = "column_names"

    # dataframe record count
    rec_cnt = d_f.shape[0]
    col_cnt = d_f.shape[1]

    # get the basic metadata
    basic = get_basic_meta(d_f)

    # generate the character based metadata - generates values for all types
    char = get_char_meta(d_f)

    # join metadata content on the index
    init_meta = basic.join(char, how="left")

    # identify primary key and categorical attributes
    primary_key = identify_pk_meta(init_meta, rec_cnt)
    categorical = identify_categorical_meta(init_meta, rec_cnt)

    # generate metadata values for numeric attributes if they exist
    if any(basic["is_numeric"]):
        num = get_numeric_meta(d_f)
        # combine into list
        elements = [init_meta, primary_key, categorical, num]
    else:
        elements = [init_meta, primary_key, categorical, num]

    # final metadata
    meta = meta.join(elements, how="left")
    meta_list = list(meta.to_dict().items())

    # convert to dictionary and at table level elements
    meta_dict = dict([("source", location),
                      ("rows", rec_cnt),
                      ("columns", col_cnt)]
                     + meta_list)

    # output
    msg = ("Message: generate_meta_table | ran successfully")
    return meta_dict, msg


def get_basic_meta(d_f):
    """Get the basic metadata from a data frame.

    Summary
    -------
    This function is used to generate a basic meta table for the provided
    data frame.

    Requires
    --------
    pandas

    Parameters
    ----------
    d_f : pandas.DataFrame
        This is a pandas data frame for which metadata should be created.

    Returns
    -------
    basic : pandas.DataFrame
        A pandas data frame with basic metadata attributes.

    Parameters
    ----------
    d_f : pandas.DataFrame
        This is a pandas data frame for which metadata should be created.

    Returns
    -------
    basic : pandas.DataFrame
        A pandas data frame with basic metadata attributes.

    """
    # create simple metadata table
    col = ["data_type", "is_numeric", "description", "unique_count",
           "na_count"]
    basic = pd.DataFrame(index=d_f.columns, columns=col)
    basic.index.name = "column_names"
    # get the basic metrics and assign to meta table
    basic["data_type"] = d_f.dtypes.astype('str')
    basic["is_numeric"] = (basic["data_type"].isin(["float64", "int64"]))
    basic["unique_count"] = d_f.nunique()
    basic["na_count"] = d_f.isna().sum()
    return basic


def get_char_meta(d_f):
    """Get the character length stats from a data frame.

    Summary
    -------
    This function is used to generate metadata about the data frame regarding
    character string length. All columns are converted to string type and the
    string length of each cell is calculated before deriving min, max and avg
    statistics.

    Requires
    --------
    pandas

    Parameters
    ----------
    d_f : pandas.DataFrame
        This is a pandas data frame for which metadata should be created.

    Returns
    -------
    char : pandas.DataFrame
        A pandas data frame with character length metadata attributes.

    """
    # create simple metadata table
    col = ["char_min_len", "char_avg_len", "char_max_len"]
    char = pd.DataFrame(index=d_f.columns, columns=col)
    char.index.name = "column_names"
    # calculate the string length of all cells
    string_length = d_f.applymap(lambda x: len(str(x)))
    # assign metrics to meta table
    char["char_min_len"] = string_length.describe().loc["min", :]
    char["char_avg_len"] = string_length.describe().loc["mean", :]
    char["char_max_len"] = string_length.describe().loc["max", :]
    return char


def get_numeric_meta(d_f):
    """Get the numeric descriptive stats from a data frame.

    Summary
    -------
    This function is used to generate metadata about numeric attributes in the
    data frame. Basic descriptive statistics are generated.

    Requires
    --------
    pandas

    Parameters
    ----------
    d_f : pandas.DataFrame
        This is a pandas data frame for which metadata should be created.

    Returns
    -------
    num : pandas.DataFrame
        A pandas data frame with numeric metadata attributes.

    """
    # descriptive stats to be returned
    col = ["num_sum", "num_min", "num_01_p", "num_10_p", "num_25_p",
           "num_50_p", "num_avg", "num_75_p", "num_90_p", "num_99_p",
           "num_max", "num_range", "num_stdev"
           ]
    # get descriptive stats and relable to match with meta table columns
    num_metrics = d_f.describe()
    num_metrics.index = ["count", "num_avg", "num_stdev", "num_min",
                         "num_25_p", "num_50_p", "num_75_p", "num_max"
                         ]
    # swap columns and rows
    num_metrics_wide = num_metrics.transpose()
    col_nam = num_metrics_wide.index
    # add additional numeric metrics
    num_metrics_wide["num_sum"] = d_f[col_nam].sum()
    num_metrics_wide["num_01_p"] = d_f[col_nam].quantile(q=0.01)
    num_metrics_wide["num_10_p"] = d_f[col_nam].quantile(q=0.10)
    num_metrics_wide["num_90_p"] = d_f[col_nam].quantile(q=0.90)
    num_metrics_wide["num_99_p"] = d_f[col_nam].quantile(q=0.99)
    num_metrics_wide["num_range"] = (num_metrics_wide["num_max"]
                                     - num_metrics_wide["num_min"])

    # output only the desired subset of metrics
    return num_metrics_wide[col]


def identify_pk_meta(meta_df, recs):
    """Identify which attributes are likely primary keys.

    Summary
    -------
    This function is used to flag which attributes are likely primary keys.

    Requires
    --------
    pandas
    numpy

    Parameters
    ----------
     meta_df : pandas.DataFrame
        A pandas data frame with standard metadata attributes.
    recs : INTEGER
        The number of records in the data frame that metadata is being created
        for.

    Returns
    -------
    primary_key : pandas.Series
        A pandas series indicating which attributes are likely primary keys.

    """
    # Primary keys are assumed to be unique for all recrods
    # no NA values, if an object then the constant string length
    # otherwise a numeric has to be an integer
    primary_key = np.logical_and(
        np.logical_and(meta_df["unique_count"] == recs,
                       meta_df["na_count"] == 0
                       ),
        np.logical_or(meta_df["char_min_len"] == meta_df["char_max_len"],
                      meta_df["data_type"] == "int64"
                      )
        )
    # If there is no primary key identified then loosen up the rules
    if any(primary_key) is False:
        # Primary keys stil need to be unique without NA
        primary_key = np.logical_and(meta_df["unique_count"] == recs,
                                     meta_df["na_count"] == 0
                                     )
        # do not allow floating point numbers to be possible primary key
        primary_key[meta_df["data_type"] == "float64"] = False
        # do not allow objects with max length > 254 to be possible primary key
        primary_key[meta_df["char_max_len"] > 254] = False
    # assign name and output
    primary_key.name = "possible_primary_key"
    return primary_key


def identify_categorical_meta(meta_df, recs):
    """Identify which attributes are likely categorical variables.

    Summary
    -------
    This function is used to flag which attributes are likely variables.

    Requires
    --------
    pandas
    numpy

    Parameters
    ----------
     meta_df : pandas.DataFrame
        A pandas data frame with standard metadata attributes.
    recs : INTEGER
        The number of records in the data frame that metadata is being created
        for.

    Returns
    -------
    categorical : pandas.Series
        A pandas series indicating which attributes are likely categorical.

    """
    # determine if an attribute is a possible categorical variable
    if recs > 900:
        categorical = np.logical_and(meta_df["unique_count"] < 30,
                                     meta_df["na_count"] < 0.3 * recs)
    else:
        categorical = np.logical_and(meta_df["unique_count"] < 11,
                                     meta_df["na_count"] < 0.3 * recs)
    # assign name and output
    categorical.name = "possible_categorical"
    return categorical
