# Copyright 2021 Iguazio
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
import os
import shutil
from pathlib import Path

from mlrun import new_task, run_local

from describe import summarize

DATA_URL = "https://s3.wasabisys.com/iguazio/data/iris/iris_dataset.csv"
PLOTS_PATH = "plots"


def _validate_paths(paths: {}):
    base_folder = PLOTS_PATH
    for path in paths:
        full_path = os.path.join(base_folder, path)
        if Path(full_path).is_file():
            print("File exist")
        else:
            raise FileNotFoundError


def test_run_local():
    if Path(PLOTS_PATH).is_dir():
        shutil.rmtree(PLOTS_PATH)
    task = new_task(
        name="task-describe",
        handler=summarize,
        inputs={"table": DATA_URL},
        params={"update_dataset": True, "label_column": "label"},
    )
    run_local(task)
    _validate_paths(
        {
            "corr.html",
            "correlation-matrix.csv",
            "hist.html",
            "imbalance.html",
            "imbalance-weights-vec.csv",
            "violin.html",
        }
    )
