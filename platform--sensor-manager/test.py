from datetime import datetime, timezone

dtformat = datetime.strptime ("2023-01-16T14:45:26+05:30", "%Y-%m-%dT%H:%M:%S%z")
secs = (dtformat - datetime(1970, 1, 1, tzinfo = timezone.utc)).total_seconds()
print (int (secs))
