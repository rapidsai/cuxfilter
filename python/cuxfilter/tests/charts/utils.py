# SPDX-FileCopyrightText: Copyright (c) 2022-2025, NVIDIA CORPORATION. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import cudf
import dask_cudf


def initialize_df(type, *df_args):
    df = cudf.DataFrame(*df_args)
    if type == cudf.DataFrame:
        return df
    return dask_cudf.from_cudf(df, npartitions=2)


def df_equals(df1, df2):
    df1 = (
        df1.compute().reset_index(drop=True)
        if isinstance(df1, dask_cudf.DataFrame)
        else df1.reset_index(drop=True)
    )
    df2 = (
        df2.compute().reset_index(drop=True)
        if isinstance(df2, dask_cudf.DataFrame)
        else df2.reset_index(drop=True)
    )

    return df1.equals(df2)


df_types = [cudf.DataFrame, dask_cudf.DataFrame]
