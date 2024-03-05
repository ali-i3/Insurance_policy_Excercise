import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read in the JSON data
df = pd.read_json('insurance-policies.json')

def merge_incorrect_columns(df: pd.DataFrame, incorrect_column: str, target_column: str) -> pd.DataFrame:
    """_summary_

    Args:
        df (pd.DataFrame): Full Dataframe
        incorrect_column (str): Column to be removed post merger
        target_column (str): Column to be updated with missing values

    Returns:
        pd.DataFrame: Full Dataframe after column correction
    """
    df[target_column] = df[target_column].fillna(df[incorrect_column])
    df = df.drop(incorrect_column, axis=1)

    return df

def convert_datetime(df: pd.DataFrame, target_column: str, format:str = 'datetime64[ns]'):
    """Convert column datatypes into Python Datetime format

    Args:
        df (pd.DataFrame): Full Dataframe
        target_column (str): Columns to updated to Datetime format
        format (str, optional): Optional format parameter. Defaults to 'datetime64[ns]'.

    Returns:
        _type_: Full Dataframe after formatting
    """
    df[target_column] = pd.to_datetime(df[target_column])
    return df


# Clean up Dataframe
incorrect_columns_list = ['sum_insureed', 'sale_dates', 'first name']
target_columns_list = ['sum_insured', 'sale_date', 'first_name']

for i,j in zip(incorrect_columns_list,target_columns_list):
    df = merge_incorrect_columns(df, i, j)

# Convert Datetime columns
date_columns_list = ['sale_date', 'cancel_date', 'start_date']

for i in date_columns_list:
    df = convert_datetime(df, i)



# Q1: Number of sales for each month
# Add Month/Year column to dataframe for sale date to avoid multi-indexing
df['sale_month'] = df['sale_date'].dt.strftime('%Y-%m')
monthly_sales = df['sale_date'].groupby(df['sale_month']).agg('count')


# Q2: Cancellation counts per month
df['cancel_month'] = df['cancel_date'].dt.strftime('%Y-%m')
cancellations_df = df[~df['cancel_date'].isnull()]
monthly_cancels = cancellations_df['cancel_date'].groupby(cancellations_df['cancel_month']).agg('count')


# Q3: Policies starting that month
df['start_month'] = df['start_date'].dt.strftime('%Y-%m')
monthly_policy_numbers = df['policy_number'].groupby(df['start_month']).agg(list)
monthy_policy_count = df['policy_number'].groupby(df['start_month']).agg('count')


# Q4: Month on month growth rate
monthly_sales_pct = monthly_sales.pct_change()


# Q5: Total premiums collected for policies starting that month
monthly_premiums = df['premium'].groupby(df['start_month']).agg('sum')


# Q6: Monthly IPT contributions
df['ipt_value']  =  (df['ipt_percent']/100) * df['premium']
monthly_ipt_contribution =  df['ipt_value'].groupby(df['start_month']).agg('sum')


# Q7: Monthly SERL commision
df['ipt_value']= df['ipt_value'].fillna(0)
df['serl_value']  = (df['premium'] - df['ipt_value']) * (df['commission_SERL_percent']/100)
monthly_serl_commission =  df['serl_value'].groupby(df['start_month']).agg('sum')


# Q7: # Top SERL product per month
monthly_product_serl = df.groupby(['start_month', 'product_name'], as_index=False)['serl_value'].sum()
monthly_product_serl.set_index("start_month", inplace=True)


# Visualisations
plt.figure(1)
plt.subplot(2,2,1)
monthly_sales.plot(kind='bar', title="Monthly Policy Sales", ylabel="Number of Sold Policies", xlabel="Month", ax=plt.gca())
plt.subplot(2,2,2)
monthly_cancels.plot(kind='bar', title="Monthly Cancellations", ylabel="Number of Cancellations", xlabel="Month", ax=plt.gca())
plt.subplot(2,2,3)
plot3 = monthly_sales_pct.plot(color='r', ax=plt.gca(), title="Monthly Sales Growth Rate")
yabs_max = abs(max(plot3.get_ylim(), key=abs))
plot3.set_ylim(ymin=-yabs_max, ymax=yabs_max)
plt.axhline(y=0, color='b', linestyle='-')
plt.subplot(2,2,4)
monthly_premiums.plot(kind='bar', title="Monthly Premiums Collected", ylabel="Total Monthly Premiums", xlabel="Month", color='r', ax=plt.gca())
plt.tight_layout()

plt.figure(2)
plt.subplot(2,2,1)
monthly_ipt_contribution.plot(kind='bar', title="Monthly IPT Contribution", ylabel="Total IPT", xlabel="Month", color='r', ax=plt.gca())
plt.subplot(2,2,2)
monthly_serl_commission.plot(kind='bar', title="Monthly SERL Commission", ylabel="Total SERL", xlabel="Month", color='b', ax=plt.gca())
plt.subplot(2, 1, 2)
monthly_product_serl.groupby("product_name")["serl_value"].plot(legend=True, title="Top Monthly SERL Product", xlabel="Month/Year", ylabel="SERL_Commision Totals", ax=plt.gca())
plt.tight_layout()
plt.show()