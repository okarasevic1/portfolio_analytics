import duckdb 

class LoadStoreData:

    # folder's path of data
    f_path = '/Users/okarasevic1/Documents/PortfolioAnalyzer/database/file_data/'


    def load_csv(self, file_path:str, name:str): 

        new_name = f'{self.f_path}{name}.parquet'

        with duckdb.connect(':memory:') as con:

            con = duckdb.connect(':memory:')
            con.read_csv(file_path).to_parquet(new_name)
            con.close()

        return new_name