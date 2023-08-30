# Univariate vs multivariate prediction for containerised applications auto-scaling:: a comparative study

 ## Project description
 
This paper presents a comparative study assessing univariate and multivariate proactive auto-scaling of containerised applications. A custom-made multivariate auto-scaling tool called Multivariate Forecasting Tool (MFT) was developed and compared with a production-grade univariate system called Predict Kube (PK). Both applications were evaluated using four popular open-source benchmark applications (Daytrader, Online Boutique, Quarkus-HTTP-Demo and Travels).

# Installation  
  
## How to install the MFT?

    $ virtualenv venv
    $ source venv/bin/activate
    $ pip3 install -r requirements.txt

# Project Files

Summary of the main repository files.


| Files                                | Content description                                                                   |
|--------------------------------------|---------------------------------------------------------------------------------------|
| [database](database)                 | It contains the datasets used for training the multivariate and univariate models.    |
| [experiment_files](experiment_files) | It contains the application files, configuration files, monitoring and workload files.|
| [knowledge](knowledge)               | It contains the trained multivariate models used in the MFT.                          |
| [mft](mft)                           | It contains the MFT source code.                                                      |
| [model_training](model_training)     | It contains the source code for multivariate model training.                          |
| [results](results)                   | It contains the results of experiments.                                               |
| [process_results](process_results)   | It contains the files for processing the experiment results.                          |





