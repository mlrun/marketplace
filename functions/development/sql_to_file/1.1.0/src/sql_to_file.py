# Copyright 2019 Iguazio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Generated by nuclio.export.NuclioExporter

import pandas as pd
import pyhive
from sqlalchemy.engine import create_engine
from mlrun.execution import MLClientCtx


def sql_to_file(
    context: MLClientCtx,
    sql_query: str,
    database_url: str,
    file_ext: str = "parquet",
) -> None:
    """SQL Ingest - Ingest data using SQL query

    :param context:           the function context
    :param sql_query:         the sql query used to retrieve the data
    :param database_url:      database connection URL
    :param file_ext:          ("parquet") format for result file
    """

    engine = create_engine(database_url)
    df = pd.read_sql(sql_query, engine)

    context.log_dataset(
        "query result",
        df=df,
        format=file_ext,
        artifact_path=context.artifact_subpath("data"),
    )