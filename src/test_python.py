from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.getOrCreate()

df = spark.read.csv("/mnt/trusted/clientes.csv", header=True, inferSchema=True)

=df2 = df.withColumn("idade_int", F.col("idade").cast("int"))
df2.write.mode("overwrite").parquet("/mnt/refined/clientes")

import os
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

DB_PASSWORD = "SuperSecreto123"   # ERRADO

df = spark.read.format("jdbc").option("url", "jdbc:postgresql://host:5432/db") \
    .option("dbtable", "public.usuarios") \
    .option("user", "app") \
    .option("password", DB_PASSWORD) \
    .load()


df.write.mode("overwrite").parquet("/mnt/refined/usuarios") 



from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

dados = spark.read.parquet("/dbfs/mnt/producao/catalogo_x/tabela_y/")  # ERRADO: não parametrizado

dados.write.mode("append").saveAsTable("producao.tabela_y_refined")  # referência direta a catálogos



from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

df = spark.read.json("/mnt/trusted/pedidos/2024-12-01.json")

df.filter("status == 'APROVADO'").write.mode("overwrite").parquet("/mnt/refined/pedidos-aprovados")




from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.getOrCreate()

bronze = spark.read.parquet("/mnt/bronze/events")
refined = bronze.groupBy("user_id").agg(F.count("*").alias("total"))

refined.write.mode("overwrite").parquet("/mnt/refined/events_por_usuario")


from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
df = spark.range(0, 10).toDF("c")

df.write.mode("overwrite").saveAsTable("tmp_xpto_123")  # sem comentários/descrição, sem tags

from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

run = w.jobs.submit(run_name="rodar_notebook",
                    existing_cluster_id="fixed-cluster-id",
                    notebook_task={"notebook_path": "/Repos/user/projeto/notebooks/processa_dados"})
print(run) 



from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

df = spark.read.parquet("/mnt/trusted/clientes")
df.write.mode("overwrite").parquet("/mnt/refined/clientes_refined")  # fluxo não conforme
