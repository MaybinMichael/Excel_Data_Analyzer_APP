import streamlit as st
from backend_analytics_engine import Data_Analytics
import io
import logging
#import logging.config

try:
    #create logger
    logging.basicConfig(filename = "log_file",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    logger = logging.getLogger('Front-end:')
    logger.info("\n\nNew session started")

    # Add App TiTle
    st.title("Excel Data Analyzer")
    st.text("This app helps you to analyze data and to get insights and recommendations!")

    # Upload File
    file_uploaded = st.file_uploader("Choose a file...",
                                     help="Upload files with format such as .xlsx and .xls")
    if file_uploaded != None:
        da = Data_Analytics()
        output = da.read_document(file_uploaded)
        file_uploaded = None
        if output["error_code"]== 0:
            st.success("File upload is successful")
            logger.info("File upload is successful")
        else:
            st.error(output["status_msg"])
            logger.error(output["status_msg"])


    # Show data
    show_data_call = st.button("Show Data", key="show1")
    if show_data_call:
        data=da.df
        st.dataframe(data)
        logger.info("performed Show Data")

    # Ask query
    user_query = st.text_input("Post your query ")
    if user_query != "":
        st.info("""Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor 
        incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud 
        exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. 
        Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. 
        Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt 
        mollit anim id est laborum.""")
        logger.info("Query posted by the user")

    # Check data integrity
    st.subheader("Check data integrity", divider='rainbow')
    data_integrity_check_call = st.button("Check Data Integrity")
    if data_integrity_check_call:
        output = da.check_data_integrity()
        logger.info("Call for data integrity check")
        if output["error_code"]==0:
            st.dataframe(output["output"]["data_missingness"])
            logger.info("performed data integrity check")
        else:
            st.error(output["status_msg"])
            logger.error(output["status_msg"])

    # Imputation
    st.subheader("Data Cleansing", divider='rainbow')
    col3, col4 = st.columns(2)
    with col3:
        remove_missing_rows_continuous = st.toggle("Remove missing rows (continuous features)")
        impute_missing_rows_continuous="mean"
    with col4:
        if not remove_missing_rows_continuous:
            impute_missing_rows_continuous = st.selectbox("Impute method (continuous features)", ("mean", "median"))
    with col3:
        remove_missing_rows_categorical = st.toggle("Remove missing rows (categorical features)")
        impute_missing_rows_categorical='mode'
    with col4:
        if not remove_missing_rows_categorical:
            impute_missing_rows_categorical = st.selectbox("Impute method (categorical features)", ("mode", "mode"))
    remove_foreign_rows = st.toggle("Remove rows with foreign values")
    perform_imputation = st.button("Perform imputation/ Remove missing or foreign values")
    if perform_imputation:
        logger.info("call for performing imputation/ Remove missing or foreign values")
        logger.debug("remove_missing_rows_continuous: ", str(remove_missing_rows_continuous),
                                    "\nremove_missing_rows_categorical: ", str(remove_missing_rows_categorical),
                                    "\nremove_foreign_rows: ",str(remove_foreign_rows),
                                    "\nimpute_missing_rows_continuous: ",str(impute_missing_rows_continuous),
                                    "\nimpute_missing_rows_categorical: ",str(impute_missing_rows_categorical)
                                    )
        output = da.keep_data_integrity(remove_missing_rows_continuous=remove_missing_rows_continuous,
                                    remove_missing_rows_categorical=remove_missing_rows_categorical,
                                    remove_foreign_rows=remove_foreign_rows,
                                    impute_missing_rows_continuous=impute_missing_rows_continuous,
                                    impute_missing_rows_categorical=impute_missing_rows_categorical
                                    )
        if output["error_code"]==0:
            st.success(output["status_msg"])
            logger.info(output["status_msg"])
        else:
            st.error(output["status_msg"])
            logger.error(output["status_msg"])
    def convert_df(df):
        return df.to_csv().encode('utf-8')

    # Descriptive analytics
    st.subheader("Descriptive analytics", divider='rainbow')
    descriptive_analytics_call = st.button("Perform Descriptive Analytics")
    if descriptive_analytics_call:
        logger.info("call for descriptive analytics")
        output = da.describe_data()
        if output["error_code"]==0:
            st.dataframe(output["output"]["cont_data_summary"])
            excel1 =convert_df(output["output"]["cont_data_summary"])
            download1 = st.download_button(label="Download",
                                  data=excel1,
                                  file_name='continuous_data_summary.csv')
            st.dataframe(output["output"]["categ_data_summary"])
            excel2 = convert_df(output["output"]["categ_data_summary"])
            download2 = st.download_button(label="Download",
                                           data=excel1,
                                           file_name='categorical_data_summary.csv')
        else:
            st.error(output["status_msg"])
            logger.error(output["status_msg"])

    # Insights from graphs
    st.subheader("Visualization", divider='rainbow')

    #Download image function
    def download_img(fig, fig_name):
        buffer = io.BytesIO() # creating an in memory buffer
        fig.write_image(file=buffer, format='pdf') # save the figure as a png to the buffer
        st.download_button(label="Download Image",
                                           data=buffer,
                                           file_name=fig_name,
                                           mime="application/pdf")

    # Show distribution
    show_distribution_flag = st.checkbox("Show distribution of features")
    if show_distribution_flag:
        logger.info("call for distribution plot")
        features=set(da.cont_var)
        feature = st.selectbox("Choose a feature", features, key="distribution_graph")
        output = da.show_distribution(feature=feature)
        if output["error_code"] ==0:
            st.plotly_chart(output["output"])
            logger.info("distribution plot generated")
            # Download image
            download_img(output["output"], "Distribution_plot.pdf")
        else:
            st.error(output["status_msg"])
            logger.error(output["status_msg"])

    # Show trend
    st.divider()
    show_trend_flag = st.checkbox("Show trend of features")
    if show_trend_flag:
        logger.info("call for trend plot")
        col1, col2 = st.columns(2)
        with col1:
            x_feature = st.radio("Choose x-axis", da.cont_var)
        with col2:
            y_feature = st.radio("Choose y-axis", da.cont_var)
        output = da.show_trend(x_feature=x_feature,
                               y_feature=y_feature)
        if output["error_code"] ==0:
            st.plotly_chart(output["output"])
            logger.info("trend plot generated")
            # Download image
            download_img(output["output"], "Trend_plot.pdf")
        else:
            st.error(output["status_msg"])
            logger.error(output["status_msg"])

    # Show outliers
    st.divider()
    show_outliers_flag = st.checkbox("Show outliers of data feature-wise")
    if show_outliers_flag:
        logger.info("call for outlier plot")
        features_set = set(da.cont_var)
        feature_for_outliers = st.selectbox("Choose a feature", features_set, key="outlier_graph")
        output = da.show_outliers(feature=feature_for_outliers)
        if output["error_code"] == 0:
            st.plotly_chart(output["output"])
            logger.info("outlier plot generated")
            # Download image
            download_img(output["output"], "outliers_plot.pdf")
        else:
            st.error(output["status_msg"])
            logger.error(output["status_msg"])
    st.divider()

    # Outlier removal and imputation
    st.subheader("Outlier Removal and Imputation", divider='rainbow')
    show_outlier_flag = st.checkbox("Do you want to remove outliers?")
    if show_outlier_flag:
        imputation_method = st.selectbox("Imputation method", ("mean", "median"))
        feature_list = st.multiselect(label="Choose features for outlier removal",
                                      options=da.cont_var)
        f = st.slider(label="Factor deciding whisker length",
                      min_value=0.0,
                      max_value=5.0,
                      step=0.1)
        start_call = st.button("Start")
        if start_call:
            logger.info("call for outlier removal")
            output = da.outlier_removal_imputation(
                                    remove_outliers = show_outlier_flag,
                                    imputation_method = imputation_method,
                                    selected_columns = feature_list,
                                    lower_extreme = [],
                                    higher_extreme = [],
                                    f=f
                                    )
            if output["error_code"] ==0:
                st.success(output["status_msg"])
                logger.info(output["status_msg"])
            else:
                st.error(output["status_msg"])
                logger.error(output["status_msg"])
except Exception as e:
    print(e)
