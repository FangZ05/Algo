import pandas as pd
import time
file_path = 'AMD_daily.csv'

start_time = time.time()

for i in range(10):
    df = pd.read_csv(file_path, nrows=5)



print("--- %s seconds ---" % (time.time() - start_time))
