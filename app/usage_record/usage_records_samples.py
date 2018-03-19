full_record_sample = {
  "by_project": {
    "buckets": [
      {
        "key": "1",
        "by_type": {
          "buckets": [
            {
              "key": "Running VM",
              "by_offering": {
                "buckets": [
                  {
                    "key": "100|offering_name_100|4|4096",
                    "rawusage_sum": {
                      "value": 72
                    }
                  },
                  {
                    "key": "200|offering_name_200|1|1024",
                    "rawusage_sum": {
                      "value": 48
                    }
                  }
                ]
              }
            }
          ]
        }
      }
    ]
  }
}

records_with_overlapping_running_and_allocated = {
  "by_project": {
    "buckets": [
      {
        "key": "1",
        "by_type": {
          "buckets": [
            {
              "key": "Allocated VM",
              "by_offering": {
                "buckets": [
                  {
                    "key": "100|offering_name_100|4|4096",
                    "rawusage_sum": {
                      "value": 72
                    }
                  }
                ]
              }
            },
            {
              "key": "Running VM",
              "by_offering": {
                "buckets": [
                  {
                    "key": "100|offering_name_100|4|4096",
                    "rawusage_sum": {
                      "value": 48
                    }
                  }
                ]
              }
            }
          ]
        }
      }
    ]
  }
}

record_with_running_time_equals_allocated_time = {
  "by_project": {
    "buckets": [
      {
        "key": "1",
        "by_type": {
          "buckets": [
            {
              "key": "Allocated VM",
              "by_offering": {
                "buckets": [
                  {
                    "key": "100|offering_name_100|4|4096",
                    "rawusage_sum": {
                      "value": 48
                    }
                  }
                ]
              }
            },
            {
              "key": "Running VM",
              "by_offering": {
                "buckets": [
                  {
                    "key": "100|offering_name_100|4|4096",
                    "rawusage_sum": {
                      "value": 48
                    }
                  }
                ]
              }
            }
          ]
        }
      }
    ]
  }
}