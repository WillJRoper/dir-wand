# Data Processing Examples

Examples of using WAND for batch data processing, ETL pipelines, and data analysis workflows.

## Batch CSV Processing

Process multiple CSV files in parallel.

### Setup

```bash
mkdir "batch_{id}"

cat > "batch_{id}/process.py" << 'EOF'
#!/usr/bin/env python3
import pandas as pd
import sys

batch_id = "{id}"

# Read input
df = pd.read_csv(f"input_{batch_id}.csv")

# Process data
df_processed = df.copy()
df_processed["value"] = df_processed["value"] * 2
df_processed["batch_id"] = batch_id

# Write output
df_processed.to_csv(f"output_{batch_id}.csv", index=False)

print(f"Batch {batch_id}: Processed {len(df)} rows")
EOF

chmod +x "batch_{id}/process.py"

# Create sample input files
for i in {0..9}; do
    echo "value" > "batch_{id}/input_{id}.csv"
    for j in {1..100}; do
        echo "$j" >> "batch_{id}/input_{id}.csv"
    done
done
```

### Execution

```bash
dir-wand --template "batch_{id}" --id 0-9 \
  --run "cd batch_{id} && python3 process.py"
```

## ETL Pipeline

Extract, transform, and load data from multiple sources.

### Setup

```bash
mkdir "etl_{source}_{date}"

cat > "etl_{source}_{date}/config.yaml" << 'EOF'
etl:
  source: {source}
  date: {date}

extract:
  connection_string: "postgresql://db.example.com/{source}"
  query: "SELECT * FROM data WHERE date = '{date}'"

transform:
  operations:
    - remove_nulls
    - normalize_values
    - add_derived_columns

load:
  destination: "s3://data-lake/processed/{source}/{date}/"
  format: "parquet"
EOF

cat > "etl_{source}_{date}/run_etl.py" << 'EOF'
#!/usr/bin/env python3
import yaml
import pandas as pd
from sqlalchemy import create_engine

with open("config.yaml") as f:
    config = yaml.safe_load(f)

# Extract
print(f"Extracting data from {config['etl']['source']}...")
engine = create_engine(config["extract"]["connection_string"])
df = pd.read_sql(config["extract"]["query"], engine)

# Transform
print(f"Transforming {len(df)} rows...")
df = df.dropna()  # remove_nulls
df["normalized"] = (df["value"] - df["value"].mean()) / df["value"].std()
df["processed_date"] = config["etl"]["date"]

# Load
print(f"Loading to {config['load']['destination']}...")
df.to_parquet(config["load"]["destination"] + "data.parquet")

print("ETL complete")
EOF

chmod +x "etl_{source}_{date}/run_etl.py"
```

### Execution

```bash
# Process data from multiple sources for multiple dates
dir-wand --template "etl_{source}_{date}" \
  -source customers orders products inventory \
  -date 2024-01-01 2024-01-02 2024-01-03 2024-01-04 \
  --run "cd etl_{source}_{date} && python3 run_etl.py"
```

## Log File Analysis

Analyze log files from multiple servers.

### Setup

```bash
mkdir "logs_{server}_{date}"

cat > "logs_{server}_{date}/analyze.py" << 'EOF'
#!/usr/bin/env python3
import re
import json
from collections import Counter

server = "{server}"
date = "{date}"

# Read log file
log_file = f"/var/logs/{server}/{date}.log"

error_pattern = r"ERROR: (.*?)$"
warning_pattern = r"WARNING: (.*?)$"

errors = []
warnings = []

with open(log_file, "r") as f:
    for line in f:
        if "ERROR" in line:
            match = re.search(error_pattern, line)
            if match:
                errors.append(match.group(1))
        elif "WARNING" in line:
            match = re.search(warning_pattern, line)
            if match:
                warnings.append(match.group(1))

# Summarize
error_counts = Counter(errors)
warning_counts = Counter(warnings)

summary = {
    "server": server,
    "date": date,
    "total_errors": len(errors),
    "total_warnings": len(warnings),
    "top_errors": error_counts.most_common(10),
    "top_warnings": warning_counts.most_common(10)
}

# Save summary
with open(f"summary_{server}_{date}.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"{server} {date}: {len(errors)} errors, {len(warnings)} warnings")
EOF

chmod +x "logs_{server}_{date}/analyze.py"
```

### Execution

```bash
# Analyze logs for last 7 days across all servers
dir-wand --template "logs_{server}_{date}" \
  -server web1 web2 web3 api1 api2 db1 db2 \
  -date 2024-01-01 2024-01-02 2024-01-03 2024-01-04 2024-01-05 2024-01-06 2024-01-07 \
  --run "cd logs_{server}_{date} && python3 analyze.py"
```

## Image Processing Pipeline

Process images with different filters and sizes.

### Setup

```bash
mkdir "images_{filter}_{size}"

cat > "images_{filter}_{size}/process.sh" << 'EOF'
#!/bin/bash
filter="{filter}"
size="{size}"

input_dir="/data/images/input"
output_dir="output_${filter}_${size}"

mkdir -p "$output_dir"

for img in $input_dir/*.jpg; do
    filename=$(basename "$img")

    # Apply filter and resize
    convert "$img" \
        -filter "$filter" \
        -resize "${size}x${size}" \
        "$output_dir/$filename"
done

echo "Processed $(ls $input_dir/*.jpg | wc -l) images with $filter filter at ${size}x${size}"
EOF

chmod +x "images_{filter}_{size}/process.sh"
```

### Execution

```bash
# Create all combinations of filters and sizes
dir-wand --swapfile image_processing.yaml \
  -filter Lanczos Mitchell Cubic \
  -size 256 512 1024

# Run processing
dir-wand --template "images_{filter}_{size}" \
  --swapfile image_processing.yaml \
  --run "cd images_{filter}_{size} && ./process.sh"
```

## Database Backup and Export

Export database tables in multiple formats.

### Setup

```bash
mkdir "export_{table}_{format}"

cat > "export_{table}_{format}/export.sh" << 'EOF'
#!/bin/bash
table="{table}"
format="{format}"
date=$(date +%Y%m%d)

output_file="${table}_${date}.${format}"

case $format in
    csv)
        psql -d mydb -c "COPY $table TO STDOUT WITH CSV HEADER" > "$output_file"
        ;;
    json)
        psql -d mydb -t -c "SELECT json_agg(t) FROM $table t" > "$output_file"
        ;;
    parquet)
        python3 << PYTHON
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://localhost/mydb")
df = pd.read_sql_table("$table", engine)
df.to_parquet("$output_file")
PYTHON
        ;;
esac

echo "Exported $table to $output_file"
EOF

chmod +x "export_{table}_{format}/export.sh"
```

### Execution

```bash
dir-wand --template "export_{table}_{format}" \
  -table users orders products reviews \
  -format csv json parquet parquet \
  --run "cd export_{table}_{format} && ./export.sh"
```

## See Also

- [Scientific Computing](scientific.md)
- [Testing Examples](testing.md)
- [Basic Examples](basic.md)
