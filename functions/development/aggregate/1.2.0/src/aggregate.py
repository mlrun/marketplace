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

import os
import pandas as pd
from mlrun.datastore import DataItem

from typing import Union


def aggregate(context,
              df_artifact: Union[DataItem, pd.core.frame.DataFrame],
              save_to: str = 'aggregated-df.pq',
              keys: list = None,
              metrics: list = None,
              labels: list = None,
              metric_aggregations: list = ['mean'],
              label_aggregations: list = ['max'],
              suffix: str = '',
              window: int = 3,
              center: bool = False,
              inplace: bool = False,
              drop_na: bool = True,
              files_to_select: int = 1):
    """Time-series aggregation function
    
    Will perform a rolling aggregation on {df_artifact}, over {window} by the selected {keys}
    applying {metric_aggregations} on {metrics} and {label_aggregations} on {labels}. adding {suffix} to the
    feature names.
    
    if not {inplace}, will return the original {df_artifact}, joined by the aggregated result.

    :param context: After running a job, you need to be able to track it. To gain the maximum value, MLRun uses the
                    job context object inside the code. This provides access to job metadata, parameters,
                    inputs, secrets, and API for logging and monitoring the results, as well as log text, files,
                    artifacts, and labels.
    
    :param df_artifact: MLRun input pointing to pandas dataframe (csv/parquet file path) or a 
                        directory containing parquet files.
                        * When given a directory the latest {files_to_select} will be selected
    :param save_to:     Where to save the result dataframe.
                        * If relative will add to the {artifact_path}
    :param keys:        Subset of indexes from the source dataframe to aggregate by (default=all)
    :param metrics:     Array containing a list of metrics to run the aggregations on. (default=None) 
    :param labels:      Array containing a list of labels to run the aggregations on. (default=None) 
    :param metric_aggregations: Array containing a list of aggregation function names to run on {metrics}.
                        (Ex: 'mean', 'std') (default='mean')
    :param label_aggregations:  Array containing a list of aggregation function names to run on {metrics}.
                        (Ex: 'max', 'min') (default='max') 
    :param suffix:      Suffix to add to the feature name, E.g: <Feature_Name>_<Agg_Function>_<Suffix>
                        (Ex: 'last_60_minutes') (default='')
    :param window:      Window size to perform the rolling aggregate on. (default=3)
    :param center:      If True, Sets the value for the central sample in the window,
                        If False, will set the value to the last sample. (default=False)
    :param inplace:     If True, will return only the aggregated results.
                        If False, will join the aggregated results with the original dataframe
    :param drop_na:     Will drop na lines due to the Rolling.
    :param files_to_select: Specifies the number of *latest* files to select (and concat) for aggregation.
    """
    
    from_model = type(df_artifact) == pd.DataFrame
    if from_model:
        context.logger.info('Aggregating from Buffer')
        input_df = df_artifact
    else:
        if df_artifact.url.endswith('/'):   # is a directory?
            mpath = [os.path.join(df_artifact.url, file) for file in df_artifact.listdir() if file.endswith(('parquet', 'pq'))]
            files_by_updated = sorted(mpath, key=os.path.getmtime, reverse=True)
            context.logger.info(files_by_updated)
            latest = files_by_updated[:files_to_select]
            context.logger.info(f'Aggregating {latest}')
            input_df = pd.concat([context.get_dataitem(df).as_df() for df in latest])
        else:  # A regular artifact
            context.logger.info(f'Aggregating {df_artifact.url}')
            input_df = df_artifact.as_df()
    
    if not (metrics or labels):
        raise ValueError('please specify metrics or labels param')
    
    if keys:
        current_index = input_df.index.names
        indexes_to_drop = [col for col in input_df.index.names if col not in keys]
        df = input_df.reset_index(level=indexes_to_drop)
    else:
        df = input_df
        
    if metrics:
        metrics_df = df.loc[:, metrics].rolling(window=window, center=center).aggregate(metric_aggregations)
        metrics_df.columns = ['_'.join(col).strip() for col in metrics_df.columns.values]
        
        if suffix:
            metrics_df.columns = [f'{metric}_{suffix}' for metric in metrics_df.columns]
            
        if not inplace:
            final_df = pd.merge(input_df, metrics_df, suffixes=('', suffix), left_index=True, right_index=True)
        else:
            final_df = metrics_df

    if labels:
        labels_df = df.loc[:, labels].rolling(window=window,
                                              center=center).aggregate(label_aggregations)
        labels_df.columns = ['_'.join(col).strip() for col in labels_df.columns.values]
        
        if suffix:
            labels_df.columns = [f'{label}_{suffix}' for label in labels_df.columns]
            
        if metrics:
            final_df = pd.merge(final_df, labels_df, suffixes=('', suffix), left_index=True, right_index=True)   
        else:
            if not inplace:
                final_df = pd.merge(input_df, labels_df, suffixes=('', suffix), left_index=True, right_index=True)      
            else:
                final_df = labels_df
                
    if drop_na:
        final_df = final_df.dropna()
        
    context.logger.info('Logging artifact')
    if not from_model:
        context.log_dataset(key='aggregate', 
                            df=final_df, 
                            format='parquet',
                            local_path=save_to)
    else:
        return final_df
