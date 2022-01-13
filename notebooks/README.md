# Example notebooks

These are example notebooks to showcase cuxfilter. Related Datasets can be download using the link below:

## TRY CUXFILTER NOTEBOOKS ONLINE

1. Mortgage_example.ipynb

    [![Open In Studio Lab](https://studiolab.sagemaker.aws/studiolab.svg)](https://studiolab.sagemaker.aws/import/github/rapidsai/cuxfilter/blob/branch-22.02/notebooks/Mortgage_example.ipynb) [<img src="https://img.shields.io/badge/-Setup Studio Lab Environment-gray.svg">](#amazon-sagemaker-studio-lab)
    
    [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rapidsai/cuxfilter/blob/branch-22.02/notebooks/Mortgage_example.ipynb) [<img src="https://img.shields.io/badge/-Setup Colab Environment-gray.svg">](#google-colab)

2. NYC_taxi_example.ipynb

    [![Open In Studio Lab](https://studiolab.sagemaker.aws/studiolab.svg)](https://studiolab.sagemaker.aws/import/github/rapidsai/cuxfilter/blob/branch-22.02/notebooks/NYC_taxi_example.ipynb) [<img src="https://img.shields.io/badge/-Setup Studio Lab Environment-gray.svg">](#amazon-sagemaker-studio-lab)
    
    [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rapidsai/cuxfilter/blob/branch-22.02/notebooks/NYC_taxi_example.ipynb) [<img src="https://img.shields.io/badge/-Setup Colab Environment-gray.svg">](#google-colab)

3. auto_accidents_example.ipynb

    [![Open In Studio Lab](https://studiolab.sagemaker.aws/studiolab.svg)](https://studiolab.sagemaker.aws/import/github/rapidsai/cuxfilter/blob/branch-22.02/notebooks/auto_accidents_example.ipynb) [<img src="https://img.shields.io/badge/-Setup Studio Lab Environment-gray.svg">](#amazon-sagemaker-studio-lab)
    
    [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rapidsai/cuxfilter/blob/branch-22.02/notebooks/auto_accidents_example.ipynb) [<img src="https://img.shields.io/badge/-Setup Colab Environment-gray.svg">](#google-colab)

4. graphs.ipynb

    [![Open In Studio Lab](https://studiolab.sagemaker.aws/studiolab.svg)](https://studiolab.sagemaker.aws/import/github/rapidsai/cuxfilter/blob/branch-22.02/notebooks/graphs.ipynb) [<img src="https://img.shields.io/badge/-Setup Studio Lab Environment-gray.svg">](#amazon-sagemaker-studio-lab)
    
    [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rapidsai/cuxfilter/blob/branch-22.02/notebooks/graphs.ipynb) [<img src="https://img.shields.io/badge/-Setup Colab Environment-gray.svg">](#google-colab)

</br>


## Setup Remote Environments
### Amazon Sagemaker Studio Lab

[Amazon SageMaker Studio Lab](https://studiolab.sagemaker.aws/faq) is a free online web application for learning and experimenting with data science and machine learning using Jupyter notebooks and is free to use.

Once you have registered with your email address, simply sign in to your account, start a CPU or GPU runtime, and open your project - all in your browser.

To setup a rapids environment in studio lab(you only need to do this the first time, since studio lab has 15GB of persistent storage across sessions), open a new terminal:

```bash
conda install ipykernel

# for stable rapids version
conda install -c rapidsai -c nvidia -c numba -c conda-forge \
    cuxfilter python=3.7 cudatoolkit=11.5

# for nightly rapids version
conda install -c rapidsai-nightly -c nvidia -c numba -c conda-forge \
    cuxfilter python=3.7 cudatoolkit=11.5
```

Once installed, you should see a card in the launcher for that environment and kernel after about a minute.

<div class="alert alert-info"> <b>Note:</b> It may take about one minute for the new environment to appear as a kernel option.</div>

</br>

### Google Colab

[Google Colab](https://colab.research.google.com/?utm_source=scs-index), or "Colaboratory", allows you to write and execute Python in your browser, with 
- Zero configuration required
- Free access to GPUs
- Easy sharing

To launch cuxfilter notebooks on the colab environment, you need to follow the the RAPIDS installation instructions guide by clicking [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1rY7Ln6rEE1pOlfSHCYOVaqt8OvDO35J0#forceEdit=true&offline=true&sandboxMode=true). Once the RAPIDS libraries are installed, you can run the cuxfilter notebooks.

> Note: Unlike Studio Lab, environment storage is not persistent and each notebook needs a separate RAPIDS installation every time you start a new session.

> Copy the installation notebook cells to the top of the cuxfilter notebooks and install RAPIDS before executing the cuxfilter code.


</br></br>
## Datasets
- [Mortgage dataset](https://docs.rapids.ai/datasets/mortgage-viz-data)

- [Nyc taxi dataset](https://drive.google.com/file/d/1mTvl66VLzHwQJPcgnGBdmZTNEdNp1tYo/view?usp=sharing)

- [Auto Accidents dataset](https://drive.google.com/file/d/1jxySYJ9e32hI8PQ5QPr9_xrsu37N5fOM/view?usp=sharing)

> Note: Auto Accidents dataset has corrupted coordinate data from the years 2012-2014
