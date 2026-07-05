from cloud.bigquery import load_patients

df = load_patients()

print(df.head())

print(df.shape)