from typing import Optional, TypedDict
import pulumi
import pulumi_gcp as gcp

class BigQueryLoaderArgs(TypedDict):
    file_location_uri: Optional[pulumi.Output[str]]
    schema: Optional[pulumi.Output[str]]

class BigQueryLoader(pulumi.ComponentResource):
    dataset_id: pulumi.Output[str]
    table_id: pulumi.Output[str]
    job_id: pulumi.Output[str]

    def __init__(self, name:str, args:BigQueryLoaderArgs, opts:Optional[pulumi.ResourceOptions]=None):
        super().__init__('gcp-data:index:BigQueryLoader', name, {}, opts)

        # Create a BigQuery dataset
        bigquery_dataset = gcp.bigquery.Dataset(
            f"{name}-dataset",
            dataset_id=f"{name}_dataset",
            location="US",
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Create a BigQuery table within the dataset
        bigquery_table = gcp.bigquery.Table(
            f"{name}-table",
            dataset_id=bigquery_dataset.dataset_id,
            table_id=f"{name}_table",
            schema=args.get("schema") or "[]",
            opts=pulumi.ResourceOptions(parent=bigquery_dataset)
        )

        # Load data from the GCS bucket into the BigQuery table
        bq_load_job = gcp.bigquery.Job(
            f"{name}-table-load-job",
            location="US",
            job_id=f"{name}_load_job",
            load=gcp.bigquery.JobLoadArgs(
                source_uris=[args.get("file_location_uri")],
                destination_table=gcp.bigquery.JobLoadDestinationTableArgs(
                    project_id=gcp.config.project,
                    dataset_id=bigquery_dataset.dataset_id,
                    table_id=bigquery_table.table_id,
                ),
                source_format="CSV",
                write_disposition="WRITE_TRUNCATE",
                autodetect=True,
            ),
            opts=pulumi.ResourceOptions(parent=bigquery_table)
        )

        self.dataset_id = bigquery_dataset.dataset_id
        self.table_id = bigquery_table.table_id
        self.job_id = bq_load_job.job_id

        self.register_outputs({
            'dataset_id': self.dataset_id,
            'table_id': self.table_id,
            'job_id': self.job_id,
        })