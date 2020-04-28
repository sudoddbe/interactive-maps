import pandas as pd
import geopandas as gpd
import numpy as np
from datetime import date


def date_conversion(date_str):
    subsections = date_str.split("/")
    return str(date(int("20" + subsections[2]), int(subsections[0]), int(subsections[1])))

def read_and_sum_US_data(US_datafile):
    df = pd.read_csv(US_datafile)
    drop_columns = ["UID", "iso2", "iso3", "code3", "FIPS", "Admin2", "Province_State", "Lat", "Long_", "Combined_Key", "Population"]
    df = df.drop(columns = drop_columns)
    df = df.melt(id_vars=["Country_Region"], var_name="Date", value_name="Deaths")
    df = df.groupby(["Country_Region", "Date"]).sum().reset_index()
    df.replace(to_replace="US", value="United States of America", inplace=True)
    df.rename(columns={"Country_Region": "Country/Region"}, inplace=True)
    df['Date'] = df['Date'].apply(lambda x: date_conversion(x))
    return df


def read_time_series_global(datafile):
    df = pd.read_csv(datafile)
    #Drop lat and long since we are shamelessly using country names instead
    df = df.drop(columns = ["Lat", "Long"])
    #Reformat data so that we now have a Date and death column
    df = df.melt(id_vars=["Province/State", "Country/Region"], var_name="Date", value_name="Deaths")

    #Manual fixup of country names, should really use country codes...
    df.replace(to_replace="Korea, South", value="South Korea", inplace=True)
    df.replace(to_replace="North Macedonia", value="Macedonia", inplace=True)
    df.replace(to_replace="Serbia", value="Republic of Serbia", inplace=True)

    #Fix dates to be strings we eurpoean ordering
    df['Date'] = df['Date'].apply(lambda x: date_conversion(x))

    #For sum over the Province/State variable to get country level data
    df = df.groupby(["Country/Region", "Date"]).sum().reset_index()
    return df

def merge_geo_and_data(gdf, df):
    merged = gdf.merge(df, left_on = 'country', right_on = 'Country/Region', how="left")
    merged = merged[["country", "country_code", "geometry", "Date", "Deaths"]]

    all_dates = merged["Date"].unique()
    all_dates = [str(d) for d in all_dates if str(d) != "nan"]
    idx = pd.MultiIndex.from_product([merged["country"].unique(), all_dates], names=["country", "Date"])
    tmp = gpd.GeoDataFrame(index=idx, columns=["geometry", "Deaths"])
    all_dates = tmp.index.get_level_values(1).unique()
    for ind, grdf in merged.groupby(["country"]):
        deaths = grdf["Deaths"]
        dates = grdf["Date"]
        geos = grdf["geometry"]
        index = [(ind, d) for d in all_dates]
        val = [geos.values[0] for d in all_dates]
        gs = gpd.GeoSeries(val, index = index)
        tmp.loc[index, "geometry"] = gs

        test = np.any([str(d) == "nan" for d in dates.values])
        if not test:
             index = [(ind, d) for d in dates.values if str(d) != "nan"]
             tmp.loc[index, "Deaths"] = deaths.values

    merged = tmp
    merged = merged.reset_index()
    merged.fillna({"Deaths" : np.nan}, inplace=True)
    return merged

def read_all_data( shapefile="countries_110m/ne_110m_admin_0_countries.shp", datafile = "COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv", US_datafile = "COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"):

    gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
    gdf.columns = ['country', 'country_code', 'geometry']
    gdf.drop(gdf[gdf["country"]  == "Antarctica"].index, inplace=True)
    df = read_time_series_global(datafile)
    us_df = read_and_sum_US_data(US_datafile)
    df = df.append(us_df)
    merged = merge_geo_and_data(gdf, df)
    return merged

if __name__=="__main__":
    read_all_data()
