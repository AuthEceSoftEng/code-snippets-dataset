import os
import pandas as pd
from properties import resultsPath
from utils.code_complexity import cyclomatic_complexity, number_of_names

if __name__ == '__main__':
    df = pd.concat([pd.read_csv(os.path.join(resultsPath, f)) for f in os.listdir(resultsPath) if f.endswith('.csv')], ignore_index=True)
    print(len(df.index))

    list_1_0_10 = []
    list_1_10_20 = []
    list_1_20_30 = []
    list_1_30_ = []
    list_2_0_10 = []
    list_2_10_20 = []
    list_2_20_30 = []
    list_2_30_ = []
    list_3_0_10 = []
    list_3_10_20 = []
    list_3_20_30 = []
    list_3_30_ = []
    list_4_0_10 = []
    list_4_10_20 = []
    list_4_20_30 = []
    list_4_30_40 = []
    list_4_40_50 = []
    list_4_50_ = []
    df["cc"] = 0
    for i, code in enumerate(df["code"]):
        cc = cyclomatic_complexity(code)
        nn = number_of_names(df.loc[i, "ast_code"])
        if (nn == -1): continue
        df.loc[i, "cc"] = cc
        if (cc == 1):
            if (nn < 10):
                list_1_0_10.append(i)
            elif (nn < 20):
                list_1_10_20.append(i)
            elif (nn < 30):
                list_1_20_30.append(i)
            else:
                list_1_30_.append(i)
        elif (cc == 2):
            if (nn < 10):
                list_2_0_10.append(i)
            elif (nn < 20):
                list_2_10_20.append(i)
            elif (nn < 30):
                list_2_20_30.append(i)
            else:
                list_2_30_.append(i)
        elif (cc == 3):
            if (nn < 10):
                list_3_0_10.append(i)
            elif (nn < 20):
                list_3_10_20.append(i)
            elif (nn < 30):
                list_3_20_30.append(i)
            else:
                list_3_30_.append(i)
        else:
            if (nn < 10):
                list_4_0_10.append(i)
            elif (nn < 20):
                list_4_10_20.append(i)
            elif (nn < 30):
                list_4_20_30.append(i)
            elif (nn < 40):
                list_4_30_40.append(i)
            elif (nn < 50):
                list_4_40_50.append(i)
            else:
                list_4_50_.append(i)

    df.loc[list_1_0_10, :].to_csv(os.path.join(resultsPath, "df_1_0_10.csv"))
    df.loc[list_1_10_20, :].to_csv(os.path.join(resultsPath, "df_1_10_20.csv"))
    df.loc[list_1_20_30, :].to_csv(os.path.join(resultsPath, "df_1_20_30.csv"))
    df.loc[list_1_30_, :].to_csv(os.path.join(resultsPath, "df_1_30_.csv"))

    df.loc[list_2_0_10, :].to_csv(os.path.join(resultsPath, "df_2_0_10.csv"))
    df.loc[list_2_10_20, :].to_csv(os.path.join(resultsPath, "df_2_10_20.csv"))
    df.loc[list_2_20_30, :].to_csv(os.path.join(resultsPath, "df_2_20_30.csv"))
    df.loc[list_2_30_, :].to_csv(os.path.join(resultsPath, "df_2_30_.csv"))

    df.loc[list_3_0_10, :].to_csv(os.path.join(resultsPath, "df_3_0_10.csv"))
    df.loc[list_3_10_20, :].to_csv(os.path.join(resultsPath, "df_3_10_20.csv"))
    df.loc[list_3_20_30, :].to_csv(os.path.join(resultsPath, "df_3_20_30.csv"))
    df.loc[list_3_30_, :].to_csv(os.path.join(resultsPath, "df_3_30_.csv"))

    df.loc[list_4_0_10, :].to_csv(os.path.join(resultsPath, "df_4_0_10.csv"))
    df.loc[list_4_10_20, :].to_csv(os.path.join(resultsPath, "df_4_10_20.csv"))
    df.loc[list_4_20_30, :].to_csv(os.path.join(resultsPath, "df_4_20_30.csv"))
    df.loc[list_4_30_40, :].to_csv(os.path.join(resultsPath, "df_4_30_40.csv"))
    df.loc[list_4_40_50, :].to_csv(os.path.join(resultsPath, "df_4_40_50.csv"))
    df.loc[list_4_50_, :].to_csv(os.path.join(resultsPath, "df_4_50_.csv"))