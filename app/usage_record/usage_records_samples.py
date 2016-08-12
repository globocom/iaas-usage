full_record_sample = {
  "by_project": {
    "buckets": [
      {
        "key": "1",
        "by_type": {
          "buckets": [
            {
              "key": "Volume",
              "by_offering": {
                "buckets": [
                  {
                    "key": "1",
                    "rawusage_sum": {
                      "value": 24
                    }
                  },
                  {
                    "key": "2",
                    "rawusage_sum": {
                      "value": 24
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
                    "key": "100",
                    "rawusage_sum": {
                      "value": 72
                    }
                  },
                  {
                    "key": "200",
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

record_sample_with_low_usage = {
  "by_project": {
    "buckets": [
      {
        "key": "1",
        "by_type": {
          "buckets": [
            {
              "key": "Volume",
              "by_offering": {
                "buckets": [
                  {
                    "key": "1",
                    "rawusage_sum": {
                      "value": 0.9
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
                    "key": "100",
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
                    "key": "100",
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
                    "key": "100",
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
                    "key": "100",
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