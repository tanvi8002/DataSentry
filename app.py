
import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# ==========================================
# 1. APPLICATION CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="DataSentry",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 DataSentry")
st.subheader("Automated Data Quality Checker")

st.write(
    "Upload your CSV or Excel file to inspect, "
    "validate and clean your dataset."
)


# ==========================================
# 2. FILE UPLOAD
# ==========================================

uploaded_file = st.file_uploader(
    "Choose a dataset",
    type=["csv", "xlsx"]
)


if uploaded_file is not None:

    try:

        # Read uploaded file safely
        file_bytes = uploaded_file.getvalue()

        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(BytesIO(file_bytes))

        else:
            df = pd.read_excel(BytesIO(file_bytes))

        if df.empty:
            st.warning("The uploaded dataset is empty.")

        else:

            st.success("Dataset uploaded successfully!")

            # ==========================================
            # 3. DATASET PREVIEW
            # ==========================================

            st.subheader("Dataset Preview")

            st.dataframe(
                df,
                use_container_width=True
            )

            # ==========================================
            # 4. DATASET OVERVIEW
            # ==========================================

            total_rows = df.shape[0]
            total_columns = df.shape[1]

            missing_values = df.isnull().sum().sum()

            duplicate_check_columns = [
                column for column in df.columns
                if column.lower() not in ["customer_id", "id"]
            ]

            if not duplicate_check_columns:
                duplicate_check_columns = df.columns.tolist()

            duplicate_rows = df.duplicated(
                subset=duplicate_check_columns
            ).sum()

            duplicate_records = df[
                df.duplicated(
                    subset=duplicate_check_columns,
                    keep=False
                )
            ]

            st.subheader("Dataset Overview")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Total Rows", total_rows)
            col2.metric("Total Columns", total_columns)
            col3.metric("Missing Values", int(missing_values))
            col4.metric("Duplicate Rows", int(duplicate_rows))

            # ==========================================
            # 5. MISSING VALUES REPORT
            # ==========================================

            st.subheader("Missing Values Report")

            missing_report = pd.DataFrame({
                "Column Name": df.columns,
                "Missing Values": df.isnull().sum().values
            })

            st.dataframe(
                missing_report,
                use_container_width=True
            )

            # ==========================================
            # 6. DUPLICATE RECORD DETECTION
            # ==========================================

            st.subheader("Duplicate Records")

            st.write(
                f"Number of duplicate rows: {duplicate_rows}"
            )

            if not duplicate_records.empty:

                st.warning("Duplicate records detected!")

                st.dataframe(
                    duplicate_records,
                    use_container_width=True
                )

            else:
                st.success("No duplicate records found.")

            # ==========================================
            # 7. INVALID DATA DETECTION
            # ==========================================

            st.subheader("Invalid Data Detection")

            # Email validation
            if "email" in df.columns:

                email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

                email_values = (
                    df["email"]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )

                invalid_email_mask = (
                    email_values.ne("")
                    & ~email_values.str.match(email_pattern)
                )

                invalid_email_records = df[
                    invalid_email_mask
                ]

            else:

                email_values = pd.Series("", index=df.index)
                invalid_email_mask = pd.Series(
                    False, index=df.index
                )
                invalid_email_records = df.iloc[0:0]

            # Age validation
            if "age" in df.columns:

                age_values = pd.to_numeric(
                    df["age"],
                    errors="coerce"
                )

                invalid_age_mask = (
                    age_values.notna()
                    & (age_values < 0)
                )

                invalid_age_records = df[
                    invalid_age_mask
                ]

            else:

                age_values = pd.Series(
                    float("nan"), index=df.index
                )
                invalid_age_mask = pd.Series(
                    False, index=df.index
                )
                invalid_age_records = df.iloc[0:0]

            col1, col2 = st.columns(2)

            col1.metric(
                "Invalid Emails",
                int(invalid_email_mask.sum())
            )

            col2.metric(
                "Invalid Ages",
                int(invalid_age_mask.sum())
            )

            st.write("### Invalid Email Records")

            if not invalid_email_records.empty:

                st.warning("Invalid email addresses detected!")

                st.dataframe(invalid_email_records)

            else:
                st.success("No invalid email addresses found.")

            st.write("### Invalid Age Records")

            if not invalid_age_records.empty:

                st.warning("Invalid ages detected!")

                st.dataframe(invalid_age_records)

            else:
                st.success("No invalid ages found.")

            # ==========================================
            # 8. DATA QUALITY SCORE
            # ==========================================

            st.subheader("Data Quality Score")

            # Completeness: 30%
            total_cells = total_rows * total_columns

            if total_cells > 0:

                completeness_score = (
                    (total_cells - missing_values)
                    / total_cells
                ) * 30

            else:
                completeness_score = 0

            # Uniqueness: 25%
            if total_rows > 0:

                uniqueness_score = (
                    (total_rows - duplicate_rows)
                    / total_rows
                ) * 25

            else:
                uniqueness_score = 0

            # Validity: 25%
            total_checked_values = (
                email_values.ne("").sum()
                + age_values.notna().sum()
            )

            total_invalid_values = (
                invalid_email_mask.sum()
                + invalid_age_mask.sum()
            )

            if total_checked_values > 0:

                validity_score = (
                    (total_checked_values - total_invalid_values)
                    / total_checked_values
                ) * 25

            else:
                validity_score = 0

            # Consistency: 20%
            text_columns = df.select_dtypes(
                include=["object", "string"]
            )

            total_text_values = (
                text_columns.notna().sum().sum()
            )

            inconsistent_values = 0

            for column in text_columns.columns:

                values = (
                    text_columns[column]
                    .dropna()
                    .astype(str)
                )

                inconsistent_values += (
                    values != values.str.strip()
                ).sum()

            if total_text_values > 0:

                consistency_score = (
                    (total_text_values - inconsistent_values)
                    / total_text_values
                ) * 20

            else:
                consistency_score = 20

            quality_score = round(
                completeness_score
                + uniqueness_score
                + validity_score
                + consistency_score,
                2
            )

            st.metric(
                "Overall Data Quality Score",
                f"{quality_score}/100"
            )

            # Quality breakdown
            score_report = pd.DataFrame({
                "Category": [
                    "Completeness",
                    "Uniqueness",
                    "Validity",
                    "Consistency"
                ],
                "Score": [
                    round(completeness_score, 2),
                    round(uniqueness_score, 2),
                    round(validity_score, 2),
                    round(consistency_score, 2)
                ],
                "Maximum Score": [30, 25, 25, 20]
            })

            st.write("### Quality Breakdown")

            st.dataframe(
                score_report,
                use_container_width=True
            )

            # ==========================================
            # 9. QUALITY STATUS
            # ==========================================

            st.write("### Overall Quality Status")

            if quality_score >= 90:

                quality_status = "Excellent"
                st.success("Excellent Data Quality!")

            elif quality_score >= 75:

                quality_status = "Good"
                st.info("Good Data Quality")

            elif quality_score >= 60:

                quality_status = "Average"
                st.warning("Average Data Quality")

            else:

                quality_status = "Poor"
                st.error("Poor Data Quality")

            # ==========================================
            # 10. QUALITY SCORE CHART
            # ==========================================

            st.write("### Quality Score Visualization")

            fig1, ax1 = plt.subplots(figsize=(5, 5))

            ax1.pie(
                [
                    quality_score,
                    100 - quality_score
                ],
                labels=[
                    "Quality Score",
                    "Remaining"
                ],
                startangle=90,
                autopct="%1.1f%%",
                colors=["#2ECC71", "#E5E7EB"],
                wedgeprops={"width": 0.35}
            )

            ax1.set_title("Data Quality Score")

            st.pyplot(fig1)
            plt.close(fig1)

            # ==========================================
            # 11. QUALITY CATEGORY BAR CHART
            # ==========================================

            st.write("### Quality Category Analysis")

            fig2, ax2 = plt.subplots(figsize=(9, 5))

            ax2.bar(
                score_report["Category"],
                score_report["Score"],
                color=[
                    "#3498DB",
                    "#9B59B6",
                    "#2ECC71",
                    "#F39C12"
                ]
            )

            ax2.set_ylim(0, 35)
            ax2.set_ylabel("Score")
            ax2.set_title("Data Quality Breakdown")

            for index, score in enumerate(
                score_report["Score"]
            ):

                ax2.text(
                    index,
                    score + 0.5,
                    str(score),
                    ha="center"
                )

            plt.xticks(rotation=15)
            plt.tight_layout()

            st.pyplot(fig2)
            plt.close(fig2)

            # ==========================================
            # 12. DATA CLEANING
            # ==========================================

            st.subheader("Data Cleaning")

            st.write(
                "Choose the cleaning operations you want to perform."
            )

            remove_duplicates = st.checkbox(
                "Remove duplicate records",
                value=True
            )

            fill_missing = st.checkbox(
                "Fill missing and invalid values",
                value=True
            )

            # Create separate copy
            cleaned_df = df.copy()

            # Remove duplicate records
            if remove_duplicates:

                cleaned_df = cleaned_df.drop_duplicates(
                    subset=duplicate_check_columns
                )

            # Fill missing and invalid values
            if fill_missing:

                if "age" in cleaned_df.columns:

                    cleaned_df["age"] = pd.to_numeric(
                        cleaned_df["age"],
                        errors="coerce"
                    )

                    cleaned_df.loc[
                        cleaned_df["age"] < 0,
                        "age"
                    ] = float("nan")

                for column in cleaned_df.columns:

                    if cleaned_df[column].isnull().any():

                        if pd.api.types.is_numeric_dtype(
                            cleaned_df[column]
                        ):

                            average_value = (
                                cleaned_df[column].mean()
                            )

                            if pd.notna(average_value):

                                cleaned_df[column] = (
                                    cleaned_df[column].fillna(
                                        average_value
                                    )
                                )

                        else:

                            cleaned_df[column] = (
                                cleaned_df[column].fillna(
                                    "Unknown"
                                )
                            )

            # ==========================================
            # 13. CLEANING RESULTS
            # ==========================================

            st.subheader("Cleaning Results")

            col1, col2 = st.columns(2)

            col1.metric(
                "Original Rows",
                len(df)
            )

            col2.metric(
                "Cleaned Rows",
                len(cleaned_df)
            )

            st.write("### Cleaned Dataset Preview")

            st.dataframe(
                cleaned_df,
                use_container_width=True
            )

            # ==========================================
            # 14. DOWNLOAD CLEANED DATASET
            # ==========================================

            st.subheader("Download Cleaned Dataset")

            csv_data = cleaned_df.to_csv(
                index=False
            ).encode("utf-8")

            excel_buffer = BytesIO()

            with pd.ExcelWriter(
                excel_buffer,
                engine="openpyxl"
            ) as writer:

                cleaned_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Cleaned Data"
                )

            col1, col2 = st.columns(2)

            with col1:

                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="cleaned_dataset.csv",
                    mime="text/csv"
                )

            with col2:

                st.download_button(
                    label="Download Excel",
                    data=excel_buffer.getvalue(),
                    file_name="cleaned_dataset.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            # ==========================================
            # 15. PDF DATA QUALITY REPORT
            # ==========================================

            st.subheader("Download Data Quality Report")

            pdf_buffer = BytesIO()

            document = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4
            )

            styles = getSampleStyleSheet()

            report_content = []

            report_content.append(
                Paragraph(
                    "DataSentry - Data Quality Report",
                    styles["Title"]
                )
            )

            report_content.append(
                Spacer(1, 20)
            )

            # Dataset overview
            report_content.append(
                Paragraph(
                    "Dataset Overview",
                    styles["Heading2"]
                )
            )

            overview_data = [
                ["Metric", "Value"],
                ["Dataset Name", uploaded_file.name],
                ["Original Rows", str(total_rows)],
                ["Total Columns", str(total_columns)],
                ["Missing Values", str(int(missing_values))],
                ["Duplicate Records", str(int(duplicate_rows))],
                ["Invalid Emails", str(int(invalid_email_mask.sum()))],
                ["Invalid Ages", str(int(invalid_age_mask.sum()))],
                ["Quality Score", f"{quality_score}/100"],
                ["Quality Status", quality_status]
            ]

            overview_table = Table(
                overview_data
            )

            overview_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.darkblue
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    )
                ])
            )

            report_content.append(
                overview_table
            )

            report_content.append(
                Spacer(1, 20)
            )

            # Quality breakdown
            report_content.append(
                Paragraph(
                    "Quality Breakdown",
                    styles["Heading2"]
                )
            )

            quality_data = [
                ["Category", "Score", "Maximum"],
                [
                    "Completeness",
                    str(round(completeness_score, 2)),
                    "30"
                ],
                [
                    "Uniqueness",
                    str(round(uniqueness_score, 2)),
                    "25"
                ],
                [
                    "Validity",
                    str(round(validity_score, 2)),
                    "25"
                ],
                [
                    "Consistency",
                    str(round(consistency_score, 2)),
                    "20"
                ]
            ]

            quality_table = Table(
                quality_data
            )

            quality_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.darkblue
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    )
                ])
            )

            report_content.append(
                quality_table
            )

            report_content.append(
                Spacer(1, 20)
            )

            # Cleaning summary
            report_content.append(
                Paragraph(
                    "Cleaning Summary",
                    styles["Heading2"]
                )
            )

            cleaning_data = [
                ["Metric", "Value"],
                ["Original Rows", str(len(df))],
                ["Cleaned Rows", str(len(cleaned_df))],
                [
                    "Rows Removed",
                    str(len(df) - len(cleaned_df))
                ]
            ]

            cleaning_table = Table(
                cleaning_data
            )

            cleaning_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.darkgreen
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    )
                ])
            )

            report_content.append(
                cleaning_table
            )

            # Generate PDF
            document.build(
                report_content
            )

            pdf_buffer.seek(0)

            st.download_button(
                label="Download PDF Quality Report",
                data=pdf_buffer.getvalue(),
                file_name="DataSentry_Quality_Report.pdf",
                mime="application/pdf"
            )

    except Exception as error:

        st.error(
            f"Unable to process the file: {error}"
        )

else:

    st.info(
        "Please upload a CSV or Excel file to begin."
    )
