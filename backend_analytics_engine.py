# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 15:37:10 2023

@author: Maybin Michael
"""

#packages
import pandas as pd
import numpy as np
import os
import traceback
import re
import plotly.figure_factory as ff # Plotting library
import plotly.express as px

class Data_Analytics():
    """
    Class to perform data analytics
    
    Attributes
    ----------
    df : Pandas DataFrame
        Data uploaded by the user
    cont_var : list
        List of continuous variables in the df dataframe
    categ_var : list
        List of categorical variables in the df dataframe
        
    Methods
    -------
        Details of the method are given with each method
    """
    def __init__(self):
        """
        Constructs/define all the necessary attributes for a use case
        
        Parameters
        ----------
        
        """
        self.df = pd.DataFrame()
        self.cont_var = []
        self.categ_var = []

    def return_status(self,
                     error_code, 
                     status_msg = None,
                     error_trace = None,
                     output = None
                     ):
        """
        Creates return dictionary for all the functions
        
        Parameters
        ----------
        error_code : int
            0 - Function executed successfully, any other value -  execution failed
        status_msg : str, optional
            Status message of the function execution. If function failed, specify the reason.
            Default: None, 
        error_trace : str, optional
            Contains traceback of the error.
            Default : None
        output = any type
            Return value of the function if any
            Default : None
            
        Returns
        -------
        dictionary
            Output dictionary with multiple content
        """
        
        d = {"error_code": error_code,
             "status_msg": status_msg,
             "error_trace": error_trace,
             "output": output,
             }
        return d

    def read_document(self, document_path):
        """
        Function to read the document uploaded by the user.

        Parameters
        ----------
        document_path : string
            Path of the document uploaded by the user

        Returns
        -------
        Dictionary
            Dictionary contains Dataframe with date uploaded by user.

        """
        try:
            self.df = pd.read_excel(document_path)
            self.cont_var = self.df.select_dtypes(exclude=['object', 'datetime64']).columns
            self.categ_var = self.df.select_dtypes(include=['object'], exclude=['datetime64[ns]']).columns
            status_msg = "Function executed successfully"
            return self.return_status(0, status_msg)
        except:
            status_msg = "Upload file with .xlsx, .xls format ONLY"
            error_trace = ''.join(traceback.format_exc())
            return self.return_status(101, status_msg, error_trace)
        
    # Function to check data missingness, foreign values
    def check_data_integrity(self):
        """
        This function checks data missingness columnwise
        Returns
        -------
        Dictionary
            Contains details of missing data

        """
        # checking data missingness columnwise
        try:
            output = {}
            data_missingness = self.df.isnull().sum()
            data_missingness = data_missingness.to_frame()
            data_missingness.reset_index(inplace=True)
            data_missingness.columns = ['Features', "Missing values count"]
            output["data_missingness"] = data_missingness
            return self.return_status(0, output=output)
        except: 
            status_msg = "Data missingness could not be performed"
            error_trace = ''.join(traceback.format_exc())
            return self.return_status(102, status_msg, error_trace)
    
    # Function to remove rows with missing data and foreign values and to perform imputation
    def keep_data_integrity(self,
                            remove_missing_rows_continuous = False, 
                            remove_missing_rows_categorical = False, 
                            remove_foreign_rows= False, 
                            impute_missing_rows_continuous= 'mean',
                            impute_missing_rows_categorical= 'mode'
                            ):
        """
        Method to remove rows with missing data and foreign values and to perform imputation
        
        Parameters
        ----------
        remove_missing_rows_continuous : boolean, optional
            Removes missing rows in the case of continuous variables if True. The default is False.
        remove_missing_rows_categorical : boolean, optional
            Removes missing rows in the case of categorical variables if True. The default is False.
        remove_foreign_rows : boolean, optional
            Removes foreign values if True. The default is False.
        impute_missing_rows_continuous : str, optional
            Imputation is performed for continuous columns if any value is selected. The default is 'mean'. 
            mean - imputes missing values with mean. 
            meadian - impute missing values with median
            other methods are not supported now     
        impute_missing_rows_categorical : str, optional
            Imputation is performed for categorical columns if any value is selected. The default is 'mode'.
            mode - imputes missing values with mode
            other methods are not supported now

        Returns
        -------
        Dictionary
            DESCRIPTION.

        """
        
        # Remove/impute rows with missing values
        status_msg =''
        try:
            if remove_missing_rows_continuous == True:
                self.df.dropna(subset=self.cont_var, axis=0, how='any', inplace=True)
                status_msg = status_msg + ' Missing rows have been removed from continuous features.'
            else:
                # ------------ impute with mean and median
                if impute_missing_rows_continuous == 'mean':
                    for i in self.cont_var:
                        self.df[i].fillna(value=self.df[i].mean(), inplace=True)
                elif impute_missing_rows_continuous == 'median':
                    for i in self.cont_var:
                        self.df[i].fillna(value=self.df[i].median(), inplace=True)
                else:
                    pass
                status_msg = status_msg + ' Imputation performed on continuous features.'
                
            if remove_missing_rows_categorical == True:
                self.df.dropna(subset=self.categ_var, axis=0, how='any', inplace=True)
                status_msg = status_msg + ' Missing rows have been removed from categorical features.'
            else:
                # impute with mode
                if impute_missing_rows_categorical == 'mode':
                    for i in self.categ_var:
                        self.df[i].fillna(value=self.df[i].mode()[0], inplace=True)
                    status_msg = status_msg + ' Imputation performed on categorical features.'

        except:
            status_msg = "Removal of rows with missing data or imputation could not be performed"
            error_trace = ''.join(traceback.format_exc())
            return self.return_status(104, status_msg, error_trace)
        
        # Remove/impute rows with foreign values
        try:
            values_count_index =[]
            for col in self.categ_var:
                l = self.df[col].value_counts().index.tolist()
                values_count_index.extend(l)
            values_count_index = set(values_count_index)
            foreign_values = [val for val in values_count_index if type(val)==str and not re.findall('\w+', val)]
            self.df = self.df.replace(foreign_values, np.nan)

            if remove_foreign_rows == True:
                # remove foreign rows
                self.df.dropna(axis=0, inplace=True)
                status_msg = status_msg + ' Foreign values have been removed.'
            else:
                # perform imputation for categorical  features
                for i in self.categ_var:
                    self.df[i].fillna(value=self.df[i].mode()[0], inplace=True)
                status_msg = status_msg + ' Foreign labels in categorical features have been imputed.'
        except:
            status_msg = "Removal of rows with foreign data or imputation could not be performed"
            error_trace = ''.join(traceback.format_exc())
            return self.return_status(105, status_msg, error_trace)
        
        # Return updated df after resetting categ and cont var lists
        self.cont_var = self.df.select_dtypes(exclude = ['object', 'datetime64[ns]'])
        self.categ_var = self.df.select_dtypes(include = ['object'], exclude = ['datetime64[ns]'])
        return self.return_status(0, status_msg, output=self.df)
    
    def describe_data(self):
        """
        Performs Descriptive analytics  

        Returns
        -------
        Dictionary
            DESCRIPTION.
        """
        
        try:
            # Summary of continuous type data
            cont_data_summary = pd.DataFrame(data = None, index = self.cont_var)
            cont_data_summary = cont_data_summary.assign(Mean = self.df[self.cont_var].mean())
            cont_data_summary = cont_data_summary.assign(Standard_Deviation = self.df[self.cont_var].std())
            cont_data_summary = cont_data_summary.assign(Variance = self.df[self.cont_var].var())
            cont_data_summary = cont_data_summary.assign(Min = self.df[self.cont_var].min())
            cont_data_summary = cont_data_summary.assign(Max = self.df[self.cont_var].max())
            cont_data_summary = cont_data_summary.assign(First_Quartile = self.df[self.cont_var].quantile(0.25))
            cont_data_summary = cont_data_summary.assign(Median = self.df[self.cont_var].median())
            cont_data_summary = cont_data_summary.assign(Third_Quartile = self.df[self.cont_var].quantile(0.75))
            
            # Summary of categorical data
            categ_data_summary = pd.DataFrame(data = None, index = self.categ_var)
            categ_data_summary = categ_data_summary.assign(Count = self.df[self.categ_var].count())
            categ_data_summary = categ_data_summary.assign(Count_of_Unique_Values = self.df[self.categ_var].nunique(axis=0))
            categ_data_summary = categ_data_summary.assign(Mode = self.df[self.categ_var].mode().transpose())
            
            output = {"cont_data_summary": cont_data_summary,
                      "categ_data_summary": categ_data_summary
                      }
            return self.return_status(0, output=output)
        except:
            status_msg = "Descriptive statistics of data could not be performed"
            error_trace = ''.join(traceback.format_exc())
            return self.return_status(106, status_msg, error_trace)
        
    def show_distribution(self, feature):
        """
        This function returns distribution plot

        Parameters
        ----------
        feature : str
            Pass the feature name

        Returns
        -------
        image of the distribution of the feature

        """
        try:
            hist_data = [self.df[feature]]
            group_labels = [feature]
            fig = ff.create_distplot(hist_data, group_labels)
            return self.return_status(0, output=fig)
        except:
            status_msg = "Plotting of distribution could not be performed"
            error_trace = ''.join(traceback.format_exc())
            return self.return_status(110, status_msg, error_trace)
            
    def show_trend(self, x_feature, y_feature):
        """
        

        Parameters
        ----------
        x_feature : str
            Feature to be set as x-axis
        y_feature : str
            Feature to be set as y-axis.

        Returns
        -------
        image
            Trendline image

        """
        try:
            fig = px.scatter(self.df, x=x_feature, y=y_feature, trendline="ols")
            return self.return_status(0, output=fig)
        except:
            status_msg = "Plotting of trendline could not be performed"
            error_trace = ''.join(traceback.format_exc())
            return self.return_status(103, status_msg, error_trace)
        
    def show_outliers(self, feature):
        """
        Performs data engineering - Plotting outliers using box and whisker method

        Returns
        -------
        image
            Box and whisker image

        """
        try:
            # plotting outliers using box and whisker 
            fig = px.histogram(self.df, x=feature, marginal='box', hover_data=self.df.columns)
            return self.return_status(0, output=fig)
        except:
            status_msg = "Plotting of outliers could not be performed"
            error_trace = ''.join(traceback.format_exc())
            return self.return_status(107, status_msg, error_trace)
        
    def outlier_removal_imputation(self,
                                remove_outliers = True, 
                                imputation_method = [],
                                selected_columns = [], 
                                lower_extreme = [], 
                                higher_extreme = [],
                                f=1.3
                                ):
        """
        Performs Data engineering - remove outliers using box and whisker method or Extreme value capping

        Parameters
        ----------
        remove_outliers : boolean, optional
            Removes outliers if True. The default is True. False - Do not remove outliers                                
        imputation_method : list, optional
            List of imputation method. The default is [] 
            mean - imputes outlier with mean 
            meadian - impute  outlier with median
            other methods are not supported now                                
        selected_columns : list, optional
            List of columns which should undergo outlier removal. The default is []
        lower_extreme : list, optional
            List of lower extreme values of respective columns. The default is [].
        higher_extreme : list, optional
            List of higher extreme values of respective columns. The default is [].
        f : factor deciding whisker length, Default is 1.3

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        try:
            status_msg=''
            if remove_outliers == True:
                # remove outliers using box and whisker
                i=0
                for k in selected_columns:
                    #calculating 1st and 3rd quantile in q
                    q = self.df[k].quantile([0.25, 0.75])
                    #Calculating the whisker's Min and Max value in d
                    d = list([q.iloc[0] - (f*(q.iloc[1]-q.iloc[0])), q.iloc[1] + (f*(q.iloc[1] - q.iloc[0]))])
                    # replace the outlier values by nan
                    self.df.loc[(self.df[k] < d[0]) | (self.df[k] > d[1]), k] = np.nan
                status_msg = status_msg + " Outlier removal is performed."
                # Perform imputation
                if imputation_method != []: 
                    if imputation_method[i] == 'mean':
                        self.df[k].fillna(value=self.df[k].mean(), inplace=True)
                    elif imputation_method[i] == 'median':
                        self.df[k].fillna(value=self.df[k].median(), inplace=True)
                    status_msg = status_msg + " Imputation is performed."
                else:
                    #perform extreme value capping
                    pass
            return self.return_status(0, status_msg)

        except:
            status_msg = "Outlier removal or imputation could not be performed"
            error_trace = ''.join(traceback.format_exc())
            return self.return_status(109, status_msg, error_trace)
    
    def download_file(self, folder_path):
        """
        Downloads the data file

        Parameters
        ----------
        folderpath : str
            Folder path where the file to be downloaded

        Returns
        -------
        dataframe
            Dataframe which is converted and downloaded to the path

        """
        try:
            # Ensure output folder path exist
            if not os.path.isdir(folder_path):
                os.makedirs(folder_path)
            file_path = os.path.join(folder_path, 'file.xlsx')    
            self.df.to_excel(file_path)
            df_copy = self.df
            return self.return_status(0, output=df_copy)
        except:
            status_msg = "Downloading of the file could not be performed"
            error_trace = ''.join(traceback.format_exc())
            return self.return_status(108, status_msg, error_trace)
        
  