# Example notebooks

These are example notebooks to showcase cuxfilter with [cuDF](https://github.com/rapidsai/cudf). If you want to distribute your workflow across multiple GPUs, have more data than you can fit in memory on a single GPU, or want to visualize data spread across many files at once, you would want to use [Dask-cuDF](https://github.com/rapidsai/cudf/tree/main/python/dask_cudf) with cuxfilter. The examples notebooks can be found [here](./cuxfilter%20with%20dask_cudf/).

## TRY CUXFILTER NOTEBOOKS ONLINE

[<img src="https://img.shields.io/badge/-Setup Studio Lab Environment-gray.svg">](#amazon-sagemaker-studio-lab) [<img src="https://img.shields.io/badge/-Setup Colab Environment-gray.svg">](#google-colab)

1. Mortgage_example.ipynb

    [![Open In Studio Lab](https://studiolab.sagemaker.aws/studiolab.svg)](https://studiolab.sagemaker.aws/import/github/rapidsai/cuxfilter/blob/branch-22.02/notebooks/Mortgage_example.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rapidsai/cuxfilter/blob/branch-22.02/notebooks/Mortgage_example.ipynb)

2. NYC_taxi_example.ipynb

    [![Open In Studio Lab](https://studiolab.sagemaker.aws/studiolab.svg)](https://studiolab.sagemaker.aws/import/github/rapidsai/cuxfilter/blob/branch-22.02/notebooks/NYC_taxi_example.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rapidsai/cuxfilter/blob/branch-22.02/notebooks/NYC_taxi_example.ipynb)

3. auto_accidents_example.ipynb

    [![Open In Studio Lab](https://studiolab.sagemaker.aws/studiolab.svg)](https://studiolab.sagemaker.aws/import/github/rapidsai/cuxfilter/blob/branch-22.02/notebooks/auto_accidents_example.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rapidsai/cuxfilter/blob/branch-22.02/notebooks/auto_accidents_example.ipynb)

4. graphs.ipynb

    [![Open In Studio Lab](https://studiolab.sagemaker.aws/studiolab.svg)](https://studiolab.sagemaker.aws/import/github/rapidsai/cuxfilter/blob/branch-22.02/notebooks/graphs.ipynb)
    [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rapidsai/cuxfilter/blob/branch-22.02/notebooks/graphs.ipynb)
</br>

## Setup Remote Environments

### Amazon Sagemaker Studio Lab

[Amazon SageMaker Studio Lab](https://studiolab.sagemaker.aws/faq) is a free ML development environment that provides the compute, storage (up to 15GB), and security —all at no cost (currently). This includes GPU notebook instances.

Once you have registered with your email address, simply sign in to your account, start a CPU or GPU runtime, and open your project - all in your browser.

To setup a rapids environment in studio lab(you only need to do this the first time, since studio lab has 15GB of persistent storage across sessions), open a new terminal:

```bash
conda install ipykernel

# for stable rapids version
conda install -c rapidsai -c nvidia -c numba -c conda-forge \
    cuxfilter=22.02 python=3.7 cudatoolkit=11.5

# for nightly rapids version
conda install -c rapidsai-nightly -c nvidia -c numba -c conda-forge \
    cuxfilter python=3.7 cudatoolkit=11.5
```

> Above are sample install snippets for cuxfilter, see the [Get RAPIDS version picker](https://rapids.ai/start.html) for installing the latest `cuxfilter` version.

Once installed, you should see a card in the launcher for that environment and kernel after about a minute.

<div class="alert alert-info"> <b>Note:</b> It may take about one minute for the new environment to appear as a kernel option.</div>

### Google Colab

[Google Colab](https://colab.research.google.com/?utm_source=scs-index), or "Colaboratory", allows you to write and execute Python in your browser, with

- Zero configuration required
- Free access to GPUs
- Easy sharing

To launch cuxfilter notebooks on the colab environment, you need to follow the the RAPIDS installation instructions guide by clicking [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1rY7Ln6rEE1pOlfSHCYOVaqt8OvDO35J0#forceEdit=true&offline=true&sandboxMode=true). Once the RAPIDS libraries are installed, you can run the cuxfilter notebooks.

> Note: Unlike Studio Lab, environment storage is not persistent and each notebook needs a separate RAPIDS installation every time you start a new session.

> Copy the installation notebook cells to the top of the cuxfilter notebooks and install RAPIDS before executing the cuxfilter code.

</br>

## Download Datasets

- [Mortgage dataset](https://docs.rapids.ai/datasets/mortgage-viz-data)

- [Nyc taxi dataset](https://drive.google.com/file/d/1mTvl66VLzHwQJPcgnGBdmZTNEdNp1tYo/view?usp=sharing)

- [Auto Accidents dataset](https://drive.google.com/file/d/1jxySYJ9e32hI8PQ5QPr9_xrsu37N5fOM/view?usp=sharing)

> Note: Auto Accidents dataset has corrupted coordinate data from the years 2012-2014
