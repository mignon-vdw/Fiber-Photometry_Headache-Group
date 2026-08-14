#Recording processing

import pandas as pd

df = pd.read_csv("photometry_export.csv") #change file name or automate it

#Generate time points for a sampling rate of 130Hz

sampling_rate = 130

df["time_s"] = (
    df.index / sampling_rate
)

#Create a GCaMP output with timestamps

gcamp_df = pd.DataFrame({
    "time_s": df["time_s"],
    "gcamp": df["analog_1"]
})

gcamp_df.to_csv(
    "gcamp_signal.csv",
    index=False
)

#Create tdTomato output with timestamps

tdtomato_df = pd.DataFrame({
    "time_s": df["time_s"],
    "tdtomato": df["analog_2"]
})

gcamp_df.to_csv(
    "tdtomato_signal.csv",
    index=False
)

#Detect digital events from Digital output 2

digital2_events = df.index[
    (df["digital_2"].shift(1) == 0)
    &
    (df["digital_2"] == 1)
]

digital2_times = (
    digital2_events /
    sampling_rate
)

#Create event file

events = []

for t in digital2_events:

    events.append({
        "event_type": "digital_2",
        "time_s": t
    })

    events_df = pd.DataFrame(events)

    events_df.to_csv(
        "events.csv",
        index=False
    )