import csv
import commons.utils as utils
import commons.preprocessing as preproc

import pandas as pd
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import os
import recordlinkage
from recordlinkage.index import Block


main_directory = utils.get_absolute_path("../")
sources_directory = main_directory + "../sources/"
mediated_schema = pd.DataFrame({})

# PROJ_ID = 'steam-habitat-431613-r1'

# vertexai.init(project=PROJ_ID, location="europe-west9")

# model = GenerativeModel(
#                         model_name="gemini-1.5-pro-001",
#                         generation_config = GenerationConfig(temperature = 0, top_p = 0)
#                         )

for filename in (os.listdir(sources_directory)):
    print('Processing: ' + filename)
    filename = sources_directory + filename
    data = pd.read_csv(filename)

    first_five = data.head(5)

    prompt = """
        Imagine you are a seasoned data engineer, I'm going to give you some tabular data in .csv format and you have 
        to take each column of the table and map to one of my mediated schema.
        The columns of my mediated schema are:
        ""
        name, category, market_cap, country, city, founding_year, number_of_employees, website, ceo 
        ""
        The data is:
        ""
        """ + \
        str(first_five.to_csv(index=False)) + \
        """
        ""
        Generate a reply following this format:
        ""
        {
        <name_of_the_column_to_be_mapped> : <name_of_the_column_in_the_mediated_schema>
        }
        ""
        Do not include in the json response the <name_of_the_column_to_be_mapped> if you can't find any correspondence. 
        Please adhere strictly to these instructions to provide a structured and accurate response.
    """

    #response = model.generate_content([prompt])

    #data = data.rename(columns=response)
    data = preproc.pre_process_dataframe(data)
    mediated_schema = pd.concat([mediated_schema, data])

print(mediated_schema.describe().to_json())
print(mediated_schema.isnull().sum())

mediated_schema = mediated_schema.sort_values(by='name')
mediated_schema.to_csv(main_directory + '/mediated_schema.csv', index=False)

