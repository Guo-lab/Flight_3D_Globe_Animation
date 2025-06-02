# Flight_3D_Globe_Animation


To implement a 3D globe animation with flight paths, with the similar functionality as `Mult.dev` or `Footprint`.

```bash

.
├── constants.py
├── demo.mp4
├── flight.py
├── flights.json
├── frame_data_export.json
├── globe.py
├── output.log
├── README.md
├── smooth_flight_animation.html
├── test_traces.py
└── utils.py
```


Unfortunately, there is still a bug that the second flight path is not displayed correctly. According to the output log, the frame data is correct. However, after the first flight path is shown, the second one does not appear as expected.

Work in progress, but the basic functionality is there. The code uses `Plotly` for 3D plotting and 3D projections.

- Usage:
    
```bash 
python flight.py
```

- Test:

```bash 
python test_traces.py
```



https://github.com/user-attachments/assets/6e51ab37-03de-433e-bd6f-857cd5091b87

