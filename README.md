# NPK Fertilizer Match

The tool identifies the most suitable fertilizer by matching products based on their NPK (nitrogen, phosphorus, potassium) values for optimal plant nutrition.

This version of NPK-match has been made compatible with the KLMS Tool Template and can be incorporated withing workflows. The tool is invoked in the form of a Task within a workflow Process via the respective API call. 

## Tool Invocation Example

An example spec for executing an autonomous instance of NPK-match through the API would be:

```json
{
    "process_id": "f9645b89-34e4-4de2-8ecd-dc10163d9aed",
    "name": "NPK Fertilizer Match",
    "image": "petroud/npk-fertilizer-match:latest",
    "inputs": {
        "npk_values": [
            "325fb7c7-b269-4a1e-96f6-a861eb2fe325"
        ],
        "fertilizer_dataset":[
            "41da3a81-3768-47db-b7ac-121c92ec3f6d"
        ]
    },
    "datasets": {
        "d0": "2f8a651b-a40b-4edd-b82d-e9ea3aba4d13"
    },
    "parameters": {},
    "outputs": {
        "matched_fertilizers": {
            "url": "s3://abaco-bucket/MATCH/matched_fertilizers.csv",
            "dataset": "d0",
            "resource": {
                "name": "Matched Fertilizers based on NPK values",
                "relation": "matched"
            }
        }
    }
}
```

## Tool Input JSON
At runtime the tool expects the following, translated by the API, JSON: 
```json

{
        "input": {
            "fertilizer_dataset": [
                "s3://abaco-bucket/MATCH/Dataset_Banca_Dati_Fertilizzanti.csv"
            ],
            "npk_values": [
                "s3://abaco-bucket/MATCH/user_NPK_values.csv"
            ]
        },
        "minio": {
            "endpoint_url": "https://minio.stelar.gr",
            "id": "XXXXXXXXXXX",
            "key": "XXXXXXXXXXX",
            "skey": "XXXXXXXXXXX"
        },
        "output": {
            "matched_fertilizers": "s3://abaco-bucket/MATCH/matched_fertilizers.csv"
        },
        "parameters": {}
    }
```
### `input`
The tool expect two inputs during runtime that are being utilized in conjuction during the calculation:
- `fertilizer_dataset` (CSV): User-supplied nutrient targets for individual fields, crops, or recommendation scenarios.	
- `npk_values` (CSV): Master list of fertilizers with guaranteed nutrient analyses.	



### `output`
Upon the input files provided the tool concludes to a file representing the most suitable Fertilizers per NPK triplet. The result is in CSV form and stored 
in the path defined by the `matched_fertilizers` output key. 

## Tool Output JSON

```json
{
    "message": "Tool executed successfully!",
    "output": {
        "matched_fertilizers": "s3://abaco-bucket/MATCH/matched_fertilizers.csv"
    },
    "metrics": {
        "records_in": 10,
        "records_out": 10
    },
    "status": "success"
}
```


## How to build 
Alter the `IMGTAG` in Makefile with a repository from your Image Registry and hit 
`make` in your terminal within the same directory.