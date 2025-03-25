## Evaluation Data and Script for NTIRE 2025 Text to Image Generation Model Quality Assessment -Track2- Structure Distortion Detection

### File Directory
```
.
├── evaluate.py          # Evaluation script
├── ref
│   └── gt.pkl        # Ground truth file
├── res
│   ├── output.pkl      # Model output file
│   └── readme.txt       # Description file for the model output
└── output
    └── scores.txt       # Evaluation results
```

### Data Preparation
- The development phase annotation data ```gt.pkl``` can be found at [link](https://drive.google.com/file/d/1_0z_MKIYvPcuM0ciZdzji-hTzdSqmWSI/view?usp=sharing). Please download it and place it in the ```./ref```.
- Prepare your model output ```output.okl``` and a README file ```readme.txt```, then place them in the ```./res```.

### Evaluation
To run the evaluation script, execute the following command:
``` 
python3 evaluate.py ./ ./output
```
The script will generate the evaluation results and save them in the ```./output```.

